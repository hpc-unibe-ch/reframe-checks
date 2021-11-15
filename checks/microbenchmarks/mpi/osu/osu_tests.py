# Copyright 2016-2021 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.parameterized_test(['production'])
class AlltoallTest(rfm.RegressionTest):
    def __init__(self, variant):
        self.strict_check = False
        self.valid_systems = ['ubelix:bdw', 'ubelix:epyc2']
        self.descr = 'Alltoall OSU microbenchmark'
        self.build_system = 'Make'
        self.build_system.makefile = 'Makefile_alltoall'
        self.executable = './osu_alltoall'
        # The -m option sets the maximum message size
        # The -x option sets the number of warm-up iterations
        # The -i option sets the number of iterations
        self.executable_opts = ['-m', '8', '-x', '1000', '-i', '20000']
        self.valid_prog_environs = ['foss', 'intel']
        self.maintainers = ['Man']
        self.sanity_patterns = sn.assert_found(r'^8', self.stdout)
        self.perf_patterns = {
            'latency': sn.extractsingle(r'^8\s+(?P<latency>\S+)',
                                        self.stdout, 'latency', float)
        }
        self.tags = {variant, 'benchmark'}
        self.reference = {
                'ubelix:bdw': {'latency': (20.73, None, 2.0, 'us') },
                'ubelix:epyc2': {'latency': (20.73, None, 2.0, 'us') },
        }
        self.num_tasks_per_node = 1
        self.num_gpus_per_node  = 0
        self.num_tasks = 4
        self.extra_resources = {
            'switches': {
                'num_switches': 1
            }
        }


#@rfm.simple_test
#class FlexAlltoallTest(rfm.RegressionTest):
#    def __init__(self):
#        self.valid_systems = ['ubelix:bdw']#, 'ubelix:epyc2'] # max 4 nodes on epyc2
#        self.valid_prog_environs = ['foss']
#
#        self.descr = 'Flexible Alltoall OSU test'
#        self.build_system = 'Make'
#        self.build_system.makefile = 'Makefile_alltoall'
#        self.executable = './osu_alltoall'
#        self.num_tasks_per_node = 1
#        self.num_tasks = -5
#        self.sanity_patterns = sn.assert_found(r'^1048576', self.stdout)
#        self.tags = {'diagnostic', 'benchmark'}
#        self.maintainers = ['Man']


@rfm.parameterized_test(['small'])#, ['large'])
class AllreduceTest(rfm.RegressionTest):
    def __init__(self, variant):
        self.strict_check = False
        self.valid_systems = ['ubelix:bdw']
        if variant == 'small':
            self.valid_systems += ['ubelix:epyc2'] # thight limits on GPU and arm partition

        self.descr = 'Allreduce OSU microbenchmark'
        self.build_system = 'Make'
        self.build_system.makefile = 'Makefile_allreduce'
        self.executable = './osu_allreduce'
        # The -x option controls the number of warm-up iterations
        # The -i option controls the number of iterations
        self.executable_opts = ['-m', '8', '-x', '1000', '-i', '20000']
        self.valid_prog_environs = ['foss']
        self.sanity_patterns = sn.assert_found(r'^8', self.stdout)
        self.perf_patterns = {
            'latency': sn.extractsingle(r'^8\s+(?P<latency>\S+)',
                                        self.stdout, 'latency', float)
        }
        self.num_gpus_per_node  = 0
        self.num_tasks_per_node = 1
        if variant == 'small':
            self.tags = {'production'}
            self.num_tasks = 3
            self.reference = {
                'ubelix:gpu': { 'latency': (8, None, 0.05, 'us') },
                'ubelix:bdw': { 'latency': (8, None, 0.05, 'us') },
                'ubelix:epyc2': { 'latency': (8, None, 0.05, 'us') },
            }
        else:
            self.tags = {'benchmark'}
            self.num_tasks = 16
            self.reference = {
                'ubelix:bdw': { 'latency': (8, None, 0.05, 'us') },
                'ubelix:epyc2': { 'latency': (8, None, 0.05, 'us') },
            }

        self.extra_resources = {
            'switches': {
                'num_switches': 1
            }
        }
        self.maintainers = ['Man']

    @rfm.run_before('run')
    def set_tasks(self):
        if self.current_partition.fullname in ['ubelix:gpu']:
            self.num_gpus_per_node  = 1

