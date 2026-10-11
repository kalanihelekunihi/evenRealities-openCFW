from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[4]
s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Native333584..3335a4'):s.index('extern uint32_t opencfw_em9305_radio_access_seed_3189cc')]
h=r'''#include <stdint.h>
#include <assert.h>
#include <string.h>
#include <stdio.h>
static unsigned phase;static uint8_t initial[16],expected[16],key_rev[16];
uint32_t opencfw_em9305_radio_request_enter_310678(void){assert(phase==0||phase==3);phase++;return 0;}
uint32_t opencfw_em9305_radio_request_exit_31069c(void){assert(phase==2||phase==6);phase++;return 0;}
uint32_t opencfw_em9305_rom_cipher_key_1009c0(uintptr_t k,uint32_t mode){assert(phase==4&&mode==0&&!memcmp((void *)k,key_rev,16));phase++;return 0;}
uint32_t opencfw_em9305_rom_cipher_block_10090c(uintptr_t i,uintptr_t o,uint32_t mode){assert(mode==0);if(phase==1){uint8_t zero[16]={0};assert(!memcmp((void *)i,zero,16));memcpy((void *)o,initial,16);}else{assert(phase==5&&!memcmp((void *)i,expected,16));for(unsigned j=0;j<16;j++)((uint8_t *)o)[j]=(uint8_t)(j+91);}phase++;return 0;}
'''+b+r'''
static void twice(uint8_t *a){unsigned high=a[0]>>7;for(unsigned i=0;i<16;i++)a[i]=(uint8_t)((a[i]<<1)|(i<15?a[i+1]>>7:0));if(high)a[15]^=0x87;}
int main(void){unsigned cases=0;uint8_t key[16],in[16],out[16],sub[16];for(unsigned k=0;k<256;k++)for(unsigned len=0;len<=16;len++){if(len>4&&len!=16)continue;for(unsigned i=0;i<16;i++){key[i]=(uint8_t)(k+i);key_rev[15-i]=key[i];in[i]=(uint8_t)(k^i);initial[i]=(uint8_t)(k+13*i);}memcpy(sub,initial,16);twice(sub);memset(expected,0,16);if(len==16){for(unsigned i=0;i<16;i++)expected[i]=in[15-i];}else{twice(sub);for(unsigned i=0;i<len;i++)expected[i]=in[3-i];expected[len]=0x80;}for(unsigned i=0;i<16;i++)expected[i]^=sub[i];phase=0;opencfw_em9305_radio_keyed_message_30fdb8((uintptr_t)key,(uintptr_t)out,(uintptr_t)in,len);assert(phase==7);for(unsigned i=0;i<16;i++)assert(out[i]==106-i);cases++;}printf("%u\n",cases);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-return-stack-address',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('keyed-message-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Actual C byte reversal, doubling/reduction, padding and ordered critical/cipher call contracts for lengths 0..4 and16, all 256 initial high-byte values. Resident cipher normalized, not crypto/native ISA/hardware qualification.'},indent=2)+'\n');print('PASS',n)
