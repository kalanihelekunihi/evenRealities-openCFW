# SPDX-License-Identifier: MIT
"""Connect compiled board policy data to decoded initializer reads."""
import json
from build_transparent_image import Elf32
import verify_gx8002_board_pin_initialize as init
from verify_gx8002_board_pin_defaults import verify as data


def verify():
    policy=data();candidate=init.build();old,new=init.programs()
    path=init.ROOT/'build/gx8002-board/board-pin-defaults.o'
    elf=Elf32(path.read_bytes(),str(path));row=policy['functions'][0]
    section=next(s for s in elf.sections if s['name']==row['section_name'])
    payload=elf.contents(section)
    table=[tuple(payload[i:i+2]) for i in range(0,len(payload),2)]
    if len(table)!=13:raise ValueError('Initializer source table count')
    count=0
    for errors in (0,8191,*[1<<i for i in range(13)]):
        for returns in (False,True):
            for code,entry in ((old,0xfe2c),(new,init.ADDRESS)):
                got=init.execute(code,entry,table,errors,returns)
                if got!=init.expected(table,errors,returns):raise ValueError('Initializer source table trace')
                reads=[x for x in got[1] if x[0]=='read']
                want=[('read',init.TABLE+i,value) for i,value in enumerate(payload)]
                if reads!=want:raise ValueError('Initializer source data read extent/order')
                directions=[x for x in got[1] if x[0]=='direction']
                if directions!=[('direction',pin,0) for pin in range(13)]:raise ValueError('Initializer input policy')
                count+=1
    return {'candidate':candidate,'policy':policy,'decoded_cases':count,
            'source_admitted':False,'hardware_qualified':False,
            'limits':['Compiled table read in decoded initializer with translated memory. Helpers modeled; no MMIO/physical effects proven here.']}


if __name__=='__main__':
    report=verify();(init.ROOT/'docs/research/gx8002-board-pin-initialize-table.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Initializer/source-table cases:',report['decoded_cases'])
