#include <stdint.h>

/* Native 0x319ea0..0x319ee8: release the record's two held WSF buffers
 * (+0xa48 and +0x970 point 4 bytes past the buffer header) and clear the
 * slots, count down the init state when the record was counted (+59),
 * and decrement the active-record count at 0x805a72. */
extern uint32_t opencfw_em9305_wsf_event_release(uintptr_t);
extern uint32_t opencfw_em9305_init_state_count_down_30e49c(void);

void opencfw_em9305_child_319ea0(uintptr_t record)
{
    volatile uint32_t *slot=(volatile uint32_t *)(record+0xa48u);
    if(*slot!=0u) {
        (void)opencfw_em9305_wsf_event_release(*slot-4u);
        *slot=0u;
    }
    slot=(volatile uint32_t *)(record+0x970u);
    if(*slot!=0u) {
        (void)opencfw_em9305_wsf_event_release(*slot-4u);
        *slot=0u;
    }
    if(*(volatile uint8_t *)(record+59u)!=0u)
        (void)opencfw_em9305_init_state_count_down_30e49c();
    volatile uint8_t *count=(volatile uint8_t *)(uintptr_t)0x805a72u;
    *count=(uint8_t)(*count-1u);
}
