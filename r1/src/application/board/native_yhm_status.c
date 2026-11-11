#include <stdint.h>
extern uint32_t r1_yhm_ready_native(void);
extern uint32_t r1_yhm_register_read_native(uint32_t,uint32_t,uint8_t *);
uint32_t r1_yhm_status_native(void)
{
    if (!r1_yhm_ready_native()) return 12;
    /* A non-writing provider uses the same status as not-ready, instead of
     * a saved caller scratch byte. Raw transport status remains ignored. */
    uint8_t value=0xc0;
    (void)r1_yhm_register_read_native(6,1,&value);
    uint32_t status=value>>4;
    return status==14 ? 17 : status;
}
