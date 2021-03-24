from datetime import datetime
import os
import reframe as rfm
import reframe.utility.sanity as sn


class HelloWorldBaseTest(rfm.RegressionTest):
    def __init__(self, variant, lang):
        self.prgenv_flags = {}
        self.lang_names = {
            'c': 'C',
            'cpp': 'C++',
            'f90': 'Fortran 90'
        }
        self.descr = self.lang_names[lang] + ' Hello World'
        self.sourcepath = 'hello_world'
        self.build_system = 'SingleSource'
        self.valid_systems = ['ubelix:mc', 'ubelix:gpu', 'ubelix:amd']

        self.valid_prog_environs = ['foss', 'intel']

        self.compilation_time_seconds = None

        result = sn.findall(r'Hello World from thread \s*(\d+) out '
                            r'of \s*(\d+) from process \s*(\d+) out of '
                            r'\s*(\d+)', self.stdout)

        num_tasks = sn.getattr(self, 'num_tasks')
        num_cpus_per_task = sn.getattr(self, 'num_cpus_per_task')

        def tid(match):
            return int(match.group(1))

        def num_threads(match):
            return int(match.group(2))

        def rank(match):
            return int(match.group(3))

        def num_ranks(match):
            return int(match.group(4))

        self.sanity_patterns = sn.all(
            sn.chain(
                [sn.assert_eq(sn.count(result), num_tasks*num_cpus_per_task)],
                sn.map(lambda x: sn.assert_lt(tid(x), num_threads(x)), result),
                sn.map(lambda x: sn.assert_lt(rank(x), num_ranks(x)), result),
                sn.map(
                    lambda x: sn.assert_lt(tid(x), num_cpus_per_task), result
                ),
                sn.map(
                    lambda x: sn.assert_eq(num_threads(x), num_cpus_per_task),
                    result
                ),
                sn.map(lambda x: sn.assert_lt(rank(x), num_tasks), result),
                sn.map(
                    lambda x: sn.assert_eq(num_ranks(x), num_tasks), result
                ),
            )
        )
        self.perf_patterns = {
            'compilation_time': sn.getattr(self, 'compilation_time_seconds')
        }
        self.reference = {
            '*': {
                'compilation_time': (60, None, 0.1, 's')
            }
        }

        self.maintainers = ['VH', 'EK']
        self.tags = {'production', 'prgenv'}

    @rfm.run_before('compile')
    def setflags(self):
        envname = self.current_environ.name.replace('-nompi', '')
        prgenv_flags = self.prgenv_flags[envname]
        self.build_system.cflags = prgenv_flags
        self.build_system.cxxflags = prgenv_flags
        self.build_system.fflags = prgenv_flags

    @rfm.run_before('compile')
    def compile_timer_start(self):
        self.compilation_time_seconds = datetime.now()

    @rfm.run_after('compile')
    def compile_timer_end(self):
        elapsed = datetime.now() - self.compilation_time_seconds
        self.compilation_time_seconds = elapsed.total_seconds()

@rfm.parameterized_test(*([lang]
                          for lang in ['cpp', 'c', 'f90']))
class HelloWorldTestSerial(HelloWorldBaseTest):
    def __init__(self, lang):
        super().__init__('serial', lang)
        self.sourcesdir = 'src/serial'
        self.sourcepath += '_serial.' + lang
        self.descr += ' Serial '
        self.prgenv_flags = {
            'foss': [],
            'intel': [],
        }
        self.num_tasks = 1
        self.num_tasks_per_node = 1
        self.num_cpus_per_task = 1

@rfm.parameterized_test(*([lang]
                          for lang in ['cpp', 'c', 'f90']))
class HelloWorldTestOpenMP(HelloWorldBaseTest):
    def __init__(self, lang):
        super().__init__('openmp', lang)
        self.sourcesdir = 'src/openmp'
        self.sourcepath += '_openmp.' + lang
        self.descr += ' OpenMP '
        self.prgenv_flags = {
            'foss': ['-fopenmp'],
            'intel': ['-qopenmp'],
        }

        self.num_tasks = 1
        self.num_tasks_per_node = 1
        self.num_cpus_per_task = 4

        # On SLURM there is no need to set OMP_NUM_THREADS if one defines
        # num_cpus_per_task, but adding for completeness and portability
        self.variables = {
            'OMP_NUM_THREADS': str(self.num_cpus_per_task)
        }


@rfm.parameterized_test(*([lang]
                          for lang in ['cpp', 'c', 'f90']))
class HelloWorldTestMPI(HelloWorldBaseTest):
    def __init__(self, lang):
        super().__init__('mpi', lang)
        self.sourcesdir = 'src/mpi'
        self.sourcepath += '_mpi.' + lang
        self.descr += ' MPI '
        self.prgenv_flags = {
            'foss': [],
            'intel': [],
        }

        # for the MPI test the self.num_tasks_per_node should always be one. If
        # not, the test will fail for the total number of lines in the output
        # file is different then self.num_tasks * self.num_tasks_per_node
        self.num_tasks = 2
        self.num_tasks_per_node = 1
        self.num_cpus_per_task = 1


@rfm.parameterized_test(*([lang,si]
                          for lang in ['cpp', 'c', 'f90']
                          for si in ['small', 'normal']))
class HelloWorldTestMPIOpenMP(HelloWorldBaseTest):
    def __init__(self, lang, si):
        super().__init__('mpi_openmp', lang)
        self.sourcesdir = 'src/mpi_openmp'
        self.sourcepath += '_mpi_openmp.' + lang
        self.descr += ' MPI + OpenMP '
        self.prgenv_flags = {
            'foss': ['-fopenmp'],
            'intel': ['-qopenmp'],
        }

        if (si is 'small'):
            self.valid_systems = ['ubelix:gpu']
            self.num_tasks = 2
            self.num_tasks_per_node = 1
            self.num_cpus_per_task = 2
        else:
            self.valid_systems = ['ubelix:mc', 'ubelix:amd']
            self.num_tasks = 3
            self.num_tasks_per_node = 3
            self.num_cpus_per_task = 2

        # On SLURM there is no need to set OMP_NUM_THREADS if one defines
        # num_cpus_per_task, but adding for completeness and portability
        self.variables = {
            'OMP_NUM_THREADS': str(self.num_cpus_per_task)
        }
