/* Native SpO2 inference parent 0x968c4. Calls the reconstructed C model
 * graph with native history tails and reset-byte semantics. Failure leaks and
 * signaling comparison/FPSCR behavior follow the observed stock routine.
 * See r1/docs/reference/goodix-spo2-infer-c-review.md.
 */
#include "native_spo2_infer.h"
#include <stdint.h>
#include <stddef.h>
#include "native_spo2_infer_support.h"
#include "native_model_graph_execute.h"
extern void *goodix_mem_malloc(uint32_t);
extern void goodix_mem_free(void *);
extern void *memmove(void *,const void *,size_t);
static uint32_t word(uintptr_t p,uint32_t off){return *(const volatile uint32_t *)(p+off);}
static uint32_t byte(uintptr_t p,uint32_t off){return *(const volatile uint8_t *)(p+off);}
static uint32_t half(uintptr_t p,uint32_t off){return *(const volatile uint16_t *)(p+off);}
/* VCMPE against zero: unordered has carry set and raises IOC even for
 * quiet NaNs; FZ affects comparison without changing the stored operand. */
__attribute__((noinline)) static uint32_t compare_zero(uint32_t value)
{
 uint32_t fp=__builtin_arm_get_fpscr(),magnitude=value&0x7fffffffu,flags;
 if((fp&(1u<<24))&&magnitude&&magnitude<0x800000u){magnitude=0;fp|=128u;}
 if(magnitude>0x7f800000u){flags=0x30000000u;fp|=1u;}
 else if(!magnitude)flags=0x60000000u;
 else flags=(value>>31)?0x80000000u:0x20000000u;
 __builtin_arm_set_fpscr((fp&0x0fffffffu)|flags);return flags;
}
uint32_t r1_goodix_spo2_infer(void *context_reference,const void *unused,void *descriptor,void *output,void *flags_reference)
{
 (void)unused;uintptr_t d=(uintptr_t)descriptor;uint32_t first=byte(d,10)*byte(d,9),second=byte(d,13)*byte(d,12);
 void *buffers[2]={0,0};void *outputs[2]={0,0};buffers[0]=goodix_mem_malloc(first*4u);buffers[1]=goodix_mem_malloc(2244);
 uintptr_t ctx=word((uintptr_t)context_reference,0),a=ctx+200,b=ctx+216;uint32_t count_a=half(a,4);
 /* Stock allocates before checking history and leaks both buffers on failure. */
 if(count_a<first||half(b,4)<second)return 5;
 memmove(buffers[0],(const void *)(uintptr_t)(word(a,0)+(count_a-first)*4u),first*4u);
 r1_goodix_native_spo2_clip_normalize((const void *)(uintptr_t)(word(b,0)+(half(b,4)-second)*4u),second,buffers[1]);
 outputs[0]=output;
 uint32_t status=r1_goodix_native_model_graph_execute_veneer((const void *)(uintptr_t)word(d,28),(const void *)(uintptr_t)word(d,20),buffers,(const void *)(uintptr_t)word(d,24),outputs,0,byte(word((uintptr_t)flags_reference,0),5));
 if(status)return 5;
 union{float f;uint32_t u;} value={.u=word((uintptr_t)output,0)},lower=value;
 if(!(compare_zero(value.u)&0x20000000u))lower.u=0;
 if((int32_t)lower.u>=INT32_C(0x40000000))value.u=UINT32_C(0x40000000);
 else if(!(compare_zero(value.u)&0x20000000u))value.u=0;
 *(volatile uint32_t *)output=value.u;
 goodix_mem_free(buffers[0]);goodix_mem_free(buffers[1]);return 0;
}
