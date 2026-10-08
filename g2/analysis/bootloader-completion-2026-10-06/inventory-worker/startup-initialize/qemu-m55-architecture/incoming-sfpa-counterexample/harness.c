/* SPDX-License-Identifier: MIT. Synthetic core/NVIC fixture, not Apollo510. */
#include <stdint.h>
#define W(p) (*(volatile uint32_t *)(uintptr_t)(p))
#ifndef TEST_FP_INCOMING
#define TEST_FP_INCOMING 0
#endif
#ifndef TEST_FP
#define TEST_FP 0
#endif
#ifndef TEST_OWNERSHIP
#define TEST_OWNERSHIP 0
#endif
extern void task_entry(void),idle_entry(void),opencfw_boot_idle_cleanup(uint32_t,uint32_t,uint32_t,uint32_t);
extern void opencfw_boot_thread_delete(uint32_t *),opencfw_bl_ready_lists_initialize(void);
extern void opencfw_bl_thread_register(uint32_t *);
extern uintptr_t opencfw_bl_rtos_allocate(uint32_t);
volatile uint32_t initial_regs[14],irq_count,irq_lr,irq_psp,irq_s0,irq_fpscr,irq_pc,irq_xpsr;
static uint32_t idle_tcb[28] __attribute__((aligned(8)));
static uint32_t static_tcb[28] __attribute__((aligned(8)));
static uint8_t idle_stack[2048] __attribute__((aligned(8)));
static uint8_t static_stack[2048] __attribute__((aligned(8)));
static uint32_t incoming_tcb[28] __attribute__((aligned(8)));
static uint8_t incoming_stack[2048] __attribute__((aligned(8)));
extern void incoming_entry(void);
static uint32_t *active;static uintptr_t task_stack;static uint32_t heap_baseline;
static void semihost(uint32_t op,uintptr_t arg){register uint32_t r0 __asm__("r0")=op;register uintptr_t r1 __asm__("r1")=arg;__asm__ volatile("bkpt 0xab" : "+r"(r0):"r"(r1):"memory");}
static void text(const char *s){semihost(4,(uintptr_t)s);}
static void hex(uint32_t x){char s[11];s[0]='0';s[1]='x';for(unsigned i=0;i<8;i++)s[2+i]="0123456789abcdef"[(x>>(28-4*i))&15];s[10]=0;text(s);}
__attribute__((noreturn)) static void finish(uint32_t status){uint32_t x[2]={0x20026,status};semihost(0x20,(uintptr_t)x);for(;;){}}
__attribute__((noreturn)) static void fail(uint32_t code){text("FAIL ");hex(code);text("\n");finish(code);}
#define CHECK(x,c) do{if(!(x))fail(c);}while(0)
void record_fault(uint32_t *frame,uint32_t lr){text("FAULT LR=");hex(lr);text(" CFSR=");hex(W(0xe000ed28));text(" HFSR=");hex(W(0xe000ed2c));text(" PC=");hex(frame[6]);text("\n");finish(90);}
void opencfw_bl_stack_overflow(uint32_t *a,const char *b){(void)a;(void)b;fail(91);}
void opencfw_bl_malloc_failed(void){fail(92);}
void *memset(void *p,int c,unsigned n){uint8_t *q=p;for(unsigned i=0;i<n;i++)q[i]=(uint8_t)c;return p;}
static uint32_t *make_frame(uint8_t *base,uintptr_t entry,uint32_t arg){
 memset(base,0xa5,2048);uint32_t *f=(uint32_t *)(base+2048-72);
 f[0]=(uintptr_t)base;f[1]=0xfffffffd;
 for(unsigned i=0;i<8;i++)f[2+i]=0x44000000+i;
 f[10]=arg;f[11]=0x11111111;f[12]=0x22222222;f[13]=0x33333333;
 f[14]=0x12121212;f[15]=0xdeadbeef;f[16]=entry;f[17]=0x01000000;
 return f;
}
void record_irq(uint32_t *frame,uint32_t lr){
 irq_lr=lr;irq_psp=(uintptr_t)frame;
 if(!(lr&16)){
  /* A real FP instruction forces completion of pending lazy low-FP stacking. */
  uint32_t fpscr;__asm__ volatile("vmrs %0,fpscr":"=r"(fpscr));(void)fpscr;
  irq_s0=frame[8];irq_fpscr=frame[24];
 }
 irq_pc=frame[6];irq_xpsr=frame[7];irq_count++;
}
static uint32_t ipsr(void){uint32_t x;__asm__ volatile("mrs %0,ipsr":"=r"(x));return x;}
static uint32_t control(void){uint32_t x;__asm__ volatile("mrs %0,control":"=r"(x));return x;}
void incoming_main(void){
 uint32_t z,y,v,round;__asm__ volatile("vmov %0,s0\n vmov %1,s16\n vmov %2,s31\n vmrs %3,fpscr":"=r"(z),"=r"(y),"=r"(v),"=r"(round));
 text("INCOMING fpscr=");hex(round);text("\n");
 CHECK(z==0x40000000 && y==0x42000000 && v==0x42800000,61);CHECK(round==0x00440000,62);
 CHECK(initial_regs[0]==0xf0f00001 && initial_regs[12]==0x12121212,63);
 for(unsigned i=0;i<8;i++)CHECK(initial_regs[4+i]==0x55000000+i,64);
 CHECK(ipsr()==0 && (control()&6)==6,65);CHECK(W(0x20027134)==(uintptr_t)incoming_tcb,66);
 text("PASS actual-entry-return incoming-FP ");hex(TEST_OWNERSHIP);text(" outgoing-idle-cleaned\n");finish(0);
}
static void start_incoming(void){
 memset(incoming_stack,0xa5,2048);memset(incoming_tcb,0,112);
 uint32_t *f=(uint32_t *)(incoming_stack+2048-208);memset(f,0,208);
 f[0]=(uintptr_t)incoming_stack;f[1]=0xffffffed;
 for(unsigned i=0;i<8;i++)f[2+i]=0x55000000+i;
 f[10]=0x42000000;f[25]=0x42800000;
 f[26]=0xf0f00001;f[30]=0x12121212;f[31]=0xdeadbeef;f[32]=(uintptr_t)incoming_entry;f[33]=0x01000000;
 f[34]=0x40000000;f[50]=0x00440000;
 incoming_tcb[0]=(uintptr_t)f;incoming_tcb[12]=(uintptr_t)incoming_stack;incoming_tcb[11]=1;incoming_tcb[4]=(uintptr_t)incoming_tcb;((uint8_t*)incoming_tcb)[0x6d]=2;
 opencfw_bl_thread_register(incoming_tcb);W(0xe000ed04)=0x10000000;__asm__ volatile("dsb sy\n isb sy":::"memory");fail(67);
}
void idle_main(uint32_t arg){
 for(unsigned i=0;i<8;i++)CHECK(initial_regs[4+i]==0x44000000+i,39);
 CHECK(arg==0x1d1e0001,40);CHECK(ipsr()==0,41);CHECK(W(0x20027134)==(uintptr_t)idle_tcb,42);
 CHECK(W(0x20027140)==1 && W(0x20026f70)==1,43);CHECK(W(0x20027144)==2,44);
 CHECK(W(0x20027118)==0,45);CHECK(!(control()&4),46);
 uint32_t *saved=(uint32_t *)(uintptr_t)active[0];
 CHECK(saved[0]==task_stack && ((saved[1]&16)!=0)==!TEST_FP,51);
 if(TEST_FP){CHECK(saved[10]==0x41200000 && saved[25]==0x41a00000,52);CHECK(saved[34]==0x3f800000 && (saved[50]&0x00c00000)==0x00400000,53);}
 uint32_t outgoing=(uintptr_t)saved;
 opencfw_boot_idle_cleanup(0,0,0,0);
 CHECK(W(0x20027140)==0 && W(0x20026f70)==0,47);CHECK(W(0x20027144)==1,48);
 CHECK(W(0x20027118)==(TEST_OWNERSHIP==0?2:TEST_OWNERSHIP==1?1:0),49);
 CHECK(W(0x2002710c)==heap_baseline,50);
 text("FACT irq_lr=");hex(irq_lr);text(" irq_psp=");hex(irq_psp);text(" irq_pc=");hex(irq_pc);text(" irq_xpsr=");hex(irq_xpsr);text(" irq_s0=");hex(irq_s0);text(" irq_fpscr=");hex(irq_fpscr);text(" outgoing_frame=");hex(outgoing);text(" free_count=");hex(W(0x20027118));text(" task_count=");hex(W(0x20027144));text(" heap_free=");hex(W(0x2002710c));text(" control_idle=");hex(control());text("\n");
 if(TEST_FP_INCOMING)start_incoming();
 text("PASS actual-entry-return ");text(TEST_FP?"FP ":"basic ");hex(TEST_OWNERSHIP);text(" idle-reclaimed\n");finish(0);
}
void task_main(void){
 CHECK(initial_regs[0]==0xa0b0c0d0,1);
 CHECK(initial_regs[1]==0x11111111 && initial_regs[2]==0x22222222 && initial_regs[3]==0x33333333,2);
 CHECK(initial_regs[12]==0x12121212,3);CHECK(initial_regs[13]==0xdeadbeef,4);
 CHECK(ipsr()==0 && (control()&2),5);CHECK(W(0x20027134)==(uintptr_t)active,6);
 if(TEST_FP){uint32_t z=0x3f800000,y=0x41200000,v=0x41a00000,round=0x00440000;
  __asm__ volatile("vmov s0,%0\n vmov s16,%1\n vmov s31,%2\n vmsr fpscr,%3"::"r"(z),"r"(y),"r"(v),"r"(round):"memory");
 }
 W(0xe000e100)=1;W(0xe000e200)=1;
 __asm__ volatile("dsb sy\n isb sy":::"memory");
 CHECK(irq_count==1 && ipsr()==0,10);CHECK((irq_lr&0x1c)==(TEST_FP?0xc:0x1c),11);
 CHECK(irq_xpsr&0x01000000,12);
 if(TEST_FP){uint32_t z,y,v,round;__asm__ volatile("vmov %0,s0\n vmov %1,s16\n vmov %2,s31\n vmrs %3,fpscr":"=r"(z),"=r"(y),"=r"(v),"=r"(round));
  CHECK(z==0x3f800000 && y==0x41200000 && v==0x41a00000,13);CHECK((round&0x00c00000)==0x00400000,14);CHECK(irq_s0==z && irq_fpscr==round,15);
 }
 /* Current-task deletion must defer free until actual PendSV switches stack. */
 opencfw_boot_thread_delete(active);fail(30);
}
void harness_main(void){
 text("START M55 core-only\n");
 W(0xe000ed08)=0;W(0xe000ed20)=0xffff0000;W(0xe000ed88)=0x00f00000;
 __asm__ volatile("dsb sy\n isb sy":::"memory");
 memset((void*)0x200004c4,0,4);memset((void*)0x20024870,0,1120);memset((void*)0x20026f34,0,100);memset((void*)0x20027130,0,80);
 opencfw_bl_ready_lists_initialize();
 /* Trigger lazy heap initialization and record fully free baseline. */
 extern void opencfw_bl_rtos_free(uintptr_t);
 uintptr_t probe=opencfw_bl_rtos_allocate(32);opencfw_bl_rtos_free(probe);heap_baseline=W(0x2002710c);W(0x20027118)=0;
 task_stack=TEST_OWNERSHIP==0?opencfw_bl_rtos_allocate(2048):(uintptr_t)static_stack;
 active=TEST_OWNERSHIP==2?static_tcb:(uint32_t*)opencfw_bl_rtos_allocate(112);
 memset(active,0,112);memset(idle_tcb,0,112);
 active[0]=(uintptr_t)make_frame((uint8_t*)task_stack,(uintptr_t)task_entry,0xa0b0c0d0);active[12]=task_stack;active[11]=1;active[4]=(uintptr_t)active;
 ((uint8_t*)active)[0x6d]=TEST_OWNERSHIP;
 idle_tcb[0]=(uintptr_t)make_frame(idle_stack,(uintptr_t)idle_entry,0x1d1e0001);idle_tcb[12]=(uintptr_t)idle_stack;idle_tcb[11]=0;idle_tcb[4]=(uintptr_t)idle_tcb;((uint8_t*)idle_tcb)[0x6d]=2;
 opencfw_bl_thread_register(idle_tcb);opencfw_bl_thread_register(active);
 W(0x20027150)=1;W(0x20027134)=(uintptr_t)active;W(0x20027170)=0;
 __asm__ volatile("cpsie i\n svc #2":::"memory");fail(70);
}
