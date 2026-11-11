#include <stdint.h>
extern uint32_t r1_gomore_packed_sample_get_native(const volatile uint8_t *,uint32_t);
extern uint32_t r1_gomore_packed_sample_set_native(uint32_t,volatile uint8_t *,int32_t);
struct __attribute__((packed,may_alias)) propagate_word { uint32_t value; };

uint32_t r1_gomore_clear_pending_native(uint32_t context)
{
    volatile uint8_t *state=(volatile uint8_t *)(uintptr_t)context;
    if (state[1000]==1) state[1000]=0;
    return context;
}

uint32_t r1_gomore_propagate_packed_status_native(uint32_t context,
        volatile void *unused,volatile void *output)
{
    (void)unused;
    volatile uint8_t *state=(volatile uint8_t *)(uintptr_t)context;
    if (state[1000]) {
        uint32_t slot=((volatile struct propagate_word *)(state+720))->value/30u;
        uint8_t value=(uint8_t)r1_gomore_packed_sample_get_native(state,(slot-2u)%2880u);
        slot=((volatile struct propagate_word *)(state+720))->value/30u;
        (void)r1_gomore_packed_sample_set_native(value,state,(int32_t)((slot-1u)%2880u));
        *(volatile uint8_t *)output=value;
        (void)r1_gomore_clear_pending_native(context);
    }
    return 0;
}
