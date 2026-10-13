#include <stdint.h>
extern int32_t audio_uart_lv_clamp_width_4408d6(int32_t,int32_t,int32_t,int32_t);
extern int32_t audio_uart_lv_clamp_height_440968(int32_t,int32_t,int32_t,int32_t);
static uint32_t count;
static void host(uint32_t op,uintptr_t p){register uint32_t r0 __asm__("r0")=op;register uintptr_t r1 __asm__("r1")=p;__asm__ volatile("bkpt 0xab":"+r"(r0),"+r"(r1)::"memory");}
static void hex(uint32_t v){char s[10];for(int i=0;i<8;i++)s[i]="0123456789abcdef"[(v>>(28-i*4))&15];s[8]='\n';s[9]=0;host(4,(uintptr_t)s);}
void fault_handler(void){host(4,(uintptr_t)"FAULT\n");uint32_t p[2]={0x20026,1};host(0x20,(uintptr_t)p);for(;;){}}
extern void call_probe(uint32_t,int32_t,int32_t,int32_t,int32_t);
static volatile uint32_t *const output=(void*)0x20015000;
static const uint32_t seeds[]={0x4444,0x5555,0x6666,0x7777,0x8888,0x9999,0xaaaa,0xbbbb};
static void check(uint32_t fn,uint32_t a,uint32_t b,uint32_t c,uint32_t ref){call_probe(fn,a,b,c,ref);for(uint32_t i=0;i<8;i++)if(output[1+i]!=seeds[i]){host(4,(uintptr_t)"FAIL_REG\n");fault_handler();}if(output[9]!=output[10]){host(4,(uintptr_t)"FAIL_SP\n");fault_handler();}}
static void test(uint32_t k,uint32_t a,uint32_t b,uint32_t c,uint32_t ref){check(k?0x28108969:0x281088d7,a,b,c,ref);uint32_t expected=output[0];check((uint32_t)(k?audio_uart_lv_clamp_height_440968:audio_uart_lv_clamp_width_4408d6),a,b,c,ref);if(expected!=output[0]){host(4,(uintptr_t)"FAIL_VALUE\n");hex(k);hex(a);hex(b);hex(c);hex(ref);hex(expected);hex(output[0]);fault_handler();}count++;}
static const uint32_t values[]={0,1,99,100,0x7fffffff,0x80000000,0xffffffff,0x1ffffffe,0x1fffffff,0x20000000,0x20000001,0x2fffffff,0x30000000,0x3ffffffe,0x3fffffff,0xa0000000};
static const uint32_t bounds[]={0,1,0xffffffff,0x7fffffff,0x80000000,0x1ffffffe,0x1fffffff,0x20000001,0x2fffffff,0x30000000,0xa0000001,0xbffffffe};
static const uint32_t refs[]={0,1,100,0xffffffff,0x80000000,0x7fffffff,0x12345678,0x87654321};
static uint32_t rng=319;static uint32_t next(void){rng^=rng<<13;rng^=rng>>17;rng^=rng<<5;return rng;}
int main(void){for(uint32_t k=0;k<2;k++){for(uint32_t i=0;i<16;i++)for(uint32_t lo=0;lo<12;lo++)for(uint32_t hi=0;hi<12;hi++)for(uint32_t r=0;r<8;r++)test(k,values[i],bounds[lo],bounds[hi],refs[r]);for(uint32_t i=0;i<4096;i++){uint32_t a=next(),b=next(),c=next(),r=next();test(k,a,b,c,r);}}host(4,(uintptr_t)"PASS_NATIVE_M55_CLAMPS\n");hex(count);uint32_t p[2]={0x20026,0};host(0x20,(uintptr_t)p);for(;;){}}
