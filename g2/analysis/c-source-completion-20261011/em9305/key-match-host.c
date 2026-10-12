#include <stdint.h>
#include <assert.h>
#include <stdio.h>
static unsigned expectedchallenge,result;
uint32_t opencfw_em9305_radio_hash24_314640(uintptr_t p,uint32_t c){assert(p==0x810000&&c==expectedchallenge);return result;}
/* Authenticated key-match315640..315658: split six-byte address into
 * low24-bit comparison and high24-bit cipher challenge. */
uint32_t opencfw_em9305_radio_key_match_315640(uintptr_t key,uint32_t low,uint32_t high)
{
 uint32_t expected=low&0xffffffu;
 uint32_t challenge=((low>>24u)|(high<<8u))&0xffffffu;
 uint32_t actual=opencfw_em9305_radio_hash24_314640(key,challenge);
 return expected==actual;
}


int main(void){unsigned cases=0;for(unsigned upper=0;upper<256;upper++)for(unsigned lower=0;lower<256;lower++)for(unsigned match=0;match<2;match++){uint32_t low=(upper<<24)|0x123456;uint32_t high=0xa5b60000|lower;expectedchallenge=(lower<<8)|upper;result=match?0x123456:0x123457;assert(opencfw_em9305_radio_key_match_315640(0x810000,low,high)==match);cases++;}result=0xff123456;expectedchallenge=0;assert(opencfw_em9305_radio_key_match_315640(0x810000,0x123456,0)==0);cases++;printf("PASS %u\n",cases);}
