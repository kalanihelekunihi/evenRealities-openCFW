/* Stock 0x00005dd8 wrapper around the pinned PDL ILO measurement APIs. */
#include "ilo.h"
#include "../clock-selection/clock.h"
#include "cy_sysclk.h"

#define REG(a) (*(volatile uint32_t *)(a))

uint32_t touch_ilo_compensate(uint8_t *context)
{
    if (context == 0) {
        return 1u;
    }

    uint32_t cycles = 500u;
    Cy_SysClk_IloStartMeasurement();
    while (Cy_SysClk_IloCompensate(cycles, &cycles) != CY_SYSCLK_SUCCESS) {
    }
    uint32_t count = REG(0x40030020u);
    Cy_SysClk_IloStopMeasurement();

    uint8_t *internal = *(uint8_t **)(context + 8);
    *(uint32_t *)(internal + 44) = (count << 24) / 1000000u;
    *(uint32_t *)(internal + 32) =
        touch_timer_cycles(*(uint32_t *)(internal + 28), context);
    *(uint32_t *)(internal + 40) =
        touch_timer_cycles(*(uint32_t *)(internal + 36), context);

    cycles = *(uint32_t *)(internal + 32);
    if (*(uint32_t *)(*(uint8_t **)(context + 4) + 8) & 0x20u) {
        cycles = *(uint32_t *)(internal + 40);
    }
    const uint8_t *channel = *(const uint8_t **)(*(const uint8_t **)context + 8);
    volatile uint32_t *hardware = *(volatile uint32_t **)channel;
    hardware[0x70 / 4] &= 0xffff0000u;
    channel = *(const uint8_t **)(*(const uint8_t **)context + 8);
    hardware = *(volatile uint32_t **)channel;
    hardware[0x70 / 4] |= cycles;
    return 0u;
}
