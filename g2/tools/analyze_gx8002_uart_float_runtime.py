# SPDX-License-Identifier: MIT
"""Record upstream runtime provenance and stock identity limits."""
import json,subprocess
from build_gx8002_uart_configure_object import build,ROOT
from analyze_gx8002_upstream_objects import IMAGE,IMAGE_SHA,sha,authenticated_blob
from build_transparent_image import Elf32

def analyze():
    candidate=build();gcc=ROOT/'build/upstream-csky-toolchain-build/gcc';commit=candidate['runtime_link']['gcc_source_commit']
    sources=[]
    for name in ('libgcc/fp-bit.c','libgcc/fp-bit.h','libgcc/libgcc2.c','libgcc/config/csky/t-csky','COPYING.RUNTIME'):
        blob=subprocess.check_output(['git','-C',str(gcc),'rev-parse',commit+':'+name],text=True).strip()
        sources.append({'path':name,'blob':blob,'sha256':sha(authenticated_blob(gcc/name,blob))})
    path=ROOT/'build/gx8002-uart-configure/runtime.elf';elf=Elf32(path.read_bytes(),str(path));text=next(s for s in elf.sections if s['name']=='.text');payload=elf.contents(text)
    stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('Stock identity')
    rows=[]
    for name,offset in (('__floatunsidf',0x13a5c),('__fixunsdfsi',0x12ff8),('__divdf3',0x13894),('__muldf3',0x13694),('__adddf3',0x13628)):
        symbol=next(s for s in elf.symbols() if s['name']==name);start=symbol['value']-text['address'];body=payload[start:start+symbol['size']]
        rows.append({'symbol':name,'stock_candidate_offset':offset,'linked_address':symbol['value'],'compiled_bytes':len(body),'compiled_sha256':sha(body),'equal_length_stock_slice_sha256':sha(stock[offset:offset+len(body)]),'byte_exact':body==stock[offset:offset+len(body)]})
    return {'candidate':candidate,'upstream_source_files':sources,'helper_comparison':rows,'source_admitted':False,'limits':['Stock target names inferred from UART arithmetic and structural similarity, not yet fully proved. Equal-length slices are not established stock function extents. No helper is byte-exact; semantic execution is required. Native GCC runtime is source-built, not binary extracted.']}

if __name__=='__main__':
    report=analyze();(ROOT/'docs/research/gx8002-uart-float-runtime.json').write_text(json.dumps(report,indent=2)+'\n');print('Runtime helpers:',len(report['helper_comparison']))
