from pathlib import Path
import subprocess,tempfile,json,hashlib
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Native31737c..3173ac'):s.index('/* Native333584..3335a4')]
d=(root/'g2/build/c-firmware/20261011/em-activation-round/em-inspection.bin').read_bytes();assert hashlib.sha256(d).hexdigest()=='0de6e945a56ec886a92e44d4eaefe02fbca6db11f8747876e30bffb45cffce03';v=list(d[0x334b80-0x302400:0x334b98-0x302400])
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint8_t key[16],input[16],output[16];static uintptr_t scratch;static unsigned calls;
uint32_t opencfw_em9305_radio_keyed_message_30fdb8(uintptr_t k,uintptr_t o,uintptr_t i,uint32_t len);
'''+b+r'''
uint32_t opencfw_em9305_radio_keyed_message_30fdb8(uintptr_t k,uintptr_t o,uintptr_t i,uint32_t len){
 if(calls==0){assert(k==(uintptr_t)opencfw_em9305_seed_constants_334b80&&i==(uintptr_t)input&&len==16);scratch=o-32;}
 if(calls==1){assert(k==scratch+32&&o==scratch+16&&i==(uintptr_t)(opencfw_em9305_seed_constants_334b80+16)&&len==4);for(unsigned j=0;j<16;j++)assert(((uint8_t *)k)[j]==1);}
 if(calls==2){assert(k==(uintptr_t)key&&o==scratch&&i==scratch+16&&len==16);for(unsigned j=0;j<16;j++)assert(((uint8_t *)i)[j]==2);}
 if(calls==3){assert(k==scratch&&o==(uintptr_t)output&&i==(uintptr_t)(opencfw_em9305_seed_constants_334b80+20)&&len==4);for(unsigned j=0;j<16;j++)assert(((uint8_t *)k)[j]==3);}
 calls++;memset((void *)o,calls,16);return 99;
}
int main(void){unsigned n=0;for(unsigned phy=0;phy<256;phy++)for(unsigned length=0;length<4096;length++)for(unsigned e=0;e<2;e++){uint32_t l=length+(e?4:0);uint32_t expected=phy==2?44+4*l:phy==3?720+64*l:80+8*l;assert(opencfw_em9305_radio_phy_duration_31737c(phy,length,e?0xffffffff:0)==expected);n++;}
const uint8_t expected[24]={'''+','.join(map(str,v))+r'''};assert(!memcmp(expected,opencfw_em9305_seed_constants_334b80,24));calls=0;opencfw_em9305_radio_encrypt_seed_317334((uintptr_t)key,(uintptr_t)input,(uintptr_t)output);assert(calls==4&&output[0]==4);printf("%u\n",n);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('duration-seed-receipt.json').write_text(json.dumps({'duration_cases_passed':n,'seed_ordered_calls_passed':4,'authenticated_data_bytes_matched':24,'scope':'Actual C PHY/length0..4095/fullword nonzero encrypted state and ordered scratch-buffer chain; keyedmessage child normalized. No cryptographic/nativeISA/placement/hardware proof.'},indent=2)+'\n');print('PASS',n,'SEED',4,'DATA',24)
