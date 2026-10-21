/* Native WsfSetOsSpecificEvent 0x52b8d8: task/ISR notification paths. */
#include <stdint.h>
extern void *audio_wsf_event_group; /* selected WsfOsInit BSS, native 0x20074ef0 */
extern uint32_t g2_log_is_privileged(void); /* selected MRS CONTROL body */
extern uint32_t g2_log_exception_number(void); /* selected MRS IPSR body */
extern uint32_t xEventGroupSetBitsFromISR(void *,uint32_t,int32_t *); /* selected 0x47ee4a */
extern uint32_t xEventGroupSetBits(void *,uint32_t); /* selected 0x47ed76 */
void WsfSetOsSpecificEvent(void) {
    void *handle=audio_wsf_event_group;
    if(!handle)return;
    if(g2_log_is_privileged() && (g2_log_exception_number()&0x1ffu)) {
        int32_t higher_priority_woken=0;
        if(xEventGroupSetBitsFromISR(handle,1u,&higher_priority_woken) && higher_priority_woken)
            *(volatile uint32_t *)(uintptr_t)0xe000ed04u=0x10000000u;
    } else if(xEventGroupSetBits(handle,1u)) {
        *(volatile uint32_t *)(uintptr_t)0xe000ed04u=0x10000000u;
        __asm volatile("dsb sy\n\tisb sy" ::: "memory");
    }
}
