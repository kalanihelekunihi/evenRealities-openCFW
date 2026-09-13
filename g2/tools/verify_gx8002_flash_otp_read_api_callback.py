# SPDX-License-Identifier: MIT
"""Read API dispatch through source-owned table to decoded chunking callback."""
import json,struct,subprocess
from verify_gx8002_flash_otp_read_api import verify as qualify,ROOT
from compare_gx8002_flash_otp_read import execute as read
from model_gx8002_flash_otp_read import expected
from execute_gx8002_clock_source_select import execute
from verify_gx8002_power_initialize import word
from verify_gx8002_memcpy_source import decode
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import sha


def verify():
    evidence=qualify();directory=ROOT/'build/gx8002-board';artifacts={}
    for kind,filename in (('flash-interface-table','flash-interface-table.elf'),('flash-otp-read','otp-read.elf')):
        path=directory/filename;elf=Elf32(path.read_bytes(),kind);report=json.loads((ROOT/f'docs/research/gx8002-{kind}-verification.json').read_text())
        for row in report.get('functions',[report]):
            section=next(s for s in elf.sections if s['name']==row['section_name']);assert sha(elf.contents(section))==row['compiled_sha256']
        artifacts[kind]=elf
    table=artifacts['flash-interface-table'];data=table.contents(next(s for s in table.sections if s['name']=='.data.flash_interface'));target=struct.unpack_from('<I',data,88)[0];assert target==0x10023fa4
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');code=decode(subprocess.check_output([pre,'-d',str(directory/'otp-read.elf')],text=True));wrapper=decode((directory/'flash-otp-read-api-candidate.disassembly.txt').read_text());calls=[]
    for address in (0,1,1023,0xffffffff):
      for length in (0,1,31,32,33,65):
       for manufacturer in (0,0x5e,0x85,0xffff):
            memory={};word(memory,0x2002655c,target);args=[0x20026504,address,0xfffffffe,length]
            wanted,trace=expected(address,args[2],length,1024,4096,4096,7,manufacturer,delay=1)
            def callback(destination,parameters,state,events):
                assert destination==target and parameters[:3]==args[1:]
                result=read(code,target,0,*parameters[:3],trace,seed=0xffffffff,frame=48)
                assert result==wanted;calls.append(result);return result
            result,after,events=execute(wrapper,0x100247f4,args,memory,callback)
            assert result[:2]==('return',wanted) and after==memory and not events
    assert len(calls)==96
    summarized=0
    for length in (0x80000000,0x80000001,0xffffff00,0xffffffff):
        address=(-length)&0xffffffff
        memory={};word(memory,0x2002655c,target);args=[0x20026504,address,0xfffffffe,length]
        wanted,trace=expected(address,args[2],length,0,4096,4096,0,0x85,summarize_receive=True)
        def callback(destination,parameters,state,events):
            assert destination==target and parameters[:3]==args[1:]
            result=read(code,target,0,*parameters[:3],trace,frame=48,summarize_receive=True)
            assert result==wanted
            return result
        result,after,events=execute(wrapper,0x100247f4,args,memory,callback)
        assert result[:2]==('return',wanted) and after==memory and not events
        summarized+=1
    return {'evidence':evidence,'decoded_read_callbacks':len(calls),'summarized_large_receive_cases':summarized,'source_table_target':target,'source_admitted':False,
            'limits':['Source-generated callback slot authenticated; actual decoded OTP read/rejection paths drive wrapper return.',
                       'SPI readiness, device state, and address encoder effects scripted as in admitted OTP read qualification; Four high-bit lengths use the separately structure-checked receive-loop summary, not literal billion-byte iteration; no physical hardware qualification.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-flash-otp-read-api-callback.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_read_callbacks'])
