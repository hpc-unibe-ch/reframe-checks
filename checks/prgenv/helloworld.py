from datetime import datetime
import os
import reframe as rfm
import reframe.utility.sanity as sn


class HelloWorldBaseTest(rfm.RegressionTest):
    lang = parameter(['c', 'cpp', 'f90'])
    prgenv_flags = {}
    sourcepath = 'hello_world'
    build_system = 'SingleSource'
    prebuild_cmds = ['_rfm_build_time="$(date +%s%N)"']
    postbuild_cmds = [
        '_rfm_build_time="$(($(date +%s%N)-_rfm_build_time))"',
        'echo "Compilations time (ns): $_rfm_build_time"'
    ]
    valid_systems = ['ubelix:epyc2', 'ubelix:bdw', 'ubelix:gpu']
    valid_prog_environs = ['foss', 'intel']

    reference = {
        '*': {
            'compilation_time': (60, None, 0.1, 's')
        }
    }

    maintainers = ['Mandes']
    tags = {'production', 'prgenv'}

    @run_after('init')
    def set_description(self):
        self.lang_names = {
            'c': 'C',
            'cpp': 'C++',
            'f90': 'Fortran 90'
        }
        self.descr = self.lang_names[self.lang] + ' Hello World'

    @sanity_function
    def assert_hello_world(self):
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

        return sn.all(sn.chain(
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

    @run_before('compile')
    def setflags(self):
        envname = self.current_environ.name
        try:
            prgenv_flags = self.prgenv_flags[envname]
        except KeyError:
            prgenv_flags = []

        self.build_system.cflags = prgenv_flags
        self.build_system.cxxflags = prgenv_flags
        self.build_system.fflags = prgenv_flags

    @performance_function('s')
    def compilation_time(self):
        return sn.extractsingle(r'Compilations time \(ns\): (\d+)',
                                self.build_stdout, 1, float) * 1.0e-9

@rfm.simple_test
class HelloWorldTestSerial(HelloWorldBaseTest):
    sourcesdir = 'src/serial'
    num_tasks = 1
    num_tasks_per_node = 1
    num_cpus_per_task = 1
    @run_after('init')
    def update_description(self):
        self.descr += ' Serial '
    @run_before('compile')
    def update_sourcepath(self):
        self.sourcepath += f'_serial.{self.lang}'

@rfm.simple_test
class HelloWorldTestOpenMP(HelloWorldBaseTest):
    sourcesdir = 'src/openmp'
    num_tasks = 1
    num_tasks_per_node = 1
    num_cpus_per_task = 4

    @run_after('init')
    def set_prgenv_compilation_flags_map(self):
        self.prgenv_flags = {
            'foss': ['-fopenmp'],
            'intel': ['-qopenmp'],
        }

    @run_after('init')
    def update_description(self):
        self.descr += ' OpenMP '

    @run_before('compile')
    def update_sourcepath(self):
        self.sourcepath += '_openmp.' + self.lang

    @run_before('run')
    def set_omp_env_variable(self):
        # On SLURM there is no need to set OMP_NUM_THREADS if one defines
        # num_cpus_per_task, but adding for completeness and portability
        self.variables['OMP_NUM_THREADS'] = str(self.num_cpus_per_task)

@rfm.simple_test
class HelloWorldTestMPI(HelloWorldBaseTest):
    sourcesdir = 'src/mpi'
    # for the MPI test the self.num_tasks_per_node should always be one. If
    # not, the test will fail for the total number of lines in the output
    # file is different then self.num_tasks * self.num_tasks_per_node
    num_tasks = 2
    num_tasks_per_node = 1
    num_cpus_per_task = 1

    @run_after('init')
    def update_description(self):
        self.descr += ' MPI '

    @run_before('compile')
    def update_sourcepath(self):
        self.sourcepath += '_mpi.' + self.lang

@rfm.simple_test
class HelloWorldTestMPIOpenMP(HelloWorldBaseTest):
    sourcesdir = 'src/mpi_openmp'

    @run_after('init')
    def set_prgenv_compilation_flags_map(self):
        self.prgenv_flags = {
            'foss': ['-fopenmp'],
            'intel': ['-qopenmp'],
        }

    @run_after('init')
    def update_description(self):
        self.descr += ' MPI + OpenMP '

    @run_before('compile')
    def update_sourcepath(self):
        self.sourcepath += '_mpi_openmp.' + self.lang

    @run_before('run')
    def set_job_size(self):
        if self.current_partition.name == 'gpu':
            self.num_tasks = 2
            self.num_tasks_per_node = 1
            self.num_cpus_per_task = 1

        elif self.current_partition.name == 'epyc2':
            self.num_tasks = 3
            self.num_tasks_per_node = 3
            self.num_cpus_per_task = 2

        elif self.current_partition.name == 'bdw':
            self.num_tasks = 5
            self.num_tasks_per_node = 5
            self.num_cpus_per_task = 4

    @run_before('run')
    def set_omp_env_variable(self):
        # On SLURM there is no need to set OMP_NUM_THREADS if one defines
        # num_cpus_per_task, but adding for completeness and portability
        self.variables['OMP_NUM_THREADS'] = str(self.num_cpus_per_task)
