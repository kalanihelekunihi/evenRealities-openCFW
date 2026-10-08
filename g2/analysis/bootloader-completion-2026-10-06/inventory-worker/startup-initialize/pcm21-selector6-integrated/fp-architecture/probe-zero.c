#include <stdint.h>
#define W(a) (*(volatile uint32_t *)(a))
static void host(uint32_t op,uintptr_t arg){register uint32_t r0 __asm__("r0")=op;register uintptr_t r1 __asm__("r1")=arg;__asm__ volatile("bkpt 0xab":"+r"(r0):"r"(r1):"memory");}
static void text(const char *s){host(4,(uintptr_t)s);}static void hex(uint32_t x){char s[9];for(unsigned i=0;i<8;i++)s[i]="0123456789abcdef"[(x>>(28-4*i))&15];s[8]=0;text(s);}
int main(void){W(0xe000ed88)=0xf00000;__asm__ volatile("dsb;isb");
const uint32_t modes[]={0,1u<<24,1u<<25,3u<<24,0x9f,(3u<<24)|0x9f};const uint32_t bits[]={0,0x80000000,1,0x80000001,0x7fc00000,0x7f800001,0xff800001,0x3f800000};
for(unsigned m=0;m<6;m++)for(unsigned i=0;i<8;i++){uint32_t before,after;__asm__ volatile("vmsr fpscr,%2;vmrs %0,fpscr;vmov s0,%3;vcmp.f32 s0,#0.0;vmrs %1,fpscr":"=r"(before),"=r"(after):"r"(modes[m]),"r"(bits[i]):"s0","s1","cc");hex(modes[m]);text(" ");hex(bits[i]);text(" ");hex(before);text(" ");hex(after);text("\n");}
uint32_t exit[2]={0x20026,0};host(0x20,(uintptr_t)exit);for(;;){} }
