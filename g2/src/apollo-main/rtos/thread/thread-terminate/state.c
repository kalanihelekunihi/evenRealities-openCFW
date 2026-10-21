/* Stock FreeRTOS eTaskGetState 0x454b88..0x454c11. */
#include <stdint.h>
extern void *g2_audio_current_task; /* pointer cell 0x20074a20 */
extern void *g2_audio_delayed_list0; /* pointer cell 0x20074a24 */
extern void *g2_audio_delayed_list1; /* pointer cell 0x20074a28 */
extern uint8_t g2_audio_suspended_list[]; /* object 0x20073d4c */
extern uint8_t g2_audio_terminated_list[]; /* object 0x20073d38 */
extern void stock_enter_critical(void); /* 0x4420d0 */
extern void stock_exit_critical(void); /* 0x4420e8 */
extern void offline_assert(void) __attribute__((noreturn));
static uint32_t field32(const void *base,uint32_t offset)
{
    return *(const uint32_t *)((const uint8_t *)base+offset);
}
uint32_t audio_task_state(void *thread)
{
    if (thread==0) offline_assert();
    if (thread==g2_audio_current_task) return 0u;
    stock_enter_critical();
    uint32_t container=field32(thread,20u);
    void *delayed0=g2_audio_delayed_list0;
    void *delayed1=g2_audio_delayed_list1;
    stock_exit_critical();
    if (container==(uint32_t)(uintptr_t)delayed0 ||
        container==(uint32_t)(uintptr_t)delayed1) return 2u;
    if (container==(uint32_t)(uintptr_t)g2_audio_suspended_list) {
        if (field32(thread,40u)!=0u) return 2u;
        if (((const uint8_t *)thread)[108u]==1u) return 2u;
        return 3u;
    }
    if (container==(uint32_t)(uintptr_t)g2_audio_terminated_list ||
        container==0u) return 4u;
    return 1u;
}
