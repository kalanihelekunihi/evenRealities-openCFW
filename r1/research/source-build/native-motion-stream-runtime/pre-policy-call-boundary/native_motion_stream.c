#include <stdint.h>
#include "../board/native_battery_memory.h"
/* Only these authenticated cold cells are owned, not the surrounding motion
 * selection/configuration records or licensed sensor provider bodies. */
volatile uint32_t r1_motion_selected_provider __attribute__((section(".r1.motion.selected"),aligned(4)))=0;
volatile uint8_t r1_motion_calibration_bypass __attribute__((section(".r1.motion.calib.bypass"),aligned(1)))=0;
extern void r1_motion_probe_and_select_provider(void);
extern void *volatile r1_device_info_kv_handle;
extern uint32_t r1_kv_class_read(void *,void *,uint32_t),r1_stream_tick_now(void);
__attribute__((naked)) uint32_t r1_motion_selected_provider_initialize(void)
{
 __asm__ volatile("push {r4,lr}\nldr r4,=r1_motion_selected_provider\nldr r0,[r4]\ncmp r0,#0\nbne 1f\nbl r1_motion_probe_and_select_provider\nldr r0,[r4]\ncmp r0,#0\nbeq 2f\n1: ldr r0,[r0]\ncmp r0,#0\nbeq 2f\npop {r4,lr}\nbx r0\n2: movs r0,#0\npop {r4,pc}\n");
}
__attribute__((naked)) uint32_t r1_motion_initialize_entry(uint32_t context __attribute__((unused)))
{__asm__ volatile("b r1_motion_selected_provider_initialize\n");}
uint32_t r1_motion_stream_close_boundary(uint32_t context __attribute__((unused))){return 1;}
__attribute__((naked)) uint32_t r1_native_motion_interrupt(void)
{
 __asm__ volatile("ldr r0,=r1_motion_selected_provider\nldr r0,[r0]\ncmp r0,#0\nbeq 1f\nldr r0,[r0,#12]\ncmp r0,#0\nbeq 1f\nbx r0\n1: bx lr\n");
}
__attribute__((naked)) int32_t r1_motion_selected_fifo_read(uint8_t *destination __attribute__((unused)),uint32_t samples __attribute__((unused)))
{
 __asm__ volatile("ldr r2,=r1_motion_selected_provider\nldr r2,[r2]\ncbz r2,1f\nldr r2,[r2,#8]\ncbz r2,1f\nbx r2\n1: mov.w r0,#-1\nbx lr\n");
}
uint32_t r1_motion_calibration_bypassed(void){return r1_motion_calibration_bypass;}
__attribute__((used,noinline)) uint32_t r1_motion_calibration_body(volatile uint8_t *out,volatile uint8_t *scratch)
{
 (void)r1_kv_class_read(r1_device_info_kv_handle,(void *)(uintptr_t)scratch,124);
 write32(out,read32(scratch+68));uint32_t last=read16(scratch+72);write16(out+4,last);return last;
}
__attribute__((naked)) uint32_t r1_motion_calibration_read(volatile void *out __attribute__((unused)))
{
 __asm__ volatile("push {r4,lr}\nsub sp,#128\nmov r1,sp\nbl r1_motion_calibration_body\nadd sp,#128\npop {r4,pc}\n");
}
__attribute__((used,noinline)) void r1_motion_adjust_samples(volatile uint8_t *destination,uint32_t count,volatile uint8_t *offset)
{
 if(read16(offset)==65535 && read16(offset+2)==65535 && read16(offset+4)==65535){write16(offset,0);write16(offset+2,0);write16(offset+4,0);}
 for(uint32_t i=0;i<count;i++)if(!r1_motion_calibration_bypassed()){
  volatile uint8_t *sample=destination+i*6;
  uint32_t delta=read16(offset);uint32_t value=read16(sample);write16(sample,value+delta);
  delta=read16(offset+2);value=read16(sample+2);write16(sample+2,value+delta);
  value=read16(sample+4);delta=read16(offset+4);write16(sample+4,value+delta);
 }
}
__attribute__((naked)) uint32_t r1_motion_thirty_sample_batch_producer(uint8_t *destination __attribute__((unused)),uint32_t length __attribute__((unused)),uint32_t context __attribute__((unused)))
{
 __asm__ volatile("push {r2,r3,r4,r5,r6,lr}\ncbz r0,2f\ncmp r1,#188\nbne 2f\nmov r4,r0\nmovs r1,#30\nbl r1_motion_selected_fifo_read\nmovs r6,r0\nbmi 2f\nmovs r5,#0\nstr r5,[sp]\nstr r5,[sp,#4]\nmov r0,sp\nbl r1_motion_calibration_read\nuxth r6,r6\nmov r0,r4\nmov r1,r6\nmov r2,sp\nbl r1_motion_adjust_samples\nstrh.w r6,[r4,#180]\nbl r1_stream_tick_now\nstr.w r0,[r4,#184]\nmovs r0,#188\nb 3f\n2: movs r0,#0\n3: pop {r2,r3,r4,r5,r6,pc}\n");
}
