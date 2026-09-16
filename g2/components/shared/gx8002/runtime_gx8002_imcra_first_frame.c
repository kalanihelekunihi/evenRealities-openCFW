/* SPDX-License-Identifier: MIT
 * Development reconstruction 0x4ef88..0x4f0d4. Valid dimensions/radius required.
 * The caller continues into prior estimation after this initialization.
 * Edge copies preserve float bits; the interior uses ordered kernel MACs.
 */
#include <stdint.h>
#include <stddef.h>
extern void *open_cfw_gx8002_memcpy(void *, const void *, size_t);
void open_cfw_gx8002_imcra_first_frame(volatile uint32_t *state, int32_t bins)
{
    int32_t radius = (int32_t)state[29];
    uint32_t smooth_address = state[30];
    volatile uint32_t *smooth_bits = (volatile uint32_t *)(uintptr_t)smooth_address;
    if (radius > 0) {
        const volatile uint32_t *power = (const volatile uint32_t *)(uintptr_t)state[16];
        for (int32_t i = 0; i < radius; ++i) smooth_bits[i] = power[i];
    }
    int32_t end = bins - radius;
    if (radius < end) {
        volatile float *smooth = (volatile float *)(uintptr_t)smooth_address;
        for (int32_t i = radius; i < end; ++i) {
            const volatile float *kernel = (const volatile float *)(uintptr_t)state[43];
            const volatile float *power = (const volatile float *)(uintptr_t)state[16];
            float sum = 0.0f;
            for (int32_t j = 0; j <= radius*2; ++j) {
                float coefficient = kernel[j];
                float sample = power[i-radius+j];
                sum = sum + coefficient * sample;
            }
            smooth[i] = sum;
        }
    }
    if (end < bins) {
        const volatile uint32_t *power = (const volatile uint32_t *)(uintptr_t)state[16];
        for (int32_t i = end; i < bins; ++i) smooth_bits[i] = power[i];
    }
    uint32_t destination = state[31];
    open_cfw_gx8002_memcpy((void *)(uintptr_t)destination,
                         (const void *)(uintptr_t)smooth_address, (uint32_t)bins*4u);
#define INITIAL_COPY(destination_index, source_index) do { \
    uint32_t bytes = state[7]*4u; \
    uint32_t source = state[source_index]; \
    uint32_t target = state[destination_index]; \
    open_cfw_gx8002_memcpy((void *)(uintptr_t)target, (const void *)(uintptr_t)source, bytes); \
} while (0)
    INITIAL_COPY(32,30);
    INITIAL_COPY(33,30);
    INITIAL_COPY(35,30);
    INITIAL_COPY(37,30);
    INITIAL_COPY(41,16);
    INITIAL_COPY(40,16);
#undef INITIAL_COPY
    int32_t histories = (int32_t)state[27];
    for (int32_t i = 0; i < histories; ++i) {
        uint32_t count = state[7];
        uint32_t offset = count*(uint32_t)i*4u;
        uint32_t target = state[34];
        uint32_t source = state[16];
        open_cfw_gx8002_memcpy((void *)(uintptr_t)(target+offset),
                             (const void *)(uintptr_t)source, count*4u);
        count = state[7];
        offset = count*(uint32_t)i*4u;
        target = state[36];
        source = state[16];
        open_cfw_gx8002_memcpy((void *)(uintptr_t)(target+offset),
                             (const void *)(uintptr_t)source, count*4u);
        histories = (int32_t)state[27];
    }
}
