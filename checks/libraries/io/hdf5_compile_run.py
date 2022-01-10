# Copyright 2016-2021 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import reframe as rfm
import reframe.utility.osext as osext
import reframe.utility.sanity as sn
from reframe.utility import find_modules, functools

@rfm.simple_test
class HDF5Test(rfm.RegressionTest):
    lang = parameter(['c', 'f90'])
    #lang = parameter(['c'])
    valid_systems = ['ubelix:epyc2', 'ubelix:bdw']
    build_system = 'SingleSource'
    keep_files = ['h5dump_out.txt']
    num_tasks = 1
    num_tasks_per_node = 1
    postrun_cmds = ['h5dump h5ex_d_chunk.h5 > h5dump_out.txt']
    maintainers = ['Mandes']
    tags = {'production', 'health'}

    valid_prog_environs = ['foss', 'intel']
    module_list = find_modules('HDF5', environ_mapping={
                    r'.*-gompi-.*': 'foss',
                    r'.*-iimpi-.*': 'intel',
                    })
    module_list = [tup for tup in module_list]

    @run_after('init')
    def set_description(self):
        lang_names = {
            'c': 'C',
            'f90': 'Fortran 90'
        }
        self.descr = (f'{lang_names[self.lang]} HDF5 ')

    @run_after('setup')
    def set_prog_environs(self):
        env = self.current_environ.name
        env_mods = [tup[2] for tup in self.module_list if tup[1].startswith(env)]
        env_mods.sort()
        if (len(env_mods) == 0):
            sn.assert_false(True,
                    f'no HDF5 module found for {env}')
        else:
            sel = env_mods[-1]
            self.modules = [sel]

    @run_before('compile')
    def set_sourcepath(self):
        self.sourcepath = f'h5ex_d_chunk.{self.lang}'

    @run_before('compile')
    def set_ldflags(self):
        self.build_system.cppflags = [
            '-I$EBROOTHDF5/include',
        ]
        if self.lang == 'c':
            self.build_system.ldflags = [
                '-L$EBROOTNETCDF/lib',
                '-lhdf5 -lhdf5_cpp'
            ]
        elif self.lang == 'f90':
            self.build_system.ldflags = [
                '-L$EBROOTNETCDF/lib',
                '-lhdf5 -lhdf5_fortran'
            ]

    @run_before('sanity')
    def set_sanity(self):
        # C and Fortran write transposed matrix
        if self.lang == 'c':
            self.sanity_patterns = sn.all([
                sn.assert_found(r'Data as written to disk by hyberslabs',
                                self.stdout),
                sn.assert_found(r'Data as read from disk by hyperslab',
                                self.stdout),
                sn.assert_found(r'\(0,0\): 0, 1, 0, 0, 1, 0, 0, 1,',
                                'h5dump_out.txt'),
                sn.assert_found(r'\(0,0\): 0, 1, 0, 0, 1, 0, 0, 1,',
                                'h5dump_out.txt'),
                sn.assert_found(r'\(1,0\): 1, 1, 0, 1, 1, 0, 1, 1,',
                                'h5dump_out.txt'),
                sn.assert_found(r'\(2,0\): 0, 0, 0, 0, 0, 0, 0, 0,',
                                'h5dump_out.txt'),
                sn.assert_found(r'\(3,0\): 0, 1, 0, 0, 1, 0, 0, 1,',
                                'h5dump_out.txt'),
                sn.assert_found(r'\(4,0\): 1, 1, 0, 1, 1, 0, 1, 1,',
                                'h5dump_out.txt'),
                sn.assert_found(r'\(5,0\): 0, 0, 0, 0, 0, 0, 0, 0',
                                'h5dump_out.txt'),
            ])
        else:
            self.sanity_patterns = sn.all([
                sn.assert_found(r'Data as written to disk by hyberslabs',
                                self.stdout),
                sn.assert_found(r'Data as read from disk by hyperslab',
                                self.stdout),
                sn.assert_found(r'\(0,0\): 0, 1, 0, 0, 1, 0,',
                                'h5dump_out.txt'),
                sn.assert_found(r'\(1,0\): 1, 1, 0, 1, 1, 0,',
                                'h5dump_out.txt'),
                sn.assert_found(r'\(2,0\): 0, 0, 0, 0, 0, 0,',
                                'h5dump_out.txt'),
                sn.assert_found(r'\(3,0\): 0, 1, 0, 0, 1, 0,',
                                'h5dump_out.txt'),
                sn.assert_found(r'\(4,0\): 1, 1, 0, 1, 1, 0,',
                                'h5dump_out.txt'),
                sn.assert_found(r'\(5,0\): 0, 0, 0, 0, 0, 0,',
                                'h5dump_out.txt'),
                sn.assert_found(r'\(6,0\): 0, 1, 0, 0, 1, 0,',
                                'h5dump_out.txt'),
                sn.assert_found(r'\(7,0\): 1, 1, 0, 1, 1, 0',
                                'h5dump_out.txt'),
            ])
