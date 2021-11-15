# Copyright 2016-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
import os
import reframe as rfm
import reframe.utility.sanity as sn


@rfm.required_version('>=2.16.0-dev.0')
@rfm.parameterized_test(*([a]
                            for a in ['ivy', 'bdw', 'epyc2']))
class HaloCellExchangeTest(rfm.RegressionTest):
    def __init__(self, arch):
        self.curr_arch = arch
        self.sourcepath = 'halo_cell_exchange.c'
        self.build_system = 'SingleSource'
        self.build_system.cflags = ['-O2']
        self.valid_prog_environs = ['foss', 'intel']
        self.executable_opts = ['input.txt']
        self.valid_systems = [ ]

        if self.curr_arch in ['epyc2']:
           self.valid_systems = [ 'ubelix:epyc2' ]
           self.num_tasks = 4
           self.num_tasks_per_node = 1
           self.num_gpus_per_node = 0
           self.perf_patterns = {
            'time_2_10': sn.extractsingle(
                r'halo_cell_exchange 4 2 1 1 10 10 10'
                r' \S+ (?P<time_mpi>\S+)', self.stdout,
                'time_mpi', float),
            'time_2_10000': sn.extractsingle(
                r'halo_cell_exchange 4 2 1 1 10000 10000 10000'
                r' \S+ (?P<time_mpi>\S+)', self.stdout,
                'time_mpi', float),
            'time_2_1000000': sn.extractsingle(
                r'halo_cell_exchange 4 2 1 1 1000000 1000000 1000000'
                r' \S+ (?P<time_mpi>\S+)', self.stdout,
                'time_mpi', float),
            'time_4_10': sn.extractsingle(
                r'halo_cell_exchange 4 2 2 1 10 10 10'
                r' \S+ (?P<time_mpi>\S+)', self.stdout,
                'time_mpi', float),
            'time_4_10000': sn.extractsingle(
                r'halo_cell_exchange 4 2 2 1 10000 10000 10000'
                r' \S+ (?P<time_mpi>\S+)', self.stdout,
                'time_mpi', float),
            'time_4_1000000': sn.extractsingle(
                r'halo_cell_exchange 4 2 2 1 1000000 1000000 1000000'
                r' \S+ (?P<time_mpi>\S+)', self.stdout,
                'time_mpi', float),
           }

           self.sanity_patterns = sn.assert_eq(
                sn.count(sn.findall(r'halo_cell_exchange', self.stdout)), 6)
        elif self.curr_arch in ['ivy ', 'bdw']:
            self.valid_systems = [ 'ubelix:ivy', 'ubelix:bdw' ]
            self.num_tasks = 6
            self.num_tasks_per_node = 1
            self.num_gpus_per_node = 0
            self.perf_patterns = {
                'time_2_10': sn.extractsingle(
                    r'halo_cell_exchange 6 2 1 1 10 10 10'
                    r' \S+ (?P<time_mpi>\S+)', self.stdout,
                    'time_mpi', float),
                'time_2_10000': sn.extractsingle(
                    r'halo_cell_exchange 6 2 1 1 10000 10000 10000'
                    r' \S+ (?P<time_mpi>\S+)', self.stdout,
                    'time_mpi', float),
                'time_2_1000000': sn.extractsingle(
                    r'halo_cell_exchange 6 2 1 1 1000000 1000000 1000000'
                    r' \S+ (?P<time_mpi>\S+)', self.stdout,
                    'time_mpi', float),
                'time_4_10': sn.extractsingle(
                    r'halo_cell_exchange 6 2 2 1 10 10 10'
                    r' \S+ (?P<time_mpi>\S+)', self.stdout,
                    'time_mpi', float),
                'time_4_10000': sn.extractsingle(
                    r'halo_cell_exchange 6 2 2 1 10000 10000 10000'
                    r' \S+ (?P<time_mpi>\S+)', self.stdout,
                    'time_mpi', float),
                'time_4_1000000': sn.extractsingle(
                    r'halo_cell_exchange 6 2 2 1 1000000 1000000 1000000'
                    r' \S+ (?P<time_mpi>\S+)', self.stdout,
                    'time_mpi', float),
                'time_6_10': sn.extractsingle(
                    r'halo_cell_exchange 6 3 2 1 10 10 10'
                    r' \S+ (?P<time_mpi>\S+)', self.stdout,
                    'time_mpi', float),
                'time_6_10000': sn.extractsingle(
                    r'halo_cell_exchange 6 3 2 1 10000 10000 10000'
                    r' \S+ (?P<time_mpi>\S+)', self.stdout,
                    'time_mpi', float),
                'time_6_1000000': sn.extractsingle(
                    r'halo_cell_exchange 6 3 2 1 1000000 1000000 1000000'
                    r' \S+ (?P<time_mpi>\S+)', self.stdout,
                    'time_mpi', float)
            }
            self.sanity_patterns = sn.assert_eq(
                sn.count(sn.findall(r'halo_cell_exchange', self.stdout)), 9)

        self.reference = {
            'ubelix:ivy': {
                'time_2_10': (1, None, 0.50, 's'),
                'time_2_10000': (1, None, 0.50, 's'),
                'time_2_1000000': (1, None, 0.50, 's'),
                'time_4_10': (1, None, 0.50, 's'),
                'time_4_10000': (1, None, 0.50, 's'),
                'time_4_1000000': (1, None, 0.50, 's'),
                'time_6_10': (1, None, 0.50, 's'),
                'time_6_10000': (1, None, 0.50, 's'),
                'time_6_1000000': (1, None, 0.50, 's')
            },
           'ubelix:bdw': {
                'time_2_10': (1, None, 0.50, 's'),
                'time_2_10000': (1, None, 0.50, 's'),
                'time_2_1000000': (1, None, 0.50, 's'),
                'time_4_10': (1, None, 0.50, 's'),
                'time_4_10000': (1, None, 0.50, 's'),
                'time_4_1000000': (1, None, 0.50, 's'),
                'time_6_10': (1, None, 0.50, 's'),
                'time_6_10000': (1, None, 0.50, 's'),
                'time_6_1000000': (1, None, 0.50, 's')
            },
            'ubelix:epyc2': {
                'time_2_10': (2e-04, None, 0.50, 's'),
                'time_2_10000': (1e-03, None, 0.50, 's'),
                'time_2_1000000': (5e-03, None, 0.50, 's'),
                'time_4_10': (9e-04, None, 0.50, 's'),
                'time_4_10000': (1e-03, None, 0.50, 's'),
                'time_4_1000000': (1e-01, None, 0.50, 's'),
                #'time_6_10': (1e-04, None, 0.50, 's'),
                #'time_6_10000': (1e-03, None, 0.50, 's'),
                #'time_6_1000000': (1e-02, None, 0.50, 's')
            },
        }

        self.maintainers = ['Mandes']
        self.tags = {'benchmark'}
