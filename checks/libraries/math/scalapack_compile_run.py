# Copyright 2016-2021 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.sanity as sn
from reframe.utility import find_modules, functools

@rfm.simple_test
class ScaLAPACKTest(rfm.RegressionTest):
    linkage = parameter(['static', 'dynamic'])

    sourcepath = 'sample_pdsyev_call.f'
    valid_systems = ['ubelix:epyc2', 'ubelix:bdw']
    valid_prog_environs = ['foss']
    num_tasks = 16
    num_tasks_per_node = 8
    build_system = 'SingleSource'
    maintainers = ['Mandes']
    tags = {'production', 'external-resources'}

    module_list = find_modules('ScaLAPACK', environ_mapping={
                    r'.*-gompi-.*': 'foss',
                    })

    @run_after('setup')
    def set_build_flags(self):
        env = self.current_environ.name
        if env == 'foss':
            self.build_system.fflags = ['-O3 -lscalapack']
        elif env == 'intel':
            self.build_system.fflags = ['-O3 -L${EBROOTIMKL}/lib/intel64 -lmkl_blacs_intelmpi_ilp64 -lmkl_lapack95_ilp64 -lmkl_scalapack_ilp64 -lmkl_blas95_ilp64 -lmkl_intel_ilp64 -lmkl_core -mkl -ldl -lm']


    @run_after('setup')
    def set_module(self):
        # intel uses MKL,
        ## which is automatically loaded with intel toolchain
        # foss need to load ScaLAPACK module
        ## here we select the latest version using only gompi and
        ## neglecting gompic versions
        env = self.current_environ.name
        if env in ['foss']:
            env_mods = [tup[2] for tup in self.module_list
                        if tup[1].startswith(env)]
            env_mods.sort()
            if (len(env_mods) == 0):
                sn.assert_false(True,
                        f'no ScaLAPACK module for gompi')
            else:
                sel = env_mods[-1]
                self.modules = [sel]

    @run_before('sanity')
    def set_sanity_patterns(self):
        def fortran_float(value):
            return float(value.replace('D', 'E'))

        def scalapack_sanity(number1, number2, expected_value):
            symbol = f'z{number1}{number2}'
            pattern = (rf'Z\(     {number2},     {number1}\)='
                       rf'\s+(?P<{symbol}>\S+)')
            found_value = sn.extractsingle(pattern, self.stdout, symbol,
                                           fortran_float)
            return sn.assert_lt(sn.abs(expected_value - found_value), 1.0e-15)

        self.sanity_patterns = sn.all([
            scalapack_sanity(1, 1, -0.04853779318803846),
            scalapack_sanity(1, 2, -0.12222271866735863),
            scalapack_sanity(1, 3, -0.28248513530339736),
            scalapack_sanity(1, 4, 0.95021462733774853),
            scalapack_sanity(2, 1, 0.09120722270314352),
            scalapack_sanity(2, 2, 0.42662009209279039),
            scalapack_sanity(2, 3, -0.8770383032575241),
            scalapack_sanity(2, 4, -0.2011973015939371),
            scalapack_sanity(3, 1, 0.4951930430455262),
            scalapack_sanity(3, 2, -0.7986420412618930),
            scalapack_sanity(3, 3, -0.2988441319801194),
            scalapack_sanity(3, 4, -0.1662736444220721),
            scalapack_sanity(4, 1, 0.8626176298213052),
            scalapack_sanity(4, 2, 0.4064822185450869),
            scalapack_sanity(4, 3, 0.2483911184660867),
            scalapack_sanity(4, 4, 0.1701907253504270)
        ])
