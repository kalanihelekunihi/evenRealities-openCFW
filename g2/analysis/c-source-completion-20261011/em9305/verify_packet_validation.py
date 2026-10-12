from pathlib import Path
import subprocess,json
root=Path(__file__).resolve().parents[4]
s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Authenticated packet validation303404'):s.index('/* Authenticated address projection303b7c')];pack=s[s.index('uint64_t opencfw_em9305_controller_pack_address('):s.index('uint32_t opencfw_em9305_controller_set_address(',s.index('uint64_t opencfw_em9305_controller_pack_address('))]
h=r'''#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned classification,match,mode,peer_kind,associate,projects,associations;
uint32_t opencfw_em9305_radio_classify_314470(uint32_t a,uint32_t r,uintptr_t k,uintptr_t d){assert(a==0&&r<=1&&k==0x820013&&d==0x820008);return classification;}
uint32_t opencfw_em9305_radio_address_mode_303e5c(void){return mode;}
uint32_t opencfw_em9305_radio_address_match_303df8(uint32_t k,uint32_t l,uint32_t h){assert(k==0&&l==500&&h==600);return match;}
uint32_t opencfw_em9305_radio_peer_kind_3039f0(uint32_t k,uint32_t l,uint32_t h){assert(k==0&&l==500&&h==600);return peer_kind;}
uint32_t opencfw_em9305_radio_address_project_303b7c(uint32_t l,uint32_t h,uintptr_t k,uintptr_t p){assert(l==0x80&&h==0x4000);projects++;*(uint8_t *)k=9;*(uint32_t *)p=700;*(uint32_t *)(p+4)=800;return 0;}
uint32_t opencfw_em9305_radio_address_associate_303844(uint32_t l,uint32_t h,uint32_t k,uint32_t a,uint32_t b){assert(l==0x80&&h==0x4000&&k==9&&a==700&&b==800);associations++;return associate;}
'''+pack+b+r'''
static void reset(unsigned type,unsigned allowed,unsigned flags){memset((void *)0x800000,0,0x100000);classification=2;match=1;mode=peer_kind=associate=projects=associations=0;*(uint8_t *)0x810000=type;*(uint8_t *)0x810001=63;*(uint32_t *)0x810002=500;*(uint16_t *)0x810006=600;*(uint16_t *)0x811000=allowed?1u<<type:0;*(uint32_t *)0x811004=flags;}
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;for(unsigned type=0;type<16;type++)for(unsigned allowed=0;allowed<2;allowed++)for(classification=0;classification<5;classification++)for(unsigned filter=0;filter<2;filter++)for(match=0;match<2;match++){unsigned c=classification,m=match;reset(type,allowed,0);classification=c;match=m;*(uint16_t *)0x811002=filter?1u<<type:0;unsigned r=opencfw_em9305_radio_packet_check_303404(0x810000,0x811000,0,0x820000);unsigned expected=!allowed?0:(type>=7&&type<=9)?1:(c==1||c==3)?0:filter&&!m&&c==2?0:1;assert(r==expected);if(allowed&&!(type>=7&&type<=9)&&c!=1&&c!=3&&expected){assert(*(uint8_t *)0x820010==type&&*(uint8_t *)0x820011==63&&*(uint32_t *)0x820000==500&&*(uint32_t *)0x820004==600&&*(uint8_t *)0x820015==1);}cases++;}
reset(9,0,128);assert(opencfw_em9305_radio_packet_check_303404(0x810000,0x811000,0,0x820000)==1);cases++;
for(unsigned c=0;c<3;c+=2)for(unsigned same=0;same<2;same++){reset(0,1,4);classification=c;*(uint32_t *)0x811010=same?500:501;*(uint32_t *)0x811014=600;unsigned r=opencfw_em9305_radio_packet_check_303404(0x810000,0x811000,0,0x820000);assert(r==(same||c==0));if(r)assert(*(uint8_t *)0x820014==(same?1:0));cases++;}
for(unsigned type=1;type<6;type+=2)for(unsigned random=0;random<2;random++)for(unsigned permit=0;permit<2;permit++){reset(type,1,1|(permit?32:0));*(uint8_t *)0x810000=type|(random?128:0);*(uint8_t *)0x810008=0x80;*(uint16_t *)0x81000c=0x4000;assert(opencfw_em9305_radio_packet_check_303404(0x810000,0x811000,0,0x820000)==(random&&permit));if(random&&permit)assert(*(uint8_t *)0x820015==0);cases++;}
reset(1,1,1);*(uint32_t *)0x811008=0;*(uint32_t *)0x81100c=0;assert(opencfw_em9305_radio_packet_check_303404(0x810000,0x811000,0,0x820000)==1);cases++;
for(unsigned a=0;a<2;a++){reset(1,1,16);*(uint8_t *)0x810000=129;*(uint8_t *)0x810008=0x80;*(uint16_t *)0x81000c=0x4000;associate=a;assert(opencfw_em9305_radio_packet_check_303404(0x810000,0x811000,1,0x820000)==1&&projects==1&&associations==1);cases++;}
reset(1,1,16);peer_kind=2;assert(opencfw_em9305_radio_packet_check_303404(0x810000,0x811000,0,0x820000)==0);cases++;printf("PASS %u\n",cases);}
'''
p=Path(__file__).with_name('packet-validation-host.c');p.write_text(h)
out=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror -fno-strict-aliasing -no-pie /work/'+str(p.relative_to(root))+' -o /tmp/test && /tmp/test'],text=True)
print(out.strip());p.with_name('packet-validation-host-receipt.json').write_text(json.dumps({'result':out.strip(),'scope':'Selected full packet check plus real address-byte pack; controlled classification/match/project/associate children. Native policy/classification decision cuts, descriptor cursor, peer random/identity filters and output status; not native ARC execution/layout/hardware proof.'},indent=2)+'\n')
