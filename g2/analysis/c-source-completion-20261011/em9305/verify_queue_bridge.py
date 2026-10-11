from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native331cdc..'):s.index('/* Native30d9f4..')]
body=body.replace('*(volatile uint8_t *)(uintptr_t)0x805884u','busy_byte').replace('*(volatile uint32_t *)(uintptr_t)0x8058d4u','link_cell').replace('*(volatile uint32_t *)(uintptr_t)0x8058d0u','primary_cell')
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static _Alignas(4) uint8_t packet_data[20],output[20];static uint8_t busy_byte;static uintptr_t link_cell,primary_cell;static unsigned flags,pattern,removes,links,primaries;
static uintptr_t primary_callback(void){assert(removes==1);primaries++;return flags&32?(uintptr_t)packet_data:0;}
static uintptr_t link_callback(void){assert(removes==1);links++;if(pattern&1)primary_cell=(uintptr_t)&primary_callback;return flags&8?(uintptr_t)packet_data:0;}
uintptr_t opencfw_em9305_wsf_event_remove(uintptr_t queue,uintptr_t handler){assert(queue==0x805870);removes++;*(uint8_t*)handler=7;if(pattern&2)busy_byte=77;return flags&2?(uintptr_t)packet_data:0;}
'''+body+r'''
int main(void){unsigned cases=0;for(flags=0;flags<64;flags++){for(pattern=0;pattern<256;pattern++){for(unsigned alias=0;alias<2;alias++){
 memset(packet_data,0xa5,20);memset(output,0xa5,20);packet_data[1]=pattern;packet_data[2]=pattern;packet_data[3]=255-pattern;busy_byte=flags&1?255:0;link_cell=flags&4?(uintptr_t)&link_callback:0;primary_cell=flags&16?(uintptr_t)&primary_callback:0;removes=links=primaries=0;unsigned queued=!(flags&1)&&(flags&2),lc=!(flags&1)&&!queued&&(flags&4),lp=lc&&(flags&8),pc=!(flags&1)&&!queued&&!lp&&((flags&16)||(lc&&(pattern&1))),pp=pc&&(flags&32);unsigned success=queued||lp||pp,type=queued?2:lp?3:1,length=queued?pattern+2:(uint16_t)(pattern+((255-pattern)<<8)+4);uint8_t expected[20];uint8_t *dest=alias?packet_data:output;memcpy(expected,dest,20);
 if(success){expected[2]=type;*(uint32_t*)(expected+8)=(uint32_t)(uintptr_t)packet_data;*(uint16_t*)(expected+4)=length;}
 assert(opencfw_em9305_dispatch_331cdc((uintptr_t)(dest+2),(uintptr_t)(dest+4),(uintptr_t)(dest+8))==success&&removes==!(flags&1)&&links==lc&&primaries==pc);assert(memcmp(expected,dest,20)==0);assert(busy_byte==(flags&1?255:success?1:pattern&2?77:0));cases++;
}}}printf("%u\n",cases);}
'''
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'t.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(d/'t.c'),'-o',str(d/'t')],check=True);n=int(subprocess.check_output([str(d/'t')],text=True))
Path(__file__).with_name('queue-bridge-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C queue bridge with normalized busy/callback cells. Busy/queue/link/primary permutations, header byte patterns and aliased type output, provider priority, primary callback replacement bylink child, busy mutation byqueue child without invented recheck, untouched empty outputs and captured length writes. Controlled children; not native runtime equality.','body_sha256':hashlib.sha256(body.encode()).hexdigest()},indent=2)+'\n');print('PASS',n)
