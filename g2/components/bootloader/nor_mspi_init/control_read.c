/* SPDX-License-Identifier: MIT. Recoverable 4251c0 validation and requests
 * requests0..24; remaining requests explicit provider.
 */
#include <stdint.h>
extern void opencfw_hal_delay_us(uint32_t);
extern uint32_t opencfw_hal_mspi_control_remaining(uint32_t,uint32_t,void *);
static volatile uint32_t *reg(uint32_t module,uint32_t offset) {
 return (volatile uint32_t *)(uintptr_t)(0x40060000u+(module<<12)+offset);
}
static void field(uint32_t module,uint32_t offset,uint32_t shift,uint32_t bits,uint32_t value) {
 volatile uint32_t *p=reg(module,offset);uint32_t mask=((1u<<bits)-1u)<<shift;
 *p=(*p&~mask)|((value<<shift)&mask);
}
/* 42488e has no argument validation; >25 leaves the low nibble untouched. */
void opencfw_hal_mspi_pio_mixed(uint32_t address) {
 const uint8_t *h=(const uint8_t *)(uintptr_t)address;uint32_t module=*(const uint32_t *)(const void *)(h+4);uint8_t mode=h[11];
 if(mode>25u)return;
 uint32_t nibble=0u;
 if(mode>=12u && mode<=19u)nibble=1u+2u*((mode-12u)>>1);
 else if(mode>=22u)nibble=9u+2u*((mode-22u)>>1);
 field(module,4u,0u,4u,nibble);
}
uint32_t opencfw_hal_mspi_control(uint32_t address,uint32_t request,void *config) {
 uint8_t *h=(uint8_t *)(uintptr_t)address;
 if(address==0u || (*(uint32_t *)(void *)h&0x01ffffffu)!=0x01bebebeu)return 2u;
 request=(uint8_t)request;if(request>=41u)return 6u;
 if(h[8]==0u)return 7u;
 uint32_t module=*(uint32_t *)(void *)(h+4);
 if(request>24u)return opencfw_hal_mspi_control_remaining(address,request,config);
 const uint8_t *p=(const uint8_t *)config;
 if(request==4u || request==5u) {field(module,0x90u,12u,1u,request==5u);return 0u;}
 if(request==6u || request==7u) {field(module,0x9cu,31u,1u,request==7u);return 0u;}
 if(request==10u || request==11u) {field(module,0x8cu,31u,1u,request==11u);return 0u;}
 if(request==12u || request==13u) {field(module,0x88u,0u,1u,request==13u);return 0u;}
 if(request==20u) {opencfw_hal_delay_us(*(uint32_t *)(void *)(h+0x8ccu));field(module,0x90u,0u,1u,0u);return 0u;}
 if(request==21u) {field(module,0x90u,0u,1u,1u);return 0u;}
 if(request==22u || request==23u) {uint32_t big=request==22u;field(module,0u,8u,1u,big);field(module,0x90u,4u,1u,big);h[13]=(uint8_t)big;return 0u;}
 /* Stock XIP-config dereferences NULL; this is not a new safety guard. */
 if(config==0 && request!=18u)return 6u;
 switch(request) {
 case 0u:field(module,0x30u,0u,1u,p[0]);return 0u;
 case 1u: {uint32_t flags=*(const uint32_t *)config;if(flags&0x00e0e0e0u)return 6u;*reg(module,0x2b4u)=flags;return 0u;}
 case 2u: {uint32_t link=*(const uint32_t *)config;if(link>=8u)return 6u;field(module,0x30u,4u,4u,link);return 0u;}
 case 3u: {uint32_t link=*(const uint32_t *)config;if(link>=4u && link!=7u)return 6u;field(module,0x30u,4u,4u,link+8u);return 0u;}
 case 8u:field(module,0x90u,2u,2u,p[0]);return 0u;
 case 9u:field(module,0x8cu,17u,2u,p[0]);return 0u;
 case 14u:
  field(module,0x88u,2u,1u,p[0]);field(module,0x88u,3u,1u,p[1]);field(module,0x88u,4u,1u,p[2]);
  field(module,0x88u,5u,5u,p[3]);field(module,0x88u,10u,5u,p[4]);field(module,0xa8u,0u,1u,p[4]>>5);
  field(module,0x88u,15u,5u,p[5]);field(module,0xa8u,8u,1u,p[5]>>5);field(module,0x88u,20u,1u,p[6]);
  field(module,0x88u,21u,5u,p[7]);field(module,0x88u,26u,5u,p[8]);field(module,0x88u,31u,1u,p[9]);return 0u;
 case 15u:
  field(module,0x8cu,0u,4u,p[9]);field(module,0x8cu,4u,1u,p[8]);field(module,0x8cu,5u,1u,p[7]);field(module,0x8cu,7u,1u,p[6]);
  field(module,0x8cu,8u,1u,p[5]);field(module,0x8cu,9u,2u,p[4]);field(module,0x8cu,11u,1u,p[3]);field(module,0x8cu,12u,1u,p[2]);
  field(module,0x8cu,13u,1u,p[1]);field(module,0x8cu,14u,3u,p[0]);return 0u;
 case 17u: {
  volatile uint8_t *out=(volatile uint8_t *)config;
  out[0]=(uint8_t)((*reg(module,0x84u)>>24)&1u);out[1]=(uint8_t)((*reg(module,0x84u)>>23)&1u);out[2]=(uint8_t)((*reg(module,0x84u)>>22)&1u);
  out[5]=(uint8_t)((*reg(module,0x84u)>>8)&63u);out[5]=(uint8_t)((*reg(module,0x90u)>>14)&63u);
  out[3]=(uint8_t)((*reg(module,0x88u)>>5)&31u);out[4]=(uint8_t)((*reg(module,0x88u)>>10)&31u);out[4]=(uint8_t)(out[4]+((*reg(module,0xa8u)<<5)&32u));return 0u;
 }
 case 18u: {
  const uint32_t *words=(const uint32_t *)config;uint32_t base=words[2];
  if((module==0u && (base-0x60000000u)>=0x10000000u) || (module==1u && (base-0x80000000u)>=0x04000000u) ||
     (module==2u && (base-0x84000000u)>=0x04000000u) || (module==3u && (base-0x88000000u)>=0x08000000u))return 5u;
  uint32_t value=(base&0x1fff0000u)|((p[12]&1u)<<4)|(p[13]&15u);
  field(module,0x9cu,0u,13u,words[0]>>16);field(module,0x9cu,16u,13u,words[1]>>16);*reg(module,0x80u)=value;return 0u;
 }
 case 19u: {uint32_t value=((uint32_t)p[6]<<21)|((uint32_t)p[7]<<14)|((uint32_t)(p[8]&1u)<<13)|((uint32_t)p[5]<<12)|(*(const uint32_t *)config&0xfffu);*reg(module,0xa0u)=value;return 0u;}
 default:break;
 }
 if(request==0x18u) {h[11]=p[0];opencfw_hal_mspi_pio_mixed(address);return 0u;}
 field(module,0x84u,24u,1u,p[0]);field(module,0x84u,23u,1u,p[1]);field(module,0x84u,22u,1u,p[2]);
 field(module,0x84u,8u,6u,p[5]);field(module,0x90u,14u,6u,p[5]);
 field(module,0x88u,5u,5u,p[3]);field(module,0x88u,10u,5u,p[4]);field(module,0xa8u,0u,1u,p[4]>>5);
 return 0u;
}
