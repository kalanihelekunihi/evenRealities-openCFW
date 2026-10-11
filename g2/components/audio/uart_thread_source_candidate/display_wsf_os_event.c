/* Native WsfSetOsSpecificEvent 0x52b8d8. */
#include <stdint.h>
extern void *audio_wsf_event_group; /* pointer cell RAM 0x20074ef0 */
extern int32_t xEventGroupSetBitsFromISR(void *,uint32_t,int32_t *); /* selected 0x47ee4a */
extern uint32_t xEventGroupSetBits(void *,uint32_t); /* selected 0x47ed76 */
extern void audio_yield(void); /* selected 0x4420bc */
uint32_t audio_wsf_in_interrupt(void) {
    uint32_t ipsr;
    __asm__ volatile("mrs %0, ipsr" : "=r"(ipsr));
    return ipsr!=0u;
}
void audio_wsf_set_os_event(void) {
    void *group=audio_wsf_event_group;
    if(group==0) return;
    if(audio_wsf_in_interrupt()!=0u) {
        int32_t wake=0;
        if(xEventGroupSetBitsFromISR(group,1u,&wake)!=0&&wake!=0)
            *(volatile uint32_t *)0xe000ed04u=0x10000000u;
    } else if(xEventGroupSetBits(group,1u)!=0u) {
        audio_yield();
    }
}
