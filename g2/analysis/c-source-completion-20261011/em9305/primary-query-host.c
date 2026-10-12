#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
static uint8_t out[32];
uint32_t opencfw_em9305_ll_signed_bounds_31026c(uintptr_t lower,uintptr_t upper)
{
 uint32_t low=*(volatile uint8_t *)(uintptr_t)0x8012b9u;
 uint32_t high=*(volatile uint8_t *)(uintptr_t)0x8012b8u;
 *(volatile uint8_t *)lower=(uint8_t)low;
 *(volatile uint8_t *)upper=(uint8_t)high;
 return (uint32_t)lower;
}
uintptr_t opencfw_em9305_radio_address_write_3045e8(uintptr_t output,uint32_t low,uint32_t high)
{
 *(volatile uint8_t *)(output+4u)=(uint8_t)high;
 *(volatile uint8_t *)output=(uint8_t)low;
 *(volatile uint8_t *)(output+5u)=(uint8_t)(high>>8u);
 *(volatile uint8_t *)(output+3u)=(uint8_t)(low>>24u);
 *(volatile uint8_t *)(output+2u)=(uint8_t)(low>>16u);
 *(volatile uint8_t *)(output+1u)=(uint8_t)(low>>8u);
 return output;
}
uint32_t opencfw_em9305_radio_address_status_303e50(void)
{ return *(volatile uint8_t *)(uintptr_t)0x80163bu; }
/* Native313960..313988: full eight-byte serialization; exact store order
 * 4,0,7,6,5,3,2,1 and original destination in R0. */
