/* Stock 0x605dc: native heart-rate source selection around the shared C
 * range/selection primitive. The raw fields at the boundary are float bits. */
#include <stdint.h>
#include "../../vendor/gomore_primitives/gomore_primitives.h"

extern void r1_gomore_log_native(uint32_t level, uint32_t category,
                                  const char *format, ...);

static float float_from_bits(uint32_t bits)
{
    float value;
    __builtin_memcpy(&value, &bits, sizeof(value));
    return value;
}

static uint32_t bits_from_float(float value)
{
    uint32_t bits;
    __builtin_memcpy(&bits, &value, sizeof(bits));
    return bits;
}

uint32_t r1_gomore_stage_605dc_native(uint32_t state_address,
                                       uint32_t elapsed_updates,
                                       uint32_t direct_address,
                                       uint32_t estimated_address,
                                       uint32_t output_address)
{
    (void)elapsed_updates;
    volatile const uint32_t *estimated =
        (volatile const uint32_t *)(uintptr_t)estimated_address;
    volatile const uint32_t *direct =
        (volatile const uint32_t *)(uintptr_t)direct_address;
    volatile uint32_t *output = (volatile uint32_t *)(uintptr_t)output_address;

    /* Stock converts estimated then direct to double before calling the
     * configured GoMore logger. The format already contains CRLF. */
    float log_estimated = float_from_bits(estimated[0]);
    float log_direct = float_from_bits(direct[0]);
    r1_gomore_log_native(22u, 0u, "[inhr]=%f [enhr]=%f\r\n",
                         (double)log_direct, (double)log_estimated);

    uint32_t direct_bits = direct[0];
    float direct_value = float_from_bits(direct_bits);
    /* The stock reads the state byte only when direct is in range. */
    uint8_t state = gomore_primitives_float_in_encoded_range(direct_value)
        ? *(volatile const uint8_t *)(uintptr_t)state_address : 1u;
    gomore_primitives_hr_candidate candidate = {0};
    if (state != 0u || !gomore_primitives_float_in_encoded_range(direct_value)) {
        candidate.heart_rate = float_from_bits(estimated[0]);
        candidate.quality = estimated[1];
    }
    gomore_primitives_hr_selection selected;
    (void)gomore_primitives_select_heart_rate(state, direct_value,
                                               &candidate, &selected);
    output[0] = bits_from_float(selected.heart_rate);
    output[1] = selected.quality;
    ((volatile uint8_t *)(uintptr_t)output)[8] = selected.source;
    return selected.source;
}
