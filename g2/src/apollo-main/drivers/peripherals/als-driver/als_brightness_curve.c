/* ALS brightness curve, stock driver\sensor\als\als.c.
 * Native 0x4ad9ea..0x4ada02, 0x4add02..0x4add8c, 0x4adec4..0x4adf04,
 * 0x4adf34..0x4adf74 and 0x4ae282..0x4ae2b6; ROM table 0x730e24.
 *
 * A reading maps to the first table row whose threshold is >= the reading.
 * The row percent is then scaled about the first row's percent (35) by the
 * learned Q10 factor at 0x20000064 (1024 = 1.0, learned range 614..1434):
 *     target = clamp(35 + ((percent - 35) * scale + 512) >> 10, 35, 100).
 * The last row is never scaled. audio_als_apply_previous (0x4add8c,
 * als-calculation) stores index, nominal and target from these helpers.
 *
 * Note: als-calculation/display_als_calculation.c still carries private
 * static copies of 0x4add02..0x4add6a and of this table. */
#include <stdbool.h>
#include <stdint.h>
#include "g2_als.h"

#define FULL_PERCENT 100u
#define Q10_HALF 0x200u

const g2_als_curve_step_t g2_als_curve_table[G2_ALS_CURVE_STEPS] = {
    {10u, 35u}, {200u, 50u}, {400u, 70u}, {1000u, 70u}, {1300u, 100u}, {0xffffffffu, 100u},
}; /* ROM 0x730e24 */

uint32_t als_function_03(uint32_t percent)
{
    uint32_t first = audio_als_first_curve_percent_4ad9e2();
    if ((int32_t)percent < (int32_t)first)
        return first;
    if ((int32_t)percent > (int32_t)FULL_PERCENT)
        return FULL_PERCENT;
    return percent;
}

/* Index of the first row whose threshold is >= lux; 5 if none. */
uint32_t als_function_14(uint32_t lux)
{
    uint32_t i;
    for (i = 0u; i < G2_ALS_CURVE_STEPS; i++)
        if (g2_als_curve_table[i].threshold >= lux)
            return i;
    return G2_ALS_CURVE_STEPS - 1u;
}

uint32_t als_function_15(uint32_t index)
{
    return g2_als_curve_table[index].percent;
}

uint32_t als_function_16(uint32_t lux)
{
    return als_function_15(als_function_14(lux));
}

/* Scale a curve percent about the first row's percent by a Q10 factor. */
uint32_t als_function_17(uint32_t percent, uint32_t scale_q10)
{
    uint32_t first = audio_als_first_curve_percent_4ad9e2();
    if (first >= percent)
        return first;
    uint64_t product = (uint64_t)scale_q10 * (percent - first) + Q10_HALF;
    return als_function_03((uint32_t)(product >> 10) + first);
}

uint32_t als_function_18(uint32_t index)
{
    uint32_t percent = als_function_15(index);
    if (index + 1u >= G2_ALS_CURVE_STEPS)
        return FULL_PERCENT;
    return als_function_17(percent, audio_als_scale_active);
}

/* Drop the learned scale back to its reset value and recompute the target
 * from the filtered reading (or the last raw one when none is filtered). */
void als_function_22(void)
{
    uint32_t lux = audio_als_active_previous != 0u ? audio_als_active_previous
                                                  : audio_als_default_previous;
    audio_als_scale_active = audio_als_scale_clamped;
    audio_als_manual_target_count = 0u;
    audio_als_scale_shadow = audio_als_scale_active;
    audio_als_recompute_pending = 0u;
    audio_als_apply_previous(lux);
}

/* True in the two darkest curve bands when the band-1 level (scaled) is not
 * below the target nor the current brightness: brighten in 2% steps. */
bool als_function_24(void)
{
    if (audio_als_curve_index >= 2u)
        return false;
    uint32_t level = als_function_17(als_function_15(1u), audio_als_scale_active);
    return level >= audio_als_curve_adjusted && level >= audio_als_manual_level;
}

/* Move current one step (at most `step`) toward target, capped at 100. */
uint32_t als_function_30(uint32_t target, uint32_t current, uint32_t step)
{
    if (current < target) {
        if (current < FULL_PERCENT - step) {
            if (target >= current + step)
                target = current + step;
        } else if (target > FULL_PERCENT) {
            target = FULL_PERCENT;
        }
    } else if (target < current && current >= step) {
        if (current - step >= target)
            target = current - step;
    }
    return target;
}
