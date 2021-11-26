# Copyright 2016-2021 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn


class NumpyBaseTest(rfm.RunOnlyRegressionTest):
    def __init__(self):
        self.descr = 'Test a few typical numpy operations'
        self.valid_prog_environs = ['foss']
        self.modules = ['SciPy-bundle']
        self.reference = {
            'ubelix:gpu': {
                'dot': (2, None, 0.05, 'seconds'),
                'svd': (3, None, 0.05, 'seconds'),
                'cholesky': (0.2, None, 0.05, 'seconds'),
                'eigendec': (12, None, 0.05, 'seconds'),
                'inv': (0.5, None, 0.05, 'seconds'),
            },
            'ubelix:bdw': {
                'dot': (0.45, None, 0.05, 'seconds'),
                'svd': (15, None, 0.05, 'seconds'),
                'cholesky': (0.5, None, 0.05, 'seconds'),
                'eigendec': (30, None, 0.05, 'seconds'),
                'inv': (0.3, None, 0.05, 'seconds'),
            },
            'ubelix:epyc2': {
                'dot': (0.7, None, 0.05, 'seconds'),
                'svd': (150, None, 0.05, 'seconds'),
                'cholesky': (1.7, None, 0.05, 'seconds'),
                'eigendec': (260, None, 0.05, 'seconds'),
                'inv': (1.5, None, 0.05, 'seconds'),
            },
        }
        self.perf_patterns = {
            'dot': sn.extractsingle(
                r'^Dotted two 4096x4096 matrices in\s+(?P<dot>\S+)\s+s',
                self.stdout, 'dot', float),
            'svd': sn.extractsingle(
                r'^SVD of a 2048x1024 matrix in\s+(?P<svd>\S+)\s+s',
                self.stdout, 'svd', float),
            'cholesky': sn.extractsingle(
                r'^Cholesky decomposition of a 2048x2048 matrix in'
                r'\s+(?P<cholesky>\S+)\s+s',
                self.stdout, 'cholesky', float),
            'eigendec': sn.extractsingle(
                r'^Eigendecomposition of a 2048x2048 matrix in'
                r'\s+(?P<eigendec>\S+)\s+s',
                self.stdout, 'eigendec', float),
            'inv': sn.extractsingle(
                r'^Inversion of a 2048x2048 matrix in\s+(?P<inv>\S+)\s+s',
                self.stdout, 'inv', float)
        }
        self.sanity_patterns = sn.assert_found(r'Numpy version:\s+\S+',
                                               self.stdout)
        self.variables = {
            'OMP_NUM_THREADS': '$SLURM_CPUS_PER_TASK',
        }
        self.executable = 'python'
        self.executable_opts = ['np_ops.py']
        self.num_tasks_per_node = 1
        self.use_multithreading = False
        self.tags = {'production'}
        self.maintainers = ['Mandes']


@rfm.simple_test
class NumpyEpyc2Test(NumpyBaseTest):
    def __init__(self):
        super().__init__()
        self.valid_systems = ['ubelix:epyc2']
        self.num_cpus_per_task = 36

@rfm.simple_test
class NumpyBroadwellTest(NumpyBaseTest):
    def __init__(self):
        super().__init__()
        self.valid_systems = ['ubelix:bdw']
        self.num_cpus_per_task = 20

@rfm.simple_test
class NumpyGpuTest(NumpyBaseTest):
    def __init__(self):
        super().__init__()
        self.valid_systems = ['ubelix:gpu']
        self.num_cpus_per_task = 3
