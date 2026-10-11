from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('extern uint32_t opencfw_em9305_radio_access_seed_3189cc'):s.index('/* Native318878/3189cc')]
for addr,name in [('0x805aa4u','upper'),('0x805aa0u','lower'),('0x8028c0u','callback'),('0x805c3cu','base')]:b=b.replace('*(volatile uint32_t *)(uintptr_t)'+addr,name)
b=b.replace('*(volatile uint8_t *)(uintptr_t)0x805a9cu','mode')
for name in ['upper','lower','callback','base','mode']:b=b.replace(name+'='+name+';',name+'=g_'+name+';')
h=r'''#include <stdint.h>
#include <assert.h>
#include <string.h>
#include <stdio.h>
static uintptr_t g_callback,g_base;static uint32_t g_upper,g_lower,g_mode;
static uint8_t record[512];static uintptr_t callback,base;static uint32_t upper,lower,mode,seed,crc;static unsigned phase,called;
uint32_t opencfw_em9305_radio_access_seed_3189cc(void){assert(phase++==0);return seed;}
uint32_t opencfw_em9305_radio_crc_seed_318960(void){assert(phase++==1&&*(uint32_t *)(record+344)==seed);return crc;}
uint32_t opencfw_em9305_radio_access_mix_3188b8(uint32_t a,uint32_t i){assert(phase++==2&&a==seed&&i==0&&record[408]==13&&*(uint16_t *)(record+348)==(uint16_t)(crc>>8));return a^0x12345678;}
uint32_t opencfw_em9305_radio_channel_transform_30e3fc(uintptr_t p){assert(phase++==3&&p==(uintptr_t)(record+352)&&*(uint32_t *)p==lower&&*(uint32_t *)(p+4)==upper&&record[398]==1);record[292]=7;return 0;}
void *opencfw_em9305_memcpy(void *o,const void *i,uint32_t n){if(n==8){assert(phase++==4&&o==record+444&&i==record+485&&record[452]==1&&*(uint16_t *)(record+454)==513);}else{assert(phase++==5&&n==16&&o==record+428&&i==record+92);}return memcpy(o,i,n);}
static uint32_t cb(uintptr_t p,uint32_t id,uint32_t flag){assert(phase==6&&p==(uintptr_t)(record+428)&&id==9&&flag==1&&*(uint16_t *)(record+468)==513);called++;return 71;}
'''+b+r'''
int main(void){unsigned cases=0;for(unsigned sec=0;sec<256;sec++)for(unsigned c=0;c<2;c++){memset(record,0xcc,512);record[484]=sec;record[292]=2;for(unsigned i=0;i<16;i++)record[92+i]=i+9;for(unsigned i=0;i<8;i++)record[485+i]=i+3;seed=0xdeadbeef^sec;crc=0xabcdef01^sec;upper=17;lower=19;mode=33;callback=c?(uintptr_t)cb:0;base=(uintptr_t)record-3*512;phase=called=0;g_callback=callback;g_base=base;g_upper=upper;g_lower=lower;g_mode=mode;uint32_t r=opencfw_em9305_radio_record_finish_32c2b0((uintptr_t)record);uint32_t mixed=seed^0x12345678;assert(*(uint32_t *)(record+412)==mixed&&*(uint16_t *)(record+400)==(uint16_t)(mixed^(mixed>>16)));assert(record[410]==33&&record[420]==7&&*(uint16_t *)(record+422)==0);assert(*(uint32_t *)(record+416)==((uint32_t)(uint16_t)(crc>>8)<<8));if(sec){assert(phase==6&&called==c&&!memcmp(record+428,record+92,16));for(unsigned i=0;i<4;i++)assert(record[444+i]==(uint8_t)((i+3)^(mixed>>(8*i))));assert(r==(c?71:(uint32_t)(uintptr_t)(record+428)));}else assert(phase==4&&!called&&r==*(uint32_t *)(record+416));cases++;}printf("%u\n",cases);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('record-finish-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C all256 secure byte values, callback present/absent, record writes and ordered genuine children. Globals/callback pointers normalized for host; no native child/crypto/layout/hardware qualification.'},indent=2)+'\n');print('PASS',n)
