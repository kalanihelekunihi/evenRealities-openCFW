/* Native WsfSetOsSpecificEvent 0x52b8d8: task/ISR notification paths.
 * Stock tests xPortIsInsideInterrupt (0x442228, MRS IPSR != 0) and, on the
 * task path, calls vPortYield (0x4420bc) when xEventGroupSetBits returns
 * non-zero. The former duplicate audio_wsf_set_os_event
 * (ble/wsf-os/display_wsf_os_event.c) is an alias of this body. */
#include <stdint.h>
extern void *audio_wsf_event_group; /* selected WsfOsInit BSS, native 0x20074ef0 */
extern int32_t xPortIsInsideInterrupt(void); /* upstream FreeRTOS port, 0x442228 */
extern void vPortYield(void); /* upstream FreeRTOS port, 0x4420bc */
extern int32_t xEventGroupSetBitsFromISR(void *,uint32_t,int32_t *); /* selected 0x47ee4a */
extern uint32_t xEventGroupSetBits(void *,uint32_t); /* selected 0x47ed76 */
void WsfSetOsSpecificEvent(void) {
    void *handle=audio_wsf_event_group;
    if(!handle)return;
    if(xPortIsInsideInterrupt()==1) {
        int32_t higher_priority_woken=0;
        if(xEventGroupSetBitsFromISR(handle,1u,&higher_priority_woken)!=0 && higher_priority_woken!=0)
            *(volatile uint32_t *)(uintptr_t)0xe000ed04u=0x10000000u;
    } else if(xEventGroupSetBits(handle,1u)!=0u) {
        vPortYield();
    }
}
__typeof__(WsfSetOsSpecificEvent) audio_wsf_set_os_event __attribute__((alias("WsfSetOsSpecificEvent")));
