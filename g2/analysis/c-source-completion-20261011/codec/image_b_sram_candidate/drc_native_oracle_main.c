#include <stdint.h>

#ifdef SOURCE_MODE
extern void gx8002_image_b_drc_process_1000e94c(
    const uint32_t *, int16_t *, float);
float gx8002_image_b_power_float_100100a4(float base, float exponent)
{
    (void)base;
    (void)exponent;
    return 1.0f;
}
#endif

int main(void)
{
    uint32_t state[2] = {0u, 8u};
    int16_t samples[8] = {
        0, 30000, 30001, 32767, -30001, -32768, 12345, -12345
    };
#ifdef SOURCE_MODE
    gx8002_image_b_drc_process_1000e94c(state, samples, 0.0f);
#else
    ((void (*)(const uint32_t *, int16_t *, float))
        (uintptr_t)UINT32_C(0x1000e94c))(state, samples, 0.0f);
#endif
#ifdef OUTPUT_INDEX
    return (uint16_t)samples[OUTPUT_INDEX];
#else
    uint32_t hash = UINT32_C(2166136261);
    for (unsigned i = 0; i < 8u; ++i) {
        hash ^= (uint16_t)samples[i];
        hash *= UINT32_C(16777619);
    }
    return (int)(hash & 255u);
#endif
}