class P2PBaseTest(rfm.RegressionTest):
    def __init__(self):
        self.exclusive_access = True
        self.strict_check = False
        self.num_tasks = 2
        self.num_tasks_per_node = 1
        self.descr = 'P2P microbenchmark'
        self.build_system = 'Make'
        self.build_system.makefile = 'Makefile_p2p'
        self.valid_prog_environs = ['foss', 'intel']
        self.tags = {'production', 'benchmark'}
        self.sanity_patterns = sn.assert_found(r'^4194304', self.stdout)

        self.extra_resources = {
            'switches': {
                'num_switches': 1
            }
        }
        self.maintainers = ['Man']


@rfm.simple_test
class P2PCPUBandwidthTest(P2PBaseTest):
    def __init__(self):
        super().__init__()
        self.valid_systems = ['ubelix:bdw', 'ubelix:epyc2']
        self.executable = './p2p_osu_bw'
        self.executable_opts = ['-x', '100', '-i', '1000']
        self.reference = {
                'ubelix:bdw': {'bw': (9607.0, -0.10, None, 'MB/s')},
                'ubelix:epyc2': {'bw': (9607.0, -0.10, None, 'MB/s')},
        }
        self.perf_patterns = {
            'bw': sn.extractsingle(r'^4194304\s+(?P<bw>\S+)',
                                   self.stdout, 'bw', float)
        }


@rfm.simple_test
class P2PCPULatencyTest(P2PBaseTest):
    def __init__(self):
        super().__init__()
        self.valid_systems = ['ubelix:bdw', 'ubelix:epyc2']
        self.executable_opts = ['-x', '100', '-i', '1000']

        self.executable = './p2p_osu_latency'
        self.reference = {
            'ubelix:bdw': {'latency': (1.30, None, 0.70, 'us')},
            'ubelix:epyc2': {'latency': (1.30, None, 0.70, 'us')},
        }
        self.perf_patterns = {
            'latency': sn.extractsingle(r'^8\s+(?P<latency>\S+)',
                                        self.stdout, 'latency', float)
        }


#@rfm.simple_test
#class G2GBandwidthTest(P2PBaseTest):
#    def __init__(self):
#        super().__init__()
#        self.valid_systems = ['ubelix:gpu']
#        self.num_gpus_per_node = 1
#        self.executable = './p2p_osu_bw'
#        self.executable_opts = ['-x', '100', '-i', '1000', '-d',
#                                'cuda', 'D', 'D']
#
#        self.reference = {
#            'ubelix:gpu': {
#                'bw': (8813.09, -0.05, None, 'MB/s')
#            },
#            '*': {
#                'bw': (0, None, None, 'MB/s')
#            }
#        }
#        self.perf_patterns = {
#            'bw': sn.extractsingle(r'^4194304\s+(?P<bw>\S+)',
#                                   self.stdout, 'bw', float)
#        }
#        self.modules = ['CUDA']
#        self.build_system.ldflags = ['-L$EBROOTCUDA/lib64',
#                                     '-lcudart', '-lcuda']
#
#        self.build_system.cppflags = ['-D_ENABLE_CUDA_']
#
#
#@rfm.simple_test
#class G2GLatencyTest(P2PBaseTest):
#    def __init__(self):
#        super().__init__()
#        self.valid_systems = ['ubelix:gpu']
#        self.num_gpus_per_node = 1
#        self.executable = './p2p_osu_latency'
#        self.executable_opts = ['-x', '100', '-i', '1000', '-d',
#                                'cuda', 'D', 'D']
#
#        self.reference = {
#            'ubelix:gpu': {
#                'latency': (5.56, None, 0.1, 'us')
#            },
#        }
#        self.perf_patterns = {
#            'latency': sn.extractsingle(r'^8\s+(?P<latency>\S+)',
#                                        self.stdout, 'latency', float)
#        }
#        self.modules = ['CUDA']
#        self.build_system.ldflags = ['-L$EBROOTCUDA/lib64',
#                                     '-lcudart', '-lcuda']
#
#        self.build_system.cppflags = ['-D_ENABLE_CUDA_']
