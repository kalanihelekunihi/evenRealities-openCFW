from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Native30b230..30b2d8'):s.index('/* Native31aa64..31aa98')].replace('*(volatile uint32_t *)(uintptr_t)0x805cacu','state_pointer')
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static _Alignas(4) uint8_t input[40],state[80];static uintptr_t state_pointer;static unsigned exists,calls,applies;
uint32_t opencfw_em9305_radio_record_exists_3072d0(uint32_t id){assert(id==input[1]);calls++;return exists;}
uint32_t opencfw_em9305_radio_record_apply_309cfc(uintptr_t p){assert(p==(uintptr_t)input&&calls==1);applies++;return 0x12345678;}
static void reset(void){memset(input,0,sizeof input);input[0]=input[1]=1;input[2]=1;*(uint32_t *)(input+4)=256;*(uint16_t *)(input+10)=5;input[13]=1;calls=applies=0;}
'''+b+r'''
int main(void){unsigned n=0;state_pointer=(uintptr_t)state;
for(unsigned cap=0;cap<2;cap++)for(unsigned extra=0;extra<256;extra++)for(unsigned req=0;req<256;req++)for(exists=0;exists<2;exists++){reset();state[62]=cap;state[63]=extra;input[13]=req;unsigned allowed=(cap?3:1)|(extra<<2);unsigned status=(req&~allowed)?17:req==0?18:exists?0x12345678:66;assert(opencfw_em9305_command_30b230((uintptr_t)input)==status);assert(calls==(status==66||status==0x12345678)&&applies==(status==0x12345678));n++;}
state[62]=state[63]=0;exists=1;
for(unsigned value=0;value<65536;value++){reset();*(uint16_t *)(input+10)=value;unsigned valid=(uint16_t)(value+0xf05f)>=0xf064;assert(opencfw_em9305_command_30b230((uintptr_t)input)==(valid?0x12345678:18));n++;}
printf("%u\n",n);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('packed-validation-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C all capability-extra/request bytes, lookup outcomes, full16bit wrapped timing bound; normalized RAM/genuine children. Other bounds source-inspected; no ISA/hardware execution.'},indent=2)+'\n');print('PASS',n)
