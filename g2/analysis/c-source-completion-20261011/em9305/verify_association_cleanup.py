from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Native327a4c..327a54'):s.index('struct opencfw_em9305_native_product_pair')];b=b.replace('*(volatile uint32_t *)(uintptr_t)0x805cacu','config_pointer').replace('*(volatile uint32_t *)(uintptr_t)0x805c3cu','record_pointer')
h=r'''#include <stdint.h>
#include <assert.h>
#include <string.h>
#include <stdio.h>
static _Alignas(4) uint8_t config[80],records[256*512],assoc[2824];static uintptr_t config_pointer,record_pointer,found;static unsigned queried,clears;
uintptr_t opencfw_em9305_radio_record_find_31aa64(uint32_t id){assert(id==257);queried++;return found;}
void *opencfw_em9305_memset(void *p,uint32_t v,uint32_t n){assert(p==assoc+176&&v==0&&n==96);clears++;return memset(p,v,n);}
'''+b+r'''
int main(void){config_pointer=(uintptr_t)config;record_pointer=(uintptr_t)records;unsigned cases=0;for(unsigned count=0;count<256;count++)for(unsigned pattern=0;pattern<4;pattern++)for(unsigned missing=0;missing<2;missing++){memset(records,0xcc,sizeof records);found=missing?0:55;config[57]=count;int expected=-1;for(unsigned i=0;i<count;i++){uint8_t *r=records+512*i;r[0]=0;r[3]=pattern==0?0:pattern==1?1:i%3==0?1:2;uint32_t value=pattern==3?found:(i+1==count||i==1)?found:77;*(uint32_t *)(r+180)=value;if(expected<0&&r[3]==1&&value==found)expected=i;}queried=0;opencfw_em9305_radio_association_callback_3291e4(257);assert(queried==1);for(unsigned i=0;i<count;i++){uint32_t value=pattern==3?found:(i+1==count||i==1)?found:77;assert(*(uint32_t *)(records+512*i+180)==(i==(unsigned)expected?0:value));}cases++;}
memset(assoc,0xa5,sizeof assoc);found=(uintptr_t)assoc;queried=clears=0;opencfw_em9305_radio_association_callback_3291d0(257);assert(queried==1&&clears==1);for(unsigned i=0;i<2824;i++)assert(assoc[i]==(i>=176&&i<272?0:0xa5));printf("%u\n",cases);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('association-cleanup-receipt.json').write_text(json.dumps({'scan_cases_passed':n,'clear_extent_passed':96,'scope':'Actual C all256 count bytes, mode/match/zero association patterns, first match, inactive rows and fullwidth id. Globals/find/memset normalized for host; no native runtime/data-layout/hardware proof.'},indent=2)+'\n');print('PASS',n,'CLEAR',96)
