# Copyright 2016-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
import os
import reframe as rfm
import reframe.utility.sanity as sn


@rfm.required_version('>=2.16.0-dev.0')
@rfm.simple_test
class HaloCellExchangeTest(rfm.RegressionTest):
    def __init__(self):
        self.sourcepath = 'halo_cell_exchange.c'
        self.build_system = 'SingleSource'
        self.build_system.cflags = ['-O2']
        self.valid_systems = ['ubelix:gpu', 'ubelix:mc']
        self.valid_prog_environs = ['foss', 'intel']

        self.num_tasks = 6
        self.num_tasks_per_node = 1
        self.num_gpus_per_node = 0

        self.executable_opts = ['input.txt']

        self.sanity_patterns = sn.assert_eq(
            sn.count(sn.findall(r'halo_cell_exchange', self.stdout)), 9)

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

        self.reference = {
            'ubelix:gpu': {
                'time_2_10': (7.193528e-06, None, 0.50, 's'),
                'time_2_10000': (2.739924e-05, None, 0.50, 's'),
                'time_2_1000000': (1.737886e-03, None, 0.50, 's'),
                'time_4_10': (7.193735e-06, None, 0.50, 's'),
                'time_4_10000': (2.861973e-05, None, 0.50, 's'),
                'time_4_1000000': (1.948640e-03, None, 0.50, 's'),
                'time_6_10': (8.107336e-06, None, 0.50, 's'),
                'time_6_10000': (3.022024e-05, None, 0.50, 's'),
                'time_6_1000000': (2.046319e-03, None, 0.50, 's')
            },
            'ubelix:mc': {
                'time_2_10': (8.116711e-06, None, 0.50, 's'),
                'time_2_10000': (2.894489e-05, None, 0.50, 's'),
                'time_2_1000000': (1.734432e-03, None, 0.50, 's'),
                'time_4_10': (8.636488e-06, None, 0.50, 's'),
                'time_4_10000': (3.127021e-05, None, 0.50, 's'),
                'time_4_1000000': (1.968542e-03, None, 0.50, 's'),
                'time_6_10': (8.552056e-06, None, 0.50, 's'),
                'time_6_10000': (3.505448e-05, None, 0.50, 's'),
                'time_6_1000000': (2.081705e-03, None, 0.50, 's')
            },
        }

        self.maintainers = ['Mandes']
        self.tags = {'benchmark'}
