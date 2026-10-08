#include <stdint.h>
#define W(a) (*(volatile uint32_t *)(a))
extern uint32_t event_a_temperature_classify_bits(uint32_t);
static void host(uint32_t op,uintptr_t arg){register uint32_t r0 __asm__("r0")=op;register uintptr_t r1 __asm__("r1")=arg;__asm__ volatile("bkpt 0xab":"+r"(r0):"r"(r1):"memory");}
static void text(const char *s){host(4,(uintptr_t)s);}static void hex(uint32_t x){char s[9];for(unsigned i=0;i<8;i++)s[i]="0123456789abcdef"[(x>>(28-4*i))&15];s[8]=0;text(s);}
static uint32_t stock(uint32_t bits){uint32_t result;__asm__ volatile("vmov s0,%1;bl stock_classifier;mov %0,r0":"=r"(result):"r"(bits):"r0","r1","r2","r3","r12","lr","s0","s1","s2","s3","memory","cc");return result;}
static void set(uint32_t m){__asm__ volatile("vmsr fpscr,%0"::"r"(m):"memory");}static uint32_t get(void){uint32_t r;__asm__ volatile("vmrs %0,fpscr":"=r"(r));return r;}
int main(void){W(0xe000ed88)=0xf00000;__asm__ volatile("dsb;isb");
const uint32_t modes[]={0,1u<<24,1u<<25,3u<<24,0x9f,(3u<<24)|0x9f,0x40000,0x1040000,0x8040000,0x00c4009f};const uint32_t bits[]={0,0x80000000,1,0x80000001,0x007fffff,0x807fffff,0x00800000,0x80800000,0x7f800000,0xff800000,0x7fc00000,0xffc00000,0x7f800001,0xff800001,0x7fffffff,0xffffffff,0xc3888001,0xc3888000,0xc3887fff,0xc1a00001,0xc1a00000,0xc19fffff,0x4247ffff,0x42480000,0x42480001,0x4479ffff,0x447a0000,0x447a0001,0x7f9800b9};
for(unsigned m=0;m<10;m++)for(unsigned i=0;i<29;i++){set(modes[m]);uint32_t before=get();uint32_t a=stock(bits[i]);uint32_t af=get();set(modes[m]);uint32_t b=event_a_temperature_classify_bits(bits[i]);uint32_t bf=get();hex(modes[m]);text(" ");hex(bits[i]);text(" ");hex(before);text(" ");hex(a);text(" ");hex(b);text(" ");hex(af);text(" ");hex(bf);text("\n");}
uint32_t exit[2]={0x20026,0};host(0x20,(uintptr_t)exit);for(;;){} }
