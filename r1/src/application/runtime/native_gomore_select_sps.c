/* Stock 0x610c8: native SPS source selection around the shared C primitive. */
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

uint32_t r1_gomore_stage_610c8_native(uint32_t state_address,
                                       uint32_t elapsed_updates,
                                       uint32_t reference_address,
                                       uint32_t gpd_address,
                                       uint32_t accelerometer_address,
                                       uint32_t output_address)
{
    (void)state_address;
    (void)elapsed_updates;
    volatile const uint32_t *reference =
        (volatile const uint32_t *)(uintptr_t)reference_address;
    volatile const uint32_t *gpd =
        (volatile const uint32_t *)(uintptr_t)gpd_address;
    volatile const uint32_t *accelerometer =
        (volatile const uint32_t *)(uintptr_t)accelerometer_address;
    volatile uint32_t *output = (volatile uint32_t *)(uintptr_t)output_address;

    /* This native logger receives three pointers to float fields. */
    r1_gomore_log_native(23u, 2u, "[SPS] sRef:%f sGpd:%f sAcc:%f",
                         reference_address, gpd_address, accelerometer_address);

    float ref_value = float_from_bits(reference[0]);
    float gpd_value = -1.0f;
    float accelerometer_value = -1.0f;
    if (!(ref_value >= 0.0f)) {
        gpd_value = float_from_bits(gpd[0]);
        if (!(gpd_value >= 0.0f)) {
            accelerometer_value = float_from_bits(accelerometer[0]);
        }
    }
    gomore_primitives_sps_selection selected;
    uint32_t status = gomore_primitives_sps_select_available(
        ref_value, gpd_value, accelerometer_value, 0u, 0, &selected);
    output[0] = bits_from_float(selected.value);
    ((volatile uint8_t *)(uintptr_t)output)[8] = selected.source;
    output[1] = bits_from_float(selected.reciprocal_hours);
    ((volatile uint8_t *)(uintptr_t)output)[9] =
        ((volatile const uint8_t *)(uintptr_t)accelerometer_address)[4];
    return status;
}
