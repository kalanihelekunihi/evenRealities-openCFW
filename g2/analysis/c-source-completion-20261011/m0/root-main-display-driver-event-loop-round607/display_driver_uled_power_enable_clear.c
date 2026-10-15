/* Apollo display power helpers 0x4d3952 and 0x4d39e4. Candidate. */
#include <stdint.h>
extern uint32_t display_driver_uled_delay_4807a0(uint32_t);

uint32_t display_driver_uled_poll_480826(uint32_t count,volatile uint32_t *register_addr,
                                          uint32_t mask,uint32_t expected,uint32_t equal) {
    for (;;) {
        uint32_t value=*register_addr & mask;
        if (((uint8_t)equal!=0u && value==expected) ||
            ((uint8_t)equal==0u && value!=expected))return 0u;
        if (count==0u)return 4u;
        --count;
        (void)display_driver_uled_delay_4807a0(1u);
    }
}

uint32_t display_driver_uled_power_enable_4d3952(uint32_t enable) {
    volatile uint32_t *control=(volatile uint32_t *)(uintptr_t)0x40004044u;
    if ((uint8_t)enable==0u) {
        *control=*control & ~0x20u;
        return 0u;
    }
    if ((*control & 0x20u)!=0u)return 0u;
    *control=*control|0x20u;
    return display_driver_uled_poll_480826(100u,
        (volatile uint32_t *)(uintptr_t)0x40004030u,
        0x01000000u,0x01000000u,1u);
}

uint32_t display_driver_uled_power_clear_4d39e4(void) {
    volatile uint32_t *control=(volatile uint32_t *)(uintptr_t)0x40004048u;
    *control=*control & ~1u;
    return 0u;
}
