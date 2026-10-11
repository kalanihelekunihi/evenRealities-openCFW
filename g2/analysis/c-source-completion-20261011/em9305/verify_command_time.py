from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native325268..325284'):s.index('/* Native306a90..306a9c')]
body=body.replace('*(volatile uint8_t *)(uintptr_t)0x805b18u','host_handler').replace('*(volatile uint32_t *)(uintptr_t)0x805b58u','time_word').replace('*(volatile uint8_t *)(uintptr_t)0x8051f0u','timer_handler')
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
static uint8_t host_handler,timer_handler;static uint32_t time_word,incoming,calls;
uint32_t opencfw_em9305_wsf_timer_start_seconds(uintptr_t timer,uint32_t time){assert(timer==0x8051e4&&time==incoming&&time_word==incoming&&timer_handler==host_handler);calls++;return 0xffffffff;}
'''+body+r'''
int main(void){unsigned n=0;for(unsigned low=0;low<65536;low++)for(unsigned high=0;high<3;high++){incoming=low|(high==1?0x10000:high==2?0xffff0000:0);host_handler=low;timer_handler=88;time_word=99;calls=0;unsigned valid=(uint16_t)(incoming-1)<=0xa1b7;assert(opencfw_em9305_command_30deec(incoming)==(valid?0:18));assert(calls==valid);if(!valid)assert(time_word==99&&timer_handler==88);n++;}printf("%u\n",n);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('command-time-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Three actual C bodies, all low16 values/highwordfixtures, fullword time store, handler/timer ordering and ignored lower result. Normalized RAM/timer; nativeISA/hardware unproved.'},indent=2)+'\n');print('PASS',n)
