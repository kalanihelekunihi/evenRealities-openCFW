from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Native318878/3189cc'):s.index('/* Native327718..32780c')];b=b.replace('__asm__ volatile("mpyuw %0,%1,35":"=r"(product):"r"(index));','product=index*35u;')
d=(root/'g2/build/c-firmware/20261011/em-activation-round/em-inspection.bin').read_bytes();assert hashlib.sha256(d).hexdigest()=='0de6e945a56ec886a92e44d4eaefe02fbca6db11f8747876e30bffb45cffce03';tables=d[0x334c6c-0x302400:0x334cac-0x302400]
h=r'''#include <stdint.h>
#include <assert.h>
#include <string.h>
#include <stdio.h>
static uint32_t random_value;static unsigned calls;
uint32_t opencfw_em9305_pal_random_step(void){calls++;return random_value;}
'''+b+r'''
int main(void){const uint8_t native_data[64]={'''+','.join(map(str,tables))+r'''};assert(!memcmp(native_data,opencfw_em9305_access_tables_334c6c,64));unsigned n=0;for(unsigned hi=0;hi<32;hi++)for(unsigned low=0;low<4096;low++){random_value=(hi<<27)|low;calls=0;uint32_t raw=(random_value&0x017af5c0)|((low&1)?0x02040831:0x0081020e)|((uint32_t)native_data[hi]<<24&0xfd000000);assert(opencfw_em9305_radio_access_raw_318878()==raw&&calls==1);assert(opencfw_em9305_radio_access_seed_3189cc()==(raw&0xfd007fff)+((uint32_t)native_data[32+(raw>>27)]<<15)+0x800000&&calls==2);assert(opencfw_em9305_radio_crc_seed_318960()==(random_value&0xffffff)&&calls==3);n++;}
for(unsigned index=0;index<65536;index++){uint32_t p=index*35,byte=(uint8_t)(p+42),bits=((byte>>1)&1)<<23;bits+=(byte&(1<<6))?1<<24:0;bits+=(byte&(1<<5))?1<<21:0;bits+=(byte&(1<<4))?1<<20:0;bits+=(byte&(1<<3))?1<<18:0;bits+=(byte&(1<<2))?1<<17:0;uint32_t adjust=(((byte>>1)&1)<<25)-((p&1)<<26);assert(opencfw_em9305_radio_access_mix_3188b8(0xdeadbeef,index)==(0xdeadbeef^(adjust|bits)));}
for(unsigned k=0;k<65536;k++){_Alignas(4) uint8_t ch[48];memset(ch,0xa5,48);uint64_t mask=((uint64_t)k<<21)|k;memcpy(ch,&mask,8);unsigned count=0;uint8_t expected[37];for(unsigned i=0;i<37;i++)if(mask>>i&1)expected[count++]=i;opencfw_em9305_radio_channel_transform_30e3fc((uintptr_t)ch);assert(ch[45]==count&&!memcmp(ch+8,expected,count));}printf("%u\n",n);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('access-seed-receipt.json').write_text(json.dumps({'seed_cases_passed':n,'mix_cases_passed':65536,'channel_cases_passed':65536,'data_bytes_matched':64,'scope':'Actual C bounded seed/index/data and channel projection; PRNG controlled and MPYUW normalized host scalar for tested operands. No native ISA/entropy/crypto/layout/hardware qualification.'},indent=2)+'\n');print('PASS',n,65536,65536,64)