uint32_t opencfw_em9305_primary_query_313960(uintptr_t output,uint32_t low,uint32_t high)
{
 *(volatile uint8_t *)(output+4u)=(uint8_t)high;
 *(volatile uint8_t *)output=(uint8_t)low;
 *(volatile uint8_t *)(output+7u)=(uint8_t)(high>>24u);
 *(volatile uint8_t *)(output+6u)=(uint8_t)(high>>16u);
 *(volatile uint8_t *)(output+5u)=(uint8_t)(high>>8u);
 *(volatile uint8_t *)(output+3u)=(uint8_t)(low>>24u);
 *(volatile uint8_t *)(output+2u)=(uint8_t)(low>>16u);
 *(volatile uint8_t *)(output+1u)=(uint8_t)(low>>8u);
 return (uint32_t)output;
}
/* Native30bf04..30bf1c: fields captured before output; second config pointer fresh. */
uint32_t opencfw_em9305_primary_query_30bf04(uintptr_t first,uintptr_t version,uintptr_t second)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t first_value=*(volatile uint16_t *)config;
 uint32_t version_value=*(volatile uint8_t *)(config+4u);
 *(volatile uint16_t *)first=(uint16_t)first_value;
 *(volatile uint8_t *)version=(uint8_t)version_value;
 config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t second_value=*(volatile uint16_t *)(config+2u);
 *(volatile uint16_t *)second=(uint16_t)second_value;
 return second_value;
}
/* Native30c92c tail31026c; selected complete child retains output pointer R0. */
uint32_t opencfw_em9305_primary_query_30c92c(uintptr_t lower,uintptr_t upper)
{return opencfw_em9305_ll_signed_bounds_31026c(lower,upper);}
/* Native30bb74..30bb80: high-word before low-word, selected six-byte serializer. */
uint32_t opencfw_em9305_primary_query_30bb74(uintptr_t output)
{
 uint32_t high=*(volatile uint32_t *)(uintptr_t)0x805b44u;
 uint32_t low=*(volatile uint32_t *)(uintptr_t)0x805b40u;
 return (uint32_t)opencfw_em9305_radio_address_write_3045e8(output,low,high);
}
/* Native30bdb4..30bdc0: high-word before low-word, full serializer tail. */
uint32_t opencfw_em9305_primary_query_30bdb4(uintptr_t output)
{
 uint32_t high=*(volatile uint32_t *)(uintptr_t)0x805a98u;
 uint32_t low=*(volatile uint32_t *)(uintptr_t)0x805a94u;
 return opencfw_em9305_primary_query_313960(output,low,high);
}
/* Native30bf20 tail303e50; incoming R0 unused by actual child. */
uint32_t opencfw_em9305_primary_query_30bf20(uint32_t ignored)
{(void)ignored;return opencfw_em9305_radio_address_status_303e50();}
/* Native30bea4..30beb0: high-word first, full serializer tail. */
uint32_t opencfw_em9305_primary_query_30bea4(uintptr_t output)
{
 uint32_t high=*(volatile uint32_t *)(uintptr_t)0x805b4cu;
 uint32_t low=*(volatile uint32_t *)(uintptr_t)0x805b48u;
 return opencfw_em9305_primary_query_313960(output,low,high);
}
/* Native310328..31033c: first halfword written before second read. */
uint32_t opencfw_em9305_primary_controls_310328(uintptr_t first,uintptr_t second)
{
 uint32_t first_value=*(volatile uint16_t *)(uintptr_t)0x8012eeu;
 *(volatile uint16_t *)first=(uint16_t)first_value;
 uint32_t second_value=*(volatile uint16_t *)(uintptr_t)0x8012ecu;
 *(volatile uint16_t *)second=(uint16_t)second_value;
 return second_value;
}
uint32_t opencfw_em9305_primary_query_30c928(uintptr_t first,uintptr_t second)
{return opencfw_em9305_primary_controls_310328(first,second);}
int main(void){if(mmap((void*)0x800000,0x10000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;unsigned n=0;for(unsigned v=0;v<65536;v++){uint32_t low=0x12340000|v,high=~low;for(unsigned k=0;k<4;k++){memset(out,0xa5,32);uint32_t r;if(k==0)r=opencfw_em9305_primary_query_313960((uintptr_t)(out+4),low,high);else{uintptr_t root=k==1?0x805a94:k==2?0x805b48:0x805b40;*(uint32_t*)root=low;*(uint32_t*)(root+4)=high;r=k==1?opencfw_em9305_primary_query_30bdb4((uintptr_t)(out+4)):k==2?opencfw_em9305_primary_query_30bea4((uintptr_t)(out+4)):opencfw_em9305_primary_query_30bb74((uintptr_t)(out+4));}uint8_t expected[32];memset(expected,0xa5,32);memcpy(expected+4,&low,4);memcpy(expected+8,&high,k==3?2:4);if(r!=(uint32_t)(uintptr_t)(out+4)||memcmp(out,expected,32))abort();n++;}
*(uint32_t*)0x805cac=0x80f000;*(uint16_t*)0x80f000=v;*(uint16_t*)0x80f002=~v;*(uint8_t*)0x80f004=v>>8;memset(out,0xa5,32);if(opencfw_em9305_primary_query_30bf04((uintptr_t)(out+2),(uintptr_t)(out+6),(uintptr_t)(out+8))!=(uint16_t)~v||*(uint16_t*)(out+2)!=v||out[6]!=(v>>8)||*(uint16_t*)(out+8)!=(uint16_t)~v||out[4]!=0xa5||out[7]!=0xa5)abort();n++;
*(uint16_t*)0x8012ee=v;*(uint16_t*)0x8012ec=~v;memset(out,0xa5,32);if(opencfw_em9305_primary_query_30c928((uintptr_t)(out+2),(uintptr_t)(out+8))!=(uint16_t)~v||*(uint16_t*)(out+2)!=v||*(uint16_t*)(out+8)!=(uint16_t)~v||out[4]!=0xa5||out[10]!=0xa5)abort();n++;
*(uint8_t*)0x8012b9=v;*(uint8_t*)0x8012b8=v>>8;memset(out,0xa5,32);if(opencfw_em9305_primary_query_30c92c((uintptr_t)(out+2),(uintptr_t)(out+8))!=(uint32_t)(uintptr_t)(out+2)||out[2]!=(uint8_t)v||out[8]!=(v>>8)||out[3]!=0xa5||out[9]!=0xa5)abort();n++;
*(uint8_t*)0x80163b=v;if(opencfw_em9305_primary_query_30bf20(0xffffffff)!=(uint8_t)v)abort();n++;}
*(uint32_t*)0x805cac=0x80f000;*(uint16_t*)0x80f000=0xf020;*(uint8_t*)0x80f004=77;*(uint16_t*)0x80f022=0x123;memset(out,0xa5,32);if(opencfw_em9305_primary_query_30bf04(0x805cac,(uintptr_t)(out+4),(uintptr_t)(out+8))!=0x123||*(uint32_t*)0x805cac!=0x80f020||out[4]!=77||*(uint16_t*)(out+8)!=0x123)abort();n++;
*(uint16_t*)0x8012ee=0x1234;*(uint16_t*)0x8012ec=0xabcd;if(opencfw_em9305_primary_query_30c928(0x8012ec,(uintptr_t)(out+8))!=0x1234||*(uint16_t*)(out+8)!=0x1234)abort();n++;
*(uint8_t*)0x8012b9=7;*(uint8_t*)0x8012b8=9;opencfw_em9305_primary_query_30c92c(0x8012b8,(uintptr_t)(out+8));if(*(uint8_t*)0x8012b8!=7||out[8]!=9)abort();n++;printf("PASS %u query fixtures\n",n);}
