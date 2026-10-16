# SPDX-License-Identifier: MIT
"""Constrain production providers to the existing open toolchain drivers."""
from pathlib import Path
import subprocess
from source_providers import ROOT


def validate_license_free(plan, recipes=None):
    # Arbitrary legacy commands cannot establish which compiler they invoke.
    if recipes:
        raise ValueError('license-free mode requires source-plan providers, not arbitrary --recipes')
    tools = {}
    for unit in plan['units']:
        argv = unit['argv']
        driver = Path(argv[0]).name
        if driver == 'clang':
            command = [argv[0], '--version']
            family = 'clang'
        elif driver == 'python3' and len(argv)>3 and argv[1]=='{root}/tools/build/linux_gcc.py' and argv[2]=='--compiler':
            compiler = argv[3]
            if unit.get('compiler_path') != compiler or not unit.get('compiler_sha256'):
                raise ValueError('license-free GCC wrapper requires a fingerprinted compiler')
            if Path(compiler).name != 'arm-none-eabi-gcc':
                raise ValueError('license-free mode only admits Clang and ARM GNU GCC')
            command = None
            family = 'gcc'
        else:
            raise ValueError('unapproved compiler driver in license-free mode: '+str(argv[:3]))
        identity = unit.get('compiler_path',argv[0])
        if identity not in tools:
            version = subprocess.run(command,cwd=ROOT,capture_output=True,text=True,check=True).stdout if command else None
            if version and 'clang version' not in version:
                raise ValueError('compiler does not identify as Clang')
            tools[identity] = dict(family=family,version=version,sha256=unit.get('compiler_sha256'))
    linker=subprocess.run(['arm-none-eabi-ld','--version'],capture_output=True,text=True,check=True).stdout
    if 'GNU ld' not in linker:raise ValueError('license-free mode requires GNU ARM ld')
    return dict(linker_version=linker,mode='license-free',compilers=tools,policy='Clang and fingerprinted ARM GNU GCC via the repository driver; no proprietary compiler invocation or activation.')
