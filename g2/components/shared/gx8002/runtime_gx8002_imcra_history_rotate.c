/* SPDX-License-Identifier: MIT
 * Development reconstruction 0x4ed32 gate and 0x4ee6a..0x4ef6e rotation.
 * Preconditions: frame >= 0, frame < INT32_MAX; positive period/history count;
 * valid bin arrays. Helper mutation must preserve these preconditions.
 * Returns with state ready for synthesis; not a complete processing function.
 */
#include <stdint.h>
#include <stddef.h>
extern void *open_cfw_gx8002_memcpy(void *, const void *, size_t);
void open_cfw_gx8002_imcra_history_rotate(volatile uint32_t *state,
                                        int32_t bins, int32_t frame)
{
    int32_t period = (int32_t)state[28];
    if ((frame + 1) % period != 0) return;
    int32_t epoch = frame / period;
    int32_t histories = (int32_t)state[27];
    int32_t slot = epoch % histories;
    uint32_t destination = state[34];
    uint32_t source = state[35];
    open_cfw_gx8002_memcpy((void *)(uintptr_t)(destination+(uint32_t)bins*(uint32_t)slot*4u),
                         (const void *)(uintptr_t)source,(uint32_t)bins*4u);
    uint32_t count = state[7];
    destination = state[36];
    source = state[37];
    open_cfw_gx8002_memcpy((void *)(uintptr_t)(destination+count*(uint32_t)slot*4u),
                         (const void *)(uintptr_t)source,count*4u);
    count = state[7];
    source = state[34];
    destination = state[32];
    open_cfw_gx8002_memcpy((void *)(uintptr_t)destination,(const void *)(uintptr_t)source,count*4u);
    count = state[7];
    source = state[36];
    destination = state[33];
    open_cfw_gx8002_memcpy((void *)(uintptr_t)destination,(const void *)(uintptr_t)source,count*4u);
    histories = (int32_t)state[27];
    bins = (int32_t)state[7];
    uint32_t first_history = state[34] + (uint32_t)bins*4u;
    uint32_t second_history = state[36] + (uint32_t)bins*4u;
    for (int32_t h = 1; h < histories; ++h) {
        if (bins > 0) {
            volatile float *first_minimum = (volatile float *)(uintptr_t)state[32];
            volatile float *second_minimum = (volatile float *)(uintptr_t)state[33];
            const volatile float *first = (const volatile float *)(uintptr_t)first_history;
            const volatile float *second = (const volatile float *)(uintptr_t)second_history;
            for (int32_t i = 0; i < bins; ++i) {
                float previous = first_minimum[i];
                float current = first[i];
                if (previous < current) current = previous;
                first_minimum[i] = current;
                previous = second_minimum[i];
                current = second[i];
                if (previous < current) current = previous;
                second_minimum[i] = current;
            }
        }
        first_history += (uint32_t)bins*4u;
        second_history += (uint32_t)bins*4u;
    }
    source = state[30];
    destination = state[35];
    open_cfw_gx8002_memcpy((void *)(uintptr_t)destination,(const void *)(uintptr_t)source,(uint32_t)bins*4u);
    count = state[7];
    source = state[31];
    destination = state[37];
    open_cfw_gx8002_memcpy((void *)(uintptr_t)destination,(const void *)(uintptr_t)source,count*4u);
}
