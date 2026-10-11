from pathlib import Path
import subprocess,tempfile,json
root=Path(__file__).resolve().parents[4];s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();body=s[s.index('/* Native30c72c/30c7d0'):s.index('/* Native331868..33194c')]
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
static uint8_t input[6],output[6];static unsigned kind,identity,found,packs,lookups,writes;
uint64_t opencfw_em9305_controller_pack_address(uintptr_t p){assert(p==(uintptr_t)input);packs++;return 0x123456789abcdef0ULL;}
static uint32_t lookup(uint32_t k,uint32_t low,uint32_t high,uintptr_t out){assert(k==kind&&low==0x9abcdef0&&high==0x12345678&&packs==1);uint32_t *pair=(uint32_t*)out;assert(pair[0]==0&&pair[1]==0);pair[0]=0x12345678;pair[1]=0xabcdef00;lookups++;return found;}
uint32_t opencfw_em9305_radio_identity_pair_303a60(uint32_t k,uint32_t l,uint32_t h,uintptr_t o){assert(identity);return lookup(k,l,h,o);}
uint32_t opencfw_em9305_radio_peer_pair_303a40(uint32_t k,uint32_t l,uint32_t h,uintptr_t o){assert(!identity);return lookup(k,l,h,o);}
uintptr_t opencfw_em9305_radio_address_write_3045e8(uintptr_t o,uint32_t l,uint32_t h){assert(o==(uintptr_t)output&&l==0x12345678&&h==0xabcdef00&&lookups==1);writes++;return o;}
'''+body+r'''
int main(void){unsigned n=0;for(kind=0;kind<256;kind++)for(identity=0;identity<2;identity++)for(unsigned f=0;f<3;f++){found=f==2?0xffffffffu:f;packs=lookups=writes=0;unsigned status=kind>1?18:found?0:2;uint32_t got=identity?opencfw_em9305_link_address_30c7d0(kind,(uintptr_t)input,(uintptr_t)output):opencfw_em9305_link_address_30c72c(kind,(uintptr_t)input,(uintptr_t)output);assert(got==status&&packs==(kind<=1)&&lookups==packs&&writes==(status==0));n++;}printf("%u\n",n);}
'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(h);subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True);n=int(subprocess.check_output([str(p/'test')],text=True))
Path(__file__).with_name('address-provider-receipt.json').write_text(json.dumps({'cases_passed':n,'scope':'Two actual C providers, all selector bytes, fullword lookup outcomes, scratch init and ordered genuine child contracts. Normalized children; nativeISA/hardware unproved.'},indent=2)+'\n');print('PASS',n)
