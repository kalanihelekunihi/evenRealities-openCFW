/* Native 0x6a320: C dispatch policy with a fixed-frame transfer adapter.
 * C preparation uses private scratch below the 216-byte native frame and
 * returns before any provider call. Outgoing words are written to native SP
 * in stock order so raw/result aliases retain their observed behavior. */
#include <stdbool.h>
#include "gh_demo.h"
#include "kernel/gh_demo_config.h"
#include "gh_demo_inner.h"
#if (__DRIVER_LIB_MODE__ == __DRV_LIB_WITH_ALGO__)
#include "gh3x2x_demo_algo_call.h"
#endif
#include <stdint.h>
#include <stddef.h>
#include "native_stream_callbacks.h"
typedef struct __attribute__((packed,may_alias)){uint32_t value;} io_word_t;
static uint32_t io_w(const volatile void *p){return ((const volatile io_word_t *)p)->value;}
static void io_put(volatile void *p,uint32_t v){((volatile io_word_t *)p)->value=v;}
static const volatile uint8_t *io_p(const volatile void *p){return (const volatile uint8_t *)(uintptr_t)io_w(p);}
typedef uint64_t io_pair_t __attribute__((aligned(4),may_alias));
static uint64_t io_pair(const volatile void *p){return *(const volatile io_pair_t *)p;}
extern void __aeabi_memclr(void *,size_t);
extern int (*g_pSnprintfUserIn)(char *,size_t,const char *,...);
extern int (*g_pPrintfUserIn)(const char *,...);
volatile uint32_t r1_goodix_frame_extrema[3] __attribute__((section(".bss.r1.goodix.frame.extrema"),aligned(4)));
static const char io_message[]="[LOG_I] pstFrameInfo : %d %d %d %d %d %d \r\n";
_Static_assert(sizeof(uintptr_t)==4 && offsetof(STGh3x2xFrameInfo,unFunctionID)==0 && offsetof(STGh3x2xFrameInfo,punFrameRawdata)==20 && offsetof(STGh3x2xFrameInfo,pstAlgoResult)==60,"native frame fields");
enum {IO_DONE,IO_TAIL,IO_CALL_DONE,IO_CALL_NEXT,IO_NEXT};
enum {IO_ALGO=1,IO_DISPATCH,IO_CLEAR,IO_FORMAT,IO_PLATFORM,IO_PRINT};
struct io_plan{uint32_t target,args[4],r4,r5,r6,action,result;};
_Static_assert(sizeof(struct io_plan)==40 && offsetof(struct io_plan,action)==32,"adapter plan");
__attribute__((used,noinline)) static void io_prepare(struct io_plan *out,uint32_t stage,const volatile uint8_t *frame,volatile uint8_t *sp,uint32_t live5,uint32_t live6)
{
 out->r4=(uintptr_t)frame;out->r5=live5;out->r6=live6;out->action=IO_DONE;out->target=0;out->result=0;
 for(unsigned i=0;i<4;++i)out->args[i]=0;
 if(stage==IO_ALGO){out->target=(uintptr_t)GH3X2X_AlgoCalculate;out->args[0]=io_w(frame);out->action=IO_CALL_NEXT;return;}
 if(stage==IO_DISPATCH){
  uint32_t function=io_w(frame),callback;const volatile uint8_t *data;out->result=function;
  switch(function){
  case 1:callback=r1_goodix_stream_callbacks[6];if(!callback)return;data=io_p(frame+20);out->args[0]=io_w(data);out->args[1]=callback;out->target=callback;out->action=IO_TAIL;return;
  case 8:callback=r1_goodix_stream_callbacks[1];if(!callback)return;data=io_p(frame+20);out->args[0]=io_w(data);out->args[1]=io_w(data+4);out->args[2]=callback;out->target=callback;out->action=IO_TAIL;return;
  case 2:case 4:case 0x40:{
   data=io_p(frame+60);out->result=data[0];if(out->result!=1)return;
   callback=r1_goodix_stream_callbacks[function==2?0:function==4?7:2];if(!callback)return;
   out->r4=callback;out->args[0]=io_w(data+4);out->result=out->args[0];if(!out->args[0])return;
   if(function!=2){uint64_t last=io_pair(data+20);io_put(sp,(uint32_t)last);io_put(sp+4,(uint32_t)(last>>32));}
   out->args[1]=io_w(data+8);out->args[2]=io_w(data+12);out->args[3]=io_w(data+16);out->target=callback;out->action=function==2?IO_TAIL:IO_CALL_DONE;return;
  }
  case 0x2000:{
   data=io_p(frame+20);uint64_t pair=io_pair(data);uint32_t a=pair,b=pair>>32;r1_goodix_frame_extrema[0]=a<b?a:b;
   pair=io_pair(data+16);a=pair;b=pair>>32;out->r5=a;r1_goodix_frame_extrema[1]=a<b?a:b;
   pair=io_pair(data+8);a=pair;b=pair>>32;r1_goodix_frame_extrema[2]=a<b?a:b;
   uint8_t selector=*(const volatile uint8_t *)(uintptr_t)0x20006c34u;
   callback=r1_goodix_stream_callbacks[selector?5:4];out->args[0]=(uintptr_t)r1_goodix_frame_extrema;out->args[1]=(uintptr_t)(r1_goodix_frame_extrema+2);out->args[2]=(uintptr_t)(r1_goodix_frame_extrema+1);out->args[3]=callback;out->target=callback;out->action=callback?IO_CALL_NEXT:IO_NEXT;return;
  }
  default:return;
  }
 }
 if(stage==IO_CLEAR){
  out->r5=(uintptr_t)&g_pSnprintfUserIn;
  if(*(int (*volatile *)(char *,size_t,const char *,...))&g_pSnprintfUserIn){out->target=(uintptr_t)__aeabi_memclr;out->args[0]=(uintptr_t)(sp+20);out->args[1]=180;out->action=IO_CALL_NEXT;}else out->action=IO_NEXT;return;
 }
 if(stage==IO_FORMAT){
  const volatile uint8_t *raw=io_p(frame+20);uint32_t c=io_w(raw+8),d=io_w(raw+12),e=io_w(raw+16),f=io_w(raw+20);
  io_put(sp+4,c);io_put(sp+8,d);io_put(sp+12,e);io_put(sp+16,f);io_put(sp,io_w(raw+4));uint32_t a=io_w(raw);
  uint32_t format=(uintptr_t)*(int (*volatile *)(char *,size_t,const char *,...))&g_pSnprintfUserIn;
  out->r5=format;out->r6=f;out->target=format;out->args[0]=(uintptr_t)(sp+20);out->args[1]=180;out->args[2]=(uintptr_t)io_message;out->args[3]=a;out->action=IO_CALL_NEXT;return;
 }
 if(stage==IO_PLATFORM){out->target=(uintptr_t)GH3X2X_PlatformLog;out->args[0]=(uintptr_t)(sp+20);out->action=IO_CALL_NEXT;return;}
 if(stage==IO_PRINT){
  uint32_t print=(uintptr_t)*(int (*volatile *)(const char *,...))&g_pPrintfUserIn;out->r5=print;out->result=(uintptr_t)&g_pPrintfUserIn;if(!print)return;
  const volatile uint8_t *raw=io_p(frame+20);uint32_t d=io_w(raw+12),e=io_w(raw+16),f=io_w(raw+20);io_put(sp,d);io_put(sp+4,e);io_put(sp+8,f);out->args[1]=io_w(raw);out->args[2]=io_w(raw+4);out->args[3]=io_w(raw+8);out->args[0]=(uintptr_t)io_message;out->target=print;out->action=IO_CALL_DONE;return;
 }
}
__attribute__((naked,noinline)) void gh3x2x_algorithm_get_io_data_hook_func(const STGh3x2xFrameInfo * const input __attribute__((unused)))
{
 __asm__ volatile(
 "push {r4,r5,r6,lr}\nsub sp,#200\nmov r4,r0\n"
 "movs r0,#1\nbl IO_PREP\nbl IO_LOAD\nblx r12\n"
 "movs r0,#2\nbl IO_PREP\nldr r0,[sp,#48]\ncmp r0,#0\nbeq IO_DONE_LABEL\ncmp r0,#1\nbeq IO_TAIL_LABEL\ncmp r0,#2\nbeq IO_CALL_DONE_LABEL\ncmp r0,#4\nbeq IO_SKIP_CALLBACK\nbl IO_LOAD\nblx r12\nb IO_CLEAR_LABEL\n"
 "IO_SKIP_CALLBACK:\nbl IO_LOAD\n"
 "IO_CLEAR_LABEL:\nmovs r0,#3\nbl IO_PREP\nldr r0,[sp,#48]\ncmp r0,#4\nbeq IO_SKIP_CLEAR\nbl IO_LOAD\nblx r12\n"
 "movs r0,#4\nbl IO_PREP\nbl IO_LOAD\nblx r12\n"
 "movs r0,#5\nbl IO_PREP\nbl IO_LOAD\nblx r12\nb IO_PRINT_LABEL\n"
 "IO_SKIP_CLEAR:\nbl IO_LOAD\n"
 "IO_PRINT_LABEL:\nmovs r0,#6\nbl IO_PREP\nldr r0,[sp,#48]\ncmp r0,#0\nbeq IO_DONE_LABEL\n"
 "IO_CALL_DONE_LABEL:\nbl IO_LOAD\nblx r12\nb IO_RETURN\n"
 "IO_DONE_LABEL:\nldr r0,[sp,#52]\nadd sp,#80\nIO_RETURN:\nadd sp,#200\npop {r4,r5,r6,pc}\n"
 "IO_TAIL_LABEL:\nbl IO_LOAD\nadd sp,#200\npop {r4,r5,r6,lr}\nbx r12\n"
 "IO_PREP:\nmov r1,r0\nmov r3,sp\nsub sp,#80\nstr r5,[sp]\nstr r6,[sp,#4]\nstr lr,[sp,#8]\nadd r0,sp,#16\nmov r2,r4\nbl io_prepare\nldr lr,[sp,#8]\nbx lr\n"
 "IO_LOAD:\nldr r12,[sp,#16]\nldr r4,[sp,#36]\nldr r5,[sp,#40]\nldr r6,[sp,#44]\nadd r0,sp,#20\nldmia r0,{r0-r3}\nadd sp,#80\nbx lr\n":::"memory");
}

