# Copyright 2016-2021 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.parameterized_test(['nompi'], ['mpi'])
class FFTWTest(rfm.RegressionTest):
    def __init__(self, exec_mode):
        self.sourcepath = 'fftw_benchmark.c'
        self.build_system = 'SingleSource'
        self.valid_systems = ['ubelix:bdw', 'ubelix:epyc2']

        self.valid_prog_environs = ['foss']
        self.num_tasks_per_node = 12
        self.num_gpus_per_node = 0
        self.sanity_patterns = sn.assert_eq(
            sn.count(sn.findall(r'execution time', self.stdout)), 1)
        self.build_system.cflags = ['-O2 -lfftw3']
        self.perf_patterns = {
            'fftw_exec_time': sn.extractsingle(
                r'execution time:\s+(?P<exec_time>\S+)', self.stdout,
                'exec_time', float),
        }

        if exec_mode == 'nompi':
            self.num_tasks = 12
            self.executable_opts = ['72 12 1000 0']
            self.reference = {
                '*': {
                    'fftw_exec_time': (30, None, 0.05, 's'),
                },
            }
        else:
            self.num_tasks = 20
            self.executable_opts = ['144 20 200 1']
            self.reference = {
                '*': {
                    'fftw_exec_time': (20, None, 0.50, 's'),
                },
            }

        self.maintainers = ['Man']
        self.tags = {'benchmark'}
