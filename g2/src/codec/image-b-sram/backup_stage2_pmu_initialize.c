/* Native image-B 0x1000a744..0x1000a77e. Cold/warm status selects
 * 144-byte PMU record clear or replay of retained callback pairs.
 * The record at 0x2002cb88 is source-owned conditional BSS.
 */
#include <stdint.h>

extern uint32_t gx8002_image_b_platform_status_10003fb8(void);
extern void gx8002_image_b_zero_100113c4(void *, uint32_t, uint32_t);
extern volatile uint32_t gx8002_image_b_pmu_record_2002cb88[36];

uint32_t gx8002_image_b_pmu_initialize_1000a744(void)
{
    volatile uint32_t *const record = gx8002_image_b_pmu_record_2002cb88;
    if (gx8002_image_b_platform_status_10003fb8() <= 1u) {
        gx8002_image_b_zero_100113c4((void *)record, 0u, 144u);
        return 1u;
    }
    uint32_t count = record[3];
    for (uint32_t i = 0u; i < count; ++i) {
        uint32_t function = record[20u + i * 2u];
        uint32_t context = record[21u + i * 2u];
        ((void (*)(uint32_t))(uintptr_t)function)(context);
    }
    return 0u;
}
