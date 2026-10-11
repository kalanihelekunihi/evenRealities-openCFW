from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Native30b2d8..30b3f8'):s.index('/* Native307410..307434')].replace('*(volatile uint32_t *)(uintptr_t)0x805cacu','state_pointer').replace('*(volatile uint8_t *)(uintptr_t)0x805a86u','mode_byte').replace('__asm__ volatile("mpyuw %0,%1,1250":"=r"(product):"r"(interval));','product=interval*1250u;').replace('__asm__ volatile("remu %0,%1,%2":"=r"(remainder):"r"(product),"r"(period));','remainder=product%period;').replace('__asm__ volatile("mpyuw %0,%1,%2":"=r"(product):"r"(factor),"r"(groups));','product=factor*groups;')
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static _Alignas(4) uint8_t input[40],state[80],mode_byte;static uintptr_t state_pointer;static unsigned available;
uint32_t opencfw_em9305_radio_record_available_307410(uint32_t id){assert(id==input[1]);return available;}
uint32_t opencfw_em9305_radio_record_extended_apply_309e60(uintptr_t p){assert(p==(uintptr_t)input);return 0x12345678;}
static void reset(void){memset(input,0,40);memset(state,0,80);input[0]=input[1]=input[2]=1;*(uint32_t *)(input+4)=256;*(uint16_t *)(input+24)=4;input[26]=4;*(uint16_t *)(input+30)=1;input[32]=input[34]=input[35]=input[36]=1;*(uint16_t *)(state+46)=251;}
static unsigned expected(void){unsigned interval=*(uint16_t *)(input+24),count=input[26],size=*(uint16_t *)(input+30),g=input[35],f=input[36],p=*(uint32_t *)(input+4);if(input[0]>239||input[1]>239||input[2]==0||input[2]>31||p<256||p>0xfffff||interval<((mode_byte&128)?2:4)||interval>3200||count==0||count>31||*(uint16_t *)(input+28)>4095||size==0||size>251||input[32]==0||input[33]>1||input[34]>1||g==0||g>7||f==0||f>15||input[37]>15||input[38]>1)return48;if(!input[34]&&(interval*1250)%p)return48;if(input[37]||g>=7||count>=9||size>*(uint16_t *)(state+46)||f>=5||count<f*g)return17;if(!available)return66;unsigned allowed=(state[62]?3:1)|(state[63]<<2);if(input[32]&~allowed)return17;return0x12345678;}
'''.replace('return48','return 48').replace('return17','return 17').replace('return66','return 66').replace('return0x','return 0x')+b+r'''
int main(void){unsigned n=0;state_pointer=(uintptr_t)state;unsigned offsets[]={0,1,2,26,32,33,34,35,36,37,38};for(unsigned j=0;j<11;j++)for(unsigned v=0;v<256;v++)for(available=0;available<2;available++){reset();input[offsets[j]]=v;assert(opencfw_em9305_command_30b2d8((uintptr_t)input)==expected());n++;}for(unsigned v=0;v<65536;v++){reset();*(uint16_t *)(input+24)=v;available=1;assert(opencfw_em9305_command_30b2d8((uintptr_t)input)==expected());n++;}printf("%u\n",n);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('extended-validation-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C boundary sweeps of11 byte fields/all interval16bitvalues with availability outcomes. RAM/children/MPYUW/REMU normalized; native remainder-zero-divisor/ISA/hardware not executed.'},indent=2)+'\n');print('PASS',n)
