#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Run an existing Linux GCC with read-only inputs and one writable output dir."""
import argparse
import os
from pathlib import Path
import subprocess
import sys


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--compiler',type=Path,required=True)
    p.add_argument('--read-root',type=Path,action='append',default=[])
    p.add_argument('arguments',nargs=argparse.REMAINDER)
    a=p.parse_args();args=a.arguments
    if args[:1]==['--']:args=args[1:]
    if '-MF' not in args:p.error('dependency output (-MF) required')
    output=Path(args[args.index('-MF')+1]).resolve().parent
    if not output.is_dir():p.error('output directory must already exist')
    compiler=a.compiler.resolve()
    container=os.environ.get('OPENCFW_GCC_CONTAINER')
    if container:
        return subprocess.run(['docker','exec',container,str(compiler),*args]).returncode
    readonly={compiler.parents[1],*(r.resolve() for r in a.read_root)}
    command=['docker','run','--rm','--network=none','--platform','linux/amd64']
    for root in sorted(readonly):
        command+=['--mount',f'type=bind,src={root},dst={root},readonly']
    command+=['--mount',f'type=bind,src={output},dst={output}',
              '--entrypoint',str(compiler),'ubuntu:24.04',*args]
    return subprocess.run(command).returncode

if __name__=='__main__':sys.exit(main())
