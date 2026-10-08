/* Selected non-type7 saturated scan7bc0. Mode switching is explicitly external. */
#include <stdint.h>
#include "scan.h"
#include "../max_raw_offline/max_raw.h"
#include "../scan_watchdog_offline/watchdog.h"
#include "../scan_frame_offline/frame.h"
uint32_t touch_execute_saturated(uint32_t *out,uint32_t id,uint32_t slot,uint8_t *context,touch_mode_switch transition){
 uint8_t *w=(uint8_t *)(*(uint32_t *)(context+12)+id*144u),*runtime=(uint8_t *)(*(uint32_t *)(context+16)+id*60u);const uint8_t *common=*(const uint8_t **)context;volatile uint32_t *hw=**(volatile uint32_t *const *const *)(common+8);
 uint32_t status=transition(5,context);const uint32_t *frame=(const uint32_t *)(*(uint32_t *)(context+40)+slot*28u);
 uint32_t temporary[6]={0,0,0,frame[3]&0xffffbfffu,frame[4],frame[5]};
 if(!status){touch_start_scan_frame(temporary,context);uint32_t budget=touch_scan_watchdog(id,slot,context);if(!touch_scan_wait(budget,context))status|=4u;}
 uint32_t fifo=hw[0x3200/4]&0xffffu;hw[0]&=0x7fffffffu;
 *out=touch_saturated_max(fifo,temporary[5],runtime[33],w[122],w[132]);return status;
}
