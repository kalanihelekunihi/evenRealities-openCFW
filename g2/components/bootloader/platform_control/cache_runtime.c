/* SPDX-License-Identifier: MIT. Reconstructed stock41e348 cache maintenance.
 * Operands and loop bounds retain the private firmware implementation;
 * physical cache coherence is not established by the offline tests.
 */
#include <stdint.h>
static volatile uint32_t *mmio(uint32_t address) {
 return (volatile uint32_t *)(uintptr_t)address;
}
static void dsb(void) { __asm__ volatile("dsb sy" ::: "memory"); }
static void isb(void) { __asm__ volatile("isb sy" ::: "memory"); }
uint32_t opencfw_boot_cache_maintain(const uint32_t *range,uint32_t operation) {
 if((*mmio(0xe000ed14u)&0x10000u)==0u) {dsb();isb();return 0;}
 operation=(uint8_t)operation;
 if(range==0) {
  *mmio(0xe000ed84u)=0;dsb();uint32_t descriptor=*mmio(0xe000ed80u);
  uint32_t set=(descriptor>>13)&0x7fffu;
  for(;;) {
   uint32_t way=(descriptor>>3)&0x3ffu;
   for(;;) {
    *mmio(operation ? 0xe000ef74u : 0xe000ef60u)=((set<<5)&0x3fe0u)|(way<<30);
    if(way==0)break;--way;
   }
   if(set==0)break;--set;
  }
  dsb();isb();return 0;
 }
 uint32_t address=range[0],count=range[1];
 if((int32_t)count<1)return 0;
 count+=(address&31u);dsb();
 do { *mmio(operation ? 0xe000ef70u : 0xe000ef5cu)=address;address+=32u;count-=32u; } while((int32_t)count>=1);
 dsb();isb();return 0;
}
