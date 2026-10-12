from pathlib import Path
import subprocess,json
root=Path(__file__).resolve().parents[4]
s=(root/'g2/components/em9305/qpc_scheduler_candidate/controller_init.c').read_text();b=s[s.index('/* Authenticated key-match315640'):s.index('/* Authenticated packet validation303404')]
h=r'''#include <stdint.h>
#include <assert.h>
#include <stdio.h>
static unsigned expectedchallenge,result;
uint32_t opencfw_em9305_radio_hash24_314640(uintptr_t p,uint32_t c){assert(p==0x810000&&c==expectedchallenge);return result;}
'''+b+r'''
int main(void){unsigned cases=0;for(unsigned upper=0;upper<256;upper++)for(unsigned lower=0;lower<256;lower++)for(unsigned match=0;match<2;match++){uint32_t low=(upper<<24)|0x123456;uint32_t high=0xa5b60000|lower;expectedchallenge=(lower<<8)|upper;result=match?0x123456:0x123457;assert(opencfw_em9305_radio_key_match_315640(0x810000,low,high)==match);cases++;}result=0xff123456;expectedchallenge=0;assert(opencfw_em9305_radio_key_match_315640(0x810000,0x123456,0)==0);cases++;printf("PASS %u\n",cases);}
'''
p=Path(__file__).with_name('key-match-host.c');p.write_text(h)
out=subprocess.check_output(['docker','run','--rm','-v',str(root)+':/work','opencfw/qemu-csky-builddeps:20261009t201800','sh','-c','gcc -std=c11 -O2 -Wall -Wextra -Werror /work/'+str(p.relative_to(root))+' -o /tmp/test && /tmp/test'],text=True)
print(out.strip());p.with_name('key-match-host-receipt.json').write_text(json.dumps({'result':out.strip(),'scope':'Selected key-match wrapper with controlled hash result/challenge assertion; native six-byte address split, discarded upper input bits and full-word output comparison. Cipher/ROM/runtime/hardware not proved.'},indent=2)+'\n')
