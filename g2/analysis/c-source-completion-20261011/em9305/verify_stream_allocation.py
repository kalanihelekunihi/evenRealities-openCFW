from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Native316ad4..316b5c'):s.index('/* Native31ac84..31ace0')].replace('*(volatile uint32_t *)(uintptr_t)0x805cacu','config_pointer').replace('*(volatile uint32_t *)(uintptr_t)0x805c40u','base_pointer')
h=r'''#include <stdint.h>
#include <assert.h>
#include <string.h>
#include <stdio.h>
static _Alignas(4) uint8_t config[80],record[1200],rows[256*8];static uintptr_t config_pointer,base_pointer;static unsigned clears;
void *opencfw_em9305_memset(void *p,unsigned v,unsigned n){assert(v==0&&n==256);clears++;return memset(p,v,n);}
'''+b+r'''
int main(void){unsigned n=0;config_pointer=(uintptr_t)config;base_pointer=(uintptr_t)rows;
for(unsigned count=0;count<8;count++)for(unsigned free=0;free<9;free++)for(unsigned slot=0;slot<256;slot++)for(unsigned mode=0;mode<2;mode++){
 memset(rows,0xa5,sizeof rows);memset(record,0,sizeof record);config[58]=count;config[34]=17;config[53]=23;record[52]=slot;record[3]=mode;clears=0;if(free<8)rows[free*256]=0;unsigned found=free<count;uintptr_t expected=found?(uintptr_t)(rows+free*256):0;assert(opencfw_em9305_radio_stream_allocate_316ad4((uintptr_t)record)==expected);assert(clears==found);assert(record[52]==(found?(uint8_t)(slot+1):slot));if(found){uint8_t *r=(uint8_t *)expected;assert(r[0]==1&&r[1]==(uint8_t)(slot+1)&&*(uint16_t *)(r+2)==40+free&&*(uint32_t *)(r+4)==(uint32_t)(uintptr_t)record);assert(*(uint32_t *)(record+56+slot*4)==(uint32_t)expected);assert(mode?r[36]==255:r[44]==255&&r[100]==127);}n++;}
printf("%u\n",n);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('stream-allocation-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C count/firstfree/record-slot byte wrap/mode and record publication; fixedRAM/memset normalized. No nativeISA or hardware execution.'},indent=2)+'\n');print('PASS',n)
