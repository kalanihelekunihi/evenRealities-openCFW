/* Native image-B timer setup 0x10004fcc..0x10005064 and timer IRQ
 * 0x100050cc..0x1000513c. Pinned NationalChip gx_delay/timer interfaces
 * corroborate the 10 records of 36 bytes and 1 MHz prescale. The records
 * occupy exact BSS at 0x200174bc and are deliberately a linker contract.
 */
#include <stdint.h>

extern void gx8002_image_b_platform_gate_10003be8(uint32_t, uint32_t);
extern uint32_t gx8002_image_b_clock_frequency_10003cf0(uint32_t);
extern void gx8002_image_b_zero_100113c4(void *, uint32_t, uint32_t);
extern void gx8002_image_b_request_irq_10004844(
    uint32_t, int32_t (*)(int32_t, void *), uint32_t);
extern uint64_t gx8002_image_b_time_10005070(void);
extern volatile uint32_t gx8002_image_b_timer_records_200174bc[90];

static volatile uint32_t *const timer =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0400000);

void gx8002_image_b_timer_set_prescale_10004fcc(void)
{
    timer[0x50u / 4u] = 1u;
    timer[0x50u / 4u] = 0u;
    timer[0x60u / 4u] = 1u;
    uint32_t count = gx8002_image_b_clock_frequency_10003cf0(23u) /
                     UINT32_C(1000000);
    timer[0x64u / 4u] = count - 1u;
    timer[0x68u / 4u] = 0u;
    timer[0x50u / 4u] = 2u;
}

int32_t gx8002_image_b_timer_irq_100050cc(int32_t irq, void *context)
{
    (void)irq;
    (void)context;
    for (uint32_t index = 0u; index < 10u; ++index) {
        volatile uint32_t *const record =
            gx8002_image_b_timer_records_200174bc + index * 9u;
        if (record[7] == 0u)
            continue;
        uint64_t now = gx8002_image_b_time_10005070();
        uint64_t deadline = (uint64_t)record[6] << 32 | record[5];
        if (now < deadline)
            continue;
        ((void (*)(uint32_t))(uintptr_t)record[0])(record[1]);
        uint32_t step = record[2] * 1000u;
        int64_t signed_step = (int64_t)(int32_t)step;
        record[3] = (uint32_t)now;
        record[4] = (uint32_t)(now >> 32);
        deadline = now + (uint64_t)signed_step;
        record[5] = (uint32_t)deadline;
        record[6] = (uint32_t)(deadline >> 32);
        if (record[8] == 0u)
            record[7] = 0u;
    }
    timer[0] = timer[0] | 1u;
    return 0;
}

void gx8002_image_b_platform_retention_10004ffc(void)
{
    gx8002_image_b_platform_gate_10003be8(23u, 1u);
    timer[0x10u / 4u] = 1u;
    timer[0x10u / 4u] = 0u;
    timer[0x20u / 4u] = 3u;
    uint32_t count = gx8002_image_b_clock_frequency_10003cf0(23u) /
                     UINT32_C(1000000);
    timer[0x24u / 4u] = count - 1u;
    timer[0x28u / 4u] = ~UINT32_C(999);
    timer[0x10u / 4u] = 2u;
    gx8002_image_b_zero_100113c4(
        (void *)gx8002_image_b_timer_records_200174bc, 0u, 360u);
    gx8002_image_b_request_irq_10004844(
        14u, gx8002_image_b_timer_irq_100050cc, 0u);
    gx8002_image_b_timer_set_prescale_10004fcc();

    volatile uint32_t *const secondary =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0400080);
    secondary[0x10u / 4u] = 1u;
    secondary[0x10u / 4u] = 0u;
    secondary[0x20u / 4u] = 1u;
    secondary[0x24u / 4u] = 0u;
    secondary[0x28u / 4u] = 0u;
    secondary[0x10u / 4u] = 2u;
}
