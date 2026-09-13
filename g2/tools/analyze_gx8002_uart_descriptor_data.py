# SPDX-License-Identifier: MIT
"""Authenticate retained UART descriptors against pinned SDK uart_config."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32

def analyze():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';rel='drivers_lib/serial/dw_uart.o';blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',SDK_COMMIT+':'+rel],text=True).strip();data=authenticated_blob(sdk/rel,blob);elf=Elf32(data,rel);symbol=next(s for s in elf.symbols() if s['name']=='uart_config');section=elf.sections[symbol['section']]
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA;body=elf.contents(section)
    assert symbol['value']==0 and symbol['size']==256 and len(body)==256 and not elf.relocations(section['index']) and body==stock[0x18aa8:0x18ba8]
    return {'sdk_commit':SDK_COMMIT,'object_blob':blob,'object_sha256':sha(data),'symbol':symbol,'package_offset':0x18aa8,'runtime_address':0x20026a94,'bytes':256,'sha256':sha(body),'source_admitted':False,'limits':['Exact authenticated UART configuration data match. Two128byte descriptors, UART bases, baud115200,unnamed defaults8/1 andIRQ6/7 agree with recovered consumers. Full typed source layout and ownership qualification pending; object bytes must not enter source build.']}
if __name__=='__main__':
    r=analyze();(ROOT/'docs/research/gx8002-uart-descriptor-data.json').write_text(json.dumps(r,indent=2)+'\n');print(r['bytes'])
