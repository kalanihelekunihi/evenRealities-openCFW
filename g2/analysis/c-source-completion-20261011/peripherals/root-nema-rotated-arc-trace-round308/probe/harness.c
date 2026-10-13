#include <stdint.h>
extern void audio_uart_nema_vg_path_process_561c68(void *);
extern void abi_probe(void(*)(void*),void*);
static volatile uint32_t *const abi=(void*)0x20016000;
static const uint32_t fp_seeds[]={0x3f800001,0xbf800002,1,0x80000002,0x7fc12345,0x7f812345,0x7f800000,0xff800000,0x3e800003,0xbe800004,0,0x80000000,0x00800000,0x007fffff,0x7f7fffff,0xff7fffff};
static volatile uint32_t phase;static uint32_t fp_control,guard_seed,arc_flags,relative_flag,mutation,slot;
static const uint32_t patterns[]={0,0x80000000,1,0x80000001,0x007fffff,0x00800000,0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,0x7fc12345,0x7f812345,0xffc54321};
static volatile uint32_t *const path=(void*)0x20010000;
static void host(uint32_t op,uintptr_t p){register uint32_t r0 __asm__("r0")=op;register uintptr_t r1 __asm__("r1")=p;__asm__ volatile("bkpt 0xab":"+r"(r0),"+r"(r1)::"memory");}
static void hex(uint32_t v){char s[10];for(int i=0;i<8;i++)s[i]="0123456789abcdef"[(v>>(28-i*4))&15];s[8]='\n';s[9]=0;host(4,(uintptr_t)s);}
__attribute__((naked)) void fault_handler(void){__asm__ volatile("mov r0,sp\n\tmov r1,lr\n\tb fault_report");}
void fault_report(uint32_t *frame,uint32_t lr){host(4,(uintptr_t)"FAULT\n");hex(phase);hex(*(volatile uint32_t*)0xe000ed28);hex(*(volatile uint32_t*)0xe000ed2c);hex(lr);for(uint32_t i=0;i<28;i++)hex(frame[i]);if(!(lr&16u))frame+=18;hex(frame[6]);hex(frame[5]);hex(frame[7]);uint32_t a[2]={0x20026,1};host(0x20,(uintptr_t)a);for(;;){}}
static uint32_t fb(float f){union{float f;uint32_t b;}v={.f=f};return v.b;}
static void setup(uint32_t k){for(uint32_t i=0;i<64;i++)path[i]=guard_seed;volatile uint8_t *s=(void*)0x20011000;volatile uint32_t *d=(void*)0x20012000;for(uint32_t i=0;i<32;i++){s[i]=0;d[i]=fb((float)((int32_t)i-5));}uint32_t n=0,m=0;
#define SEG(v) s[n++]=((v)==0?0:((v)|relative_flag))
#define VAL(v) d[m++]=fb(v)
if(k && k!=14 && k!=27 && k!=37){SEG(1);VAL(1.25f);VAL(2.5f);}
switch(k){case 0:break;case 1:SEG(2);VAL(4.75f);VAL(-3.25f);break;case 2:SEG(3);VAL(5.0f);SEG(4);VAL(-2.0f);break;case 3:SEG(5);VAL(4.0f);VAL(9.0f);VAL(8.0f);VAL(-2.0f);break;case 4:SEG(6);VAL(9.0f);VAL(-5.0f);VAL(-3.0f);VAL(8.0f);VAL(5.0f);VAL(1.0f);break;case 5:SEG(5);VAL(4.0f);VAL(9.0f);VAL(8.0f);VAL(-2.0f);SEG(7);VAL(2.0f);VAL(6.0f);break;case 6:SEG(6);VAL(9.0f);VAL(-5.0f);VAL(-3.0f);VAL(8.0f);VAL(5.0f);VAL(1.0f);SEG(8);VAL(7.0f);VAL(9.0f);VAL(2.0f);VAL(3.0f);break;case 7:SEG(9|arc_flags);VAL(4.0f);VAL(3.0f);VAL(0.0f);VAL(5.0f);VAL(6.0f);break;case 8:SEG(9|arc_flags);VAL(4.0f);VAL(3.0f);VAL(30.0f);VAL(5.0f);VAL(6.0f);break;case 9:SEG(10);VAL(4.0f);VAL(4.0f);VAL(3.0f);VAL(8.0f);VAL(5.0f);break;case 10:SEG(11);VAL(4.0f);VAL(4.0f);VAL(3.0f);VAL(8.0f);VAL(5.0f);break;case 11:SEG(0x12);VAL(2.0f);VAL(-3.0f);break;case 12:SEG(2);VAL(4);VAL(5);SEG(1);VAL(-3);VAL(2);SEG(2);VAL(7);VAL(9);break;
case 13:SEG(0);SEG(1);VAL(3);VAL(4);SEG(2);VAL(-2);VAL(-3);break;
case 14:SEG(2);VAL(3);VAL(4);break;
case 15:SEG(10);VAL(6);VAL(4);VAL(3);VAL(8);VAL(5);VAL(-2);VAL(7);break;
case 16:SEG(11);VAL(6);VAL(4);VAL(3);VAL(8);VAL(5);VAL(-2);VAL(7);break;
case 17:d[0]=fb(0);d[1]=fb(0);SEG(6);VAL(0);VAL(0);VAL(1);VAL(1);VAL(3);VAL(3);break;
case 18:d[0]=fb(0);d[1]=fb(0);SEG(6);VAL(1);VAL(-1);VAL(3);VAL(-3);VAL(6);VAL(-6);break;
case 19:SEG(6);VAL(2);VAL(3);VAL(3);VAL(4);VAL(8);VAL(9);break;
case 20:SEG(9|arc_flags);VAL(4);VAL(3);VAL(-30);VAL(5);VAL(6);break;
case 21:SEG(9|arc_flags);VAL(0);VAL(3);VAL(30);VAL(5);VAL(6);break;
case 22:SEG(9|arc_flags);VAL(4);VAL(3);VAL(30);VAL(1.25f);VAL(2.5f);break;
case 23:SEG(7);VAL(5);VAL(6);break;
case 24:SEG(8);VAL(3);VAL(5);VAL(6);VAL(8);break;
case 25:SEG(0);SEG(0);SEG(2);VAL(5);VAL(6);break;
case 26:SEG(1);VAL(3);VAL(4);SEG(2);VAL(5);VAL(6);break;
case 27:SEG(12);break;
case 28:SEG(10);VAL(2);VAL(4);VAL(3);break;
case 29:SEG(11);VAL(2);VAL(4);VAL(3);break;
case 30:SEG(10);VAL(0);break;
case 31:SEG(11);VAL(-2);break;case 32:d[0]=fb(0);d[1]=fb(0);SEG(6);VAL(1);VAL(1);VAL(1);VAL(1);VAL(0);VAL(0);break;case 33:d[0]=fb(0);d[1]=fb(0);SEG(6);VAL(2);VAL(1);VAL(3);VAL(1);VAL(3);VAL(0);break;case 34:d[0]=fb(0);d[1]=fb(0);SEG(6);VAL(1);VAL(1);VAL(3);VAL(1);VAL(6);VAL(0);break;case 35:SEG(10);VAL(10);VAL(4);VAL(3);VAL(8);VAL(5);VAL(-2);VAL(7);VAL(1);VAL(2);VAL(6);VAL(-3);break;
case 36:SEG(11);VAL(10);VAL(4);VAL(3);VAL(8);VAL(5);VAL(-2);VAL(7);VAL(1);VAL(2);VAL(6);VAL(-3);break;
case 37:SEG(2);VAL(3);VAL(4);SEG(1);VAL(5);VAL(6);SEG(2);VAL(7);VAL(8);break;
case 38:SEG(6);VAL(9);VAL(-5);VAL(-3);VAL(8);VAL(5);VAL(1);SEG(7);VAL(2);VAL(6);break;
case 39:SEG(5);VAL(4);VAL(9);VAL(8);VAL(-2);SEG(8);VAL(3);VAL(5);VAL(6);VAL(8);break;case 40:SEG(9|arc_flags);VAL(4);VAL(3);VAL(90);VAL(5);VAL(6);break;case 41:SEG(9|arc_flags);VAL(4);VAL(3);VAL(270);VAL(5);VAL(6);break;case 42:SEG(9|arc_flags);VAL(4);VAL(3);VAL(180);VAL(5);VAL(6);break;case 43:SEG(9|arc_flags);d[m++]=0x7fc12345;VAL(3);VAL(45);VAL(5);VAL(6);break;}
if(k)SEG(0);if(0)d[slot]=patterns[mutation];path[0]=n;path[1]=m;path[2]=0x20011000;path[3]=0x20012000;*(volatile uint32_t*)0x20074f14=0xa5a5a5a5;uint32_t f=0x40000u|fp_control;__asm__ volatile("vmsr fpscr,%0"::"r"(f));}
static void fail_comparison(void){uint32_t a[2]={0x20026,1};host(0x20,(uintptr_t)a);for(;;){}}
int main(void){uint32_t result[64],abi_native[25],fpscr,error_native;for(uint32_t relative=0;relative<1;relative++)for(uint32_t arc=0;arc<1;arc++)for(uint32_t guard=0;guard<1;guard++)for(uint32_t round=0;round<1;round++)for(uint32_t extra=0;extra<1;extra++)for(uint32_t k=0;k<44;k++){arc_flags=arc<<5;relative_flag=relative?16:0;guard_seed=guard==0?0:(guard==1?0x5a5a5a5a:0xffffffff);fp_control=(round<<22)|(extra?0x0300009f:0);setup(k);phase=10+k;abi_probe((void(*)(void*))0x28229c69,(void*)path);for(uint32_t i=0;i<25;i++)abi_native[i]=abi[i];for(uint32_t i=0;i<8;i++)if(abi[i]!=(i+4)*0x1111u){host(4,(uintptr_t)"FAIL_NATIVE_CORE_SEED\n");fail_comparison();}for(uint32_t i=0;i<16;i++)if(abi[9+i]!=fp_seeds[i]){host(4,(uintptr_t)"FAIL_NATIVE_FP_SEED\n");fail_comparison();}if(abi[8]!=abi[25]){host(4,(uintptr_t)"FAIL_NATIVE_SP\n");fail_comparison();}for(uint32_t i=0;i<64;i++)result[i]=path[i];__asm__ volatile("vmrs %0,fpscr":"=r"(fpscr));error_native=*(volatile uint32_t*)0x20074f14;setup(k);phase=20+k;abi_probe(audio_uart_nema_vg_path_process_561c68,(void*)path);for(uint32_t i=0;i<25;i++)if(abi_native[i]!=abi[i]){host(4,(uintptr_t)"FAIL_ABI\n");hex(i);hex(abi_native[i]);hex(abi[i]);fail_comparison();}if(abi[8]!=abi[25]){host(4,(uintptr_t)"FAIL_C_SP\n");fail_comparison();}uint32_t c;__asm__ volatile("vmrs %0,fpscr":"=r"(c));for(uint32_t i=0;i<64;i++)if(result[i]!=path[i]){host(4,(uintptr_t)"FAIL_PATH\n");hex(mutation);hex(slot);hex(relative);hex(arc);hex(guard);hex(round);hex(extra);hex(k);hex(i);hex(result[i]);hex(path[i]);fail_comparison();}if(error_native!=*(volatile uint32_t*)0x20074f14){host(4,(uintptr_t)"FAIL_ERROR_CELL\n");hex(mutation);hex(slot);hex(relative);hex(arc);hex(guard);hex(round);hex(extra);hex(k);hex(error_native);hex(*(volatile uint32_t*)0x20074f14);fail_comparison();}if(c!=fpscr){host(4,(uintptr_t)"FAIL_FPSCR\n");hex(mutation);hex(slot);hex(relative);hex(arc);hex(guard);hex(round);hex(extra);hex(k);hex(fpscr);hex(c);fail_comparison();}}
host(4,(uintptr_t)"PASS_TARGETED_BRANCH_FIXTURES_ABI_MATRIX\n");uint32_t a[2]={0x20026,0};host(0x20,(uintptr_t)a);for(;;){}}
