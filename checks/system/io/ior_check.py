# Copyright 2016-2021 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import getpass
import os
import re

import reframe as rfm
import reframe.utility.sanity as sn


class IorCheck(rfm.RegressionTest):
    base_dir = parameter(['/storage/scratch',
                        '/storage/workspace',
                        '/storage/homefs'])
    @run_after('init')
    def set_params(self):
        self.descr = f'IOR check ({self.base_dir})'
        self.time_limit = '1h'
        self.tags = {'ops', self.base_dir}
        if self.base_dir in os.getenv('SCRATCH'):
            self.test_dir = os.path.join(os.getenv('SCRATCH'), 'ior')
        elif self.base_dir in os.getenv('WORKSPACE'):
            self.test_dir = os.path.join(os.getenv('WORKSPACE'), 'ior')
        elif self.base_dir in os.getenv('HOME'):
            self.test_dir = os.path.join(os.getenv('HOME'), 'ReFrame', 'stage', 'ior')

        self.prerun_cmds = ['mkdir -p ' + self.test_dir]
        self.test_file = os.path.join(self.test_dir, 'ior')
        self.fs = {
            '/storage/scratch': {
                'valid_systems': ['ubelix:bdw', 'ubelix:gpu', 'ubelix:epyc2'],
                'ubelix:gpu': { 'num_tasks': 1, },
                'ubelix:bdw': { 'num_tasks': 3, },
                'ubelix:epyc2': { 'num_tasks': 3, },
            },
            '/storage/workspace': {
                 'valid_systems': ['ubelix:bdw', 'ubelix:gpu', 'ubelix:epyc2'],
                'ubelix:gpu': { 'num_tasks': 1, },
                'ubelix:bdw': { 'num_tasks': 3, },
                'ubelix:epyc2': { 'num_tasks': 3, },
            },
            '/storage/homefs': {
                  'valid_systems': ['ubelix:bdw', 'ubelix:gpu', 'ubelix:epyc2'],
                'ubelix:gpu': { 'num_tasks': 1, },
                'ubelix:bdw': { 'num_tasks': 3, },
                'ubelix:epyc2': { 'num_tasks': 3, },
            },
        }

        # Setting some default values
        for data in self.fs.values():
            data.setdefault('ior_block_size', '8g')
            data.setdefault('ior_access_type', 'MPIIO')
            data.setdefault(
                'reference',
                {
                    'read_bw': (0, None, None, 'MiB/s'),
                    'write_bw': (0, None, None, 'MiB/s')
                }
            )
            data.setdefault('dummy', {})  # entry for unknown systems

        cur_sys = self.current_system.name
        if cur_sys not in self.fs[self.base_dir]:
            cur_sys = 'dummy'

        self.valid_systems = self.fs[self.base_dir]['valid_systems']

        self.ior_block_size = self.fs[self.base_dir]['ior_block_size']
        self.ior_access_type = self.fs[self.base_dir]['ior_access_type']
        self.executable_opts = ['-B', '-F', '-C ', '-Q 1', '-t 4m', '-D 30',
                                '-b', self.ior_block_size,
                                '-a', self.ior_access_type]
        self.sourcesdir = os.path.join(self.current_system.resourcesdir, 'IOR')
        #self.executable = os.path.join('src', 'C', 'IOR')
        self.build_system = 'Make'

        vpe = 'valid_prog_environs'
        penv = self.fs[self.base_dir][cur_sys].get(vpe, ['intel'])
        self.valid_prog_environs = penv

        self.build_system.options = ['posix', 'mpiio']
        self.build_system.max_concurrency = 1
        self.num_gpus_per_node = 0

        # Default umask is 0022, which generates file permissions -rw-r--r--
        # we want -rw-rw-r-- so we set umask to 0002
        os.umask(2)
        self.time_limit = '5m'
        # Our references are based on fs types but regression needs reference
        # per system.
        self.reference = {
            '*': self.fs[self.base_dir]['reference']
        }

        self.maintainers = ['Mandes']

        systems_to_test = ['ubelix']
        if self.current_system.name in systems_to_test:
            self.tags |= {'production', 'external-resources'}

    @run_before('compile')
    def set_compile(self):
        self.builddir = os.path.join(self.stagedir, 'src', 'C')
        self.prebuild_cmds = ['cd ' + self.builddir ]
        self.postbuild_cmds = ['cd ' + self.stagedir ]

    @run_before('run')
    def set_exec_opts(self):
        self.executable = os.path.join(self.stagedir, 'src', 'C', 'IOR')
        part = self.current_partition.fullname
        self.num_tasks = self.fs[self.base_dir][part].get('num_tasks', 3)
        tpn = self.fs[self.base_dir][part].get('num_tasks_per_node', 1)
        self.num_tasks_per_node = tpn
        self.test_file += '.' + self.current_partition.name
        self.executable_opts += ['-o', self.test_file]

@rfm.simple_test
class IorWriteCheck(IorCheck):
    executable_opts += ['-w', '-k']
    tags |= {'write'}

    @sanity_function
    def assert_output(self):
        return sn.assert_found(r'^Max Write: ', self.stdout)

    @run_after('init')
    def set_perf_patterns(self):
        self.perf_patterns = {
            'write_bw': sn.extractsingle(
                r'^Max Write:\s+(?P<write_bw>\S+) MiB/sec', self.stdout,
                'write_bw', float)
        }

@rfm.simple_test
class IorReadCheck(IorCheck):
    executable_opts += ['-r']
    tags |= {'read'}

    @sanity_function
    def assert_output(self):
        return sn.assert_found(r'^Max Read: ', self.stdout)

    @run_after('init')
    def set_perf_patterns(self):
        self.perf_patterns = {
            'read_bw': sn.extractsingle(
                r'^Max Read:\s+(?P<read_bw>\S+) MiB/sec', self.stdout,
                'read_bw', float)
        }

    @run_after('init')
    def set_dependency(self):
        self.depends_on(re.sub(r'IorReadCheck', 'IorWriteCheck', self.name))
