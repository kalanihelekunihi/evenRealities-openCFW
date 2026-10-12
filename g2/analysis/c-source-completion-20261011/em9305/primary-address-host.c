#define _GNU_SOURCE
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned found,called,mode,packed;
static uint64_t opencfw_em9305_ll_pack64_304648(uintptr_t p){if(p!=99)abort();return UINT64_C(0x9876543212345678);}
static uint64_t opencfw_em9305_controller_pack_address(uintptr_t p){if(p!=99)abort();packed++;return UINT64_C(0x987612345678);}
static uint32_t opencfw_em9305_radio_address_reset_303e38(void){called++;return 77;}
static uint32_t opencfw_em9305_radio_address_enable_303dec(void){mode=1;return 88;}
static uint32_t opencfw_em9305_radio_address_disable_303ec0(void){mode=2;return 88;}
static uint32_t opencfw_em9305_radio_address_add_303da4(uint32_t k,uint32_t l,uint32_t h){called++;if(l!=0x12345678||h!=0x9876||k>1)abort();return found;}
static uint32_t opencfw_em9305_radio_address_remove_303e68(uint32_t k,uint32_t l,uint32_t h){return opencfw_em9305_radio_address_add_303da4(k,l,h);}
/* Native332b60..332b6e: retain low-word R0 after eight-byte packing. */
uint32_t opencfw_em9305_primary_masks_332b60(uintptr_t destination,uintptr_t input)
{
 uint64_t bits=opencfw_em9305_ll_pack64_304648(input);
 *(volatile uint32_t *)(destination+4u)=(uint32_t)(bits>>32u);
 *(volatile uint32_t *)destination=(uint32_t)bits;
 return (uint32_t)bits;
}
/* Native30b190..30b1a8: argument dead, busy latch before reset. */
uint32_t opencfw_em9305_command_primary_30b190(uint32_t ignored)
{
 (void)ignored;
 if(*(volatile uint8_t *)(uintptr_t)0x805a76u!=0u)return 12u;
 (void)opencfw_em9305_radio_address_reset_303e38();
 return 0u;
}
/* Native30af98..30aff4 and30cac4..30cb20: fullword initial kind check,
 * wrapped-byte second check and exact special 255 mode branch. */
static uint32_t opencfw_em9305_primary_address_gate(uint32_t kind)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t version=*(volatile uint8_t *)(config+4u);
 if(kind>=2u&&version<9u)return 18u;
 if((uint8_t)(kind+1u)>=3u&&version>=9u)return 18u;
 if(*(volatile uint8_t *)(uintptr_t)0x805a76u!=0u)return 12u;
 return 0u;
}
uint32_t opencfw_em9305_command_primary_30af98(uint32_t kind,uintptr_t input)
{
 uint32_t error=opencfw_em9305_primary_address_gate(kind);
 if(error!=0u)return error;
 if(kind==255u){(void)opencfw_em9305_radio_address_enable_303dec();return 0u;}
 uint64_t address=opencfw_em9305_controller_pack_address(input);
 uint32_t result=opencfw_em9305_radio_address_add_303da4(kind!=0u,(uint32_t)address,(uint32_t)(address>>32u));
 return result==0u?7u:0u;
}
uint32_t opencfw_em9305_command_primary_30cac4(uint32_t kind,uintptr_t input)
{
 uint32_t error=opencfw_em9305_primary_address_gate(kind);
 if(error!=0u)return error;
 if(kind==255u){(void)opencfw_em9305_radio_address_disable_303ec0();return 0u;}
 uint64_t address=opencfw_em9305_controller_pack_address(input);
 uint32_t result=opencfw_em9305_radio_address_remove_303e68(kind!=0u,(uint32_t)address,(uint32_t)(address>>32u));
 return result==0u?18u:0u;
}
int main(void){if(mmap((void*)0x800000,0x10000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;*(uint32_t*)0x805cac=0x80f000;unsigned n=0;for(unsigned k=0;k<65536;k++)for(unsigned v=0;v<16;v++)for(unsigned busy=0;busy<2;busy++)for(found=0;found<2;found++){*(uint8_t*)0x80f004=v;*(uint8_t*)0x805a76=busy;unsigned e=(k>=2&&v<9)||((uint8_t)(k+1)>=3&&v>=9)?18:busy?12:0;for(unsigned rem=0;rem<2;rem++){called=mode=packed=0;unsigned expect=e?e:k==255?0:found?0:rem?18:7;unsigned got=rem?opencfw_em9305_command_primary_30cac4(k,99):opencfw_em9305_command_primary_30af98(k,99);if(got!=expect||called!=(!e&&k!=255)||packed!=called||mode!=(!e&&k==255?rem+1:0))abort();n++;}}uint32_t dest[4]={1,2,3,4};if(opencfw_em9305_primary_masks_332b60((uintptr_t)(dest+1),99)!=0x12345678||dest[0]!=1||dest[1]!=0x12345678||dest[2]!=0x98765432||dest[3]!=4)abort();n++;for(unsigned b=0;b<256;b++){*(uint8_t*)0x805a76=b;called=0;if(opencfw_em9305_command_primary_30b190(0x12345678)!=(b?12:0)||called!=!b)abort();n++;}printf("PASS %u address/mask fixtures\n",n);}
