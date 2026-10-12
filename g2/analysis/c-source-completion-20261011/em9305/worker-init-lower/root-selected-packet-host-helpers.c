#include <stdint.h>
uint64_t opencfw_em9305_controller_pack_address(uintptr_t address)
{
 volatile uint8_t *bytes=(volatile uint8_t *)address;
 uint32_t second=bytes[1],third=bytes[2],first=bytes[0];
 uint32_t sixth=bytes[5],fourth=bytes[3],fifth=bytes[4];
 uint32_t low=first|(second<<8)|(third<<16)|(fourth<<24);
 uint32_t high=fifth|(sixth<<8);
 return ((uint64_t)high<<32)|low;
}
uint64_t opencfw_em9305_ll_pack64_304648(uintptr_t input)
{
 volatile uint8_t *p=(volatile uint8_t *)input;
 uint32_t b1=p[1],b5=p[5],b2=p[2],b3=p[3];
 uint32_t b6=p[6],b7=p[7],b0=p[0],b4=p[4];
 uint32_t low=b0|(b1<<8u)|(b2<<16u)|(b3<<24u);
 uint32_t high=b4|(b5<<8u)|(b6<<16u)|(b7<<24u);
 return ((uint64_t)high<<32u)|low;
}
uint32_t opencfw_em9305_short_header_decode_32dedc(uintptr_t output,uintptr_t input)
{
 uint32_t b1=*(volatile uint8_t *)(input+1u);
 uint32_t b0=*(volatile uint8_t *)input;
 uint32_t packed=b0+(b1<<8),low=(uint8_t)packed;
 *(volatile uint8_t *)(output+5u)=(uint8_t)b1;
 *(volatile uint8_t *)output=(uint8_t)(packed&3u);
 uint32_t flag=(low>>5)&1u;
 *(volatile uint8_t *)(output+4u)=(uint8_t)flag;
 *(volatile uint8_t *)(output+3u)=(uint8_t)((low>>4)&1u);
 *(volatile uint8_t *)(output+2u)=(uint8_t)((low>>3)&1u);
 *(volatile uint8_t *)(output+1u)=(uint8_t)((low>>2)&1u);
 if(flag!=0u){
  uint32_t extra=*(volatile uint8_t *)(input+2u);
  *(volatile uint8_t *)(output+6u)=(uint8_t)(extra>>6);
  *(volatile uint8_t *)(output+7u)=(uint8_t)(extra&31u);
  return 3u;
 }
 return 2u;
}
