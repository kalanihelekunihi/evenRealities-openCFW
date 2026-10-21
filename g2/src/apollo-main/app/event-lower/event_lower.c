/* Native FreeRTOS event-group create 0x47eb94/0x47ebd8 and task clear
 * 0x47ed10. List init is the exact 0x45607c field layout. */
#include <stdint.h>
extern void *pvPortMalloc(uint32_t); /* selected native 0x456110 */
extern void stock_enter_critical(void); /* selected native 0x4420d0 */
extern void stock_exit_critical(void); /* selected native 0x4420e8 */
extern void offline_assert(void) __attribute__((noreturn));
static void audio_uart_event_list_initialize(uint8_t *p)
{
    uint32_t end=(uint32_t)(uintptr_t)(p+8u);
    *(uint32_t *)(p+4u)=end;
    *(uint32_t *)(p+8u)=UINT32_MAX;
    *(uint32_t *)(p+12u)=end;
    *(uint32_t *)(p+16u)=end;
    *(uint32_t *)p=0u;
}
void *audio_uart_event_static_create(void *storage)
{
    if (!storage) offline_assert();
    uint8_t *event=(uint8_t *)storage;
    *(uint32_t *)event=0u;
    audio_uart_event_list_initialize(event+4u);
    event[28u]=1u;
    return event;
}
void *audio_uart_event_dynamic_create(void)
{
    uint8_t *event=(uint8_t *)pvPortMalloc(32u);
    if (event) {
        *(uint32_t *)event=0u;
        audio_uart_event_list_initialize(event+4u);
        event[28u]=0u;
    }
    return event;
}
uint32_t audio_uart_event_clear_task(void *event,uint32_t flags)
{
    if (!event || (flags&0xff000000u)) offline_assert();
    stock_enter_critical();
    uint32_t previous=*(uint32_t *)event;
    *(uint32_t *)event=previous&~flags;
    stock_exit_critical();
    return previous;
}
