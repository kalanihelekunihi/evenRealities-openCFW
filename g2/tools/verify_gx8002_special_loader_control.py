# SPDX-License-Identifier: MIT
"""Execute special loader control with explicitly symbolic flash-helper effects."""
import json
import subprocess
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_backup_memset_loader import execute
from verify_gx8002_memcpy_source import decode


def verify():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    tool=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    code=decode(subprocess.check_output([tool,'-D','--start-address=0x396a0','--stop-address=0x39724',str(wrapper)],text=True))
    cases=0
    for header in (0,4,0x1408c,0xffffffff):
        for seed in (0,91,0xffffffff):
            reads=[]
            def model(offset,dest,length):
                reads.append([offset,dest,length])
                # The second call's zero length is recorded, not interpreted as
                # a physical no-op or an implied whole-image read.
                return header.to_bytes(4,'little') if len(reads)==1 else b''
            result,calls,memory=execute(code,stock,0xaabbccdd,seed,model)
            expected=[['read',0x61760,0x2002ffec,4],['read',(header+0x323b4)&0xffffffff,0x20000000,0],['entry',0x10000100]]
            assert result==0 and calls==expected,(calls,expected)
            assert memory[0x2002d3e4]==0x10000100
            cases+=1
    return {'cases':cases,'stock_sha256':IMAGE_SHA,'special_mode':0xaabbccdd,'entry':0x10000100,'second_read_destination':0x20000000,'second_read_length_argument':0,'limits':['Decoded control and call arguments only, with supplied header words and returning entry. The physical meaning of zero length in flash helper 0x39930 is unresolved. This path does not establish a backup copy or backup entry, and does not resolve earlier-consumer lifetime.']}


if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-special-loader-control.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'],'special loader control cases passed')
