/* Independently reconstructed C-like startup orchestration at41c4b4.
 * Child contracts at their original addresses remain explicit test cuts.
 * This is NOT linked into the promoted firmware candidate. */
#include <stdint.h>
#include "startup_initialize_leaves.h"
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
extern uint32_t child_42252e(void);
extern uint32_t child_41c17a(uint32_t);
extern uint32_t child_41c2d8(uint32_t,uint8_t *);
extern uint32_t child_41bf84(uint32_t);
extern uint32_t child_41b918(uint32_t *);
extern uint32_t child_41c320(void);
extern uint32_t child_421548(uint32_t,uint32_t,uint32_t,uint32_t *);
extern uint32_t child_41ce52(void);
extern uint32_t child_41bbd0(uint8_t *);
extern uint32_t child_41be36(const void *);
extern uint32_t child_41b8ec(void);
extern uint32_t child_41acb2(void);
__attribute__((noinline)) uint32_t reconstructed_initialize(void){
 uint32_t scratch=0;uint8_t active=0;
 if(W(0x4000885c)&2u)W(0x4000885c)&=~4u;
 if(B(0x200271a3)==0){(void)child_42252e();(void)child_41c17a(28);W(0x40020250)&=~1u;W(0x40020250)&=~14u;}
 (void)opencfw_boot_startup_sleep_fields_write(W(0x434160));W(0x4002021c)|=1;
 if(W(0x400201bc)&8u){(void)child_41c2d8(29,&active);if(!active)(void)child_41bf84(29);}
 (void)child_41b918(&scratch);(void)child_41c320();
 if(W(0x200267f8)!=0x1f01600d){
  uint32_t s=child_421548(1,0x210,1,(uint32_t *)(uintptr_t)0x2002682c);if(s)return s;
  s=child_421548(1,0x245,1,(uint32_t *)(uintptr_t)0x2002683c);if(s)return s;
 }
 (void)child_41ce52();(void)child_41c17a(23);(void)child_41c17a(29);
 if((W(0x4002000c)&255)>=34)B(0x2000009c)=1;
 (void)child_41bbd0((uint8_t *)(uintptr_t)0x2000009c);(void)child_41be36((const void *)(uintptr_t)0x434024);
 W(0x40004044)=((W(0x40004044)|0xf80000u|0x3bfc0u)&~0x4000u);W(0x40004120)=0;
 W(0x40020448)=(W(0x40020448)&~0xff00u)|0x400u;
 if(!B(0x200271a8)){
  W(0x20027060)=(W(0x4002036c)>>20)&63;W(0x20027064)=W(0x40020088)&63;
  W(0x20027068)=W(0x4002036c)>>26;W(0x2002706c)=(W(0x40020088)>>18)&63;
  W(0x2002704c)=W(0x40020044)&127;W(0x20027050)=W(0x4002004c)&127;
  W(0x20027054)=(W(0x40020374)>>29)&3;W(0x20027058)=(W(0x40020080)>>10)&15;W(0x2002705c)=W(0x40020080)&1023;
  if(((W(0x40021108)>>4)&3)==3 && (((W(0x4002000c)&255)==33&&W(0x20000098)!=0)||(W(0x4002000c)&255)>=34)){
   if(((W(0x4002000c)&255)==33&&W(0x20000098)>=3)||((W(0x4002000c)&255)==34&&W(0x20000098)==1)||((W(0x4002000c)&255)==35&&W(0x20000098)==0))W(0x2002705c)+=7;
   else if(((W(0x4002000c)&255)==33&&W(0x20000098)<3)||((W(0x4002000c)&255)==34&&W(0x20000098)==0))W(0x2002705c)+=6;
  }
  W(0x20027070)=W(0x400201b0);W(0x20027074)=(W(0x40020344)>>25)&31;W(0x20027078)=(W(0x40020344)>>11)&31;
  W(0x2002707c)=(W(0x4002034c)>>25)&31;W(0x20027080)=(W(0x4002034c)>>11)&31;
  W(0x20027084)=(W(0x40020358)>>8)&31;W(0x20027088)=(W(0x40020354)>>17)&31;B(0x200271a8)=1;
 }
 W(0x4002037c)|=0x40000000u;W(0x40020380)|=0x10000u;W(0x40020380)|=0x1000u;
 uint32_t irq=child_41b8ec();(void)opencfw_boot_startup_hook20();(void)opencfw_boot_startup_hook24(0,B(0x200271a5));
 __asm__ volatile("msr primask,%0"::"r"(irq):"memory");
 (void)opencfw_boot_startup_hook30();(void)child_41acb2();if((W(0x4002000c)&255)>=34)W(0x400211c8)|=6;
 return 0;
}
