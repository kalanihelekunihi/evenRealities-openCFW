#include <stdint.h>

extern void gx8002_image_b_flash_callback_100075d0(
    uint32_t, uint32_t, uint32_t *, uint32_t *);

typedef void (*range_fn)(uint32_t, uint32_t, uint32_t *, uint32_t *);

int main(void)
{
    volatile uint32_t *const descriptor =
        (volatile uint32_t *)(uintptr_t)0x20016d60u;
    volatile uint32_t *const trace =
        (volatile uint32_t *)(uintptr_t)0xffffc040u;
    static const uint32_t cases[][4] = {
        {0u, 0u, 0u, 0u},
        {0u, 8192u, 0u, 1u},
        {0u, 8192u, 4095u, 2u},
        {0u, 8192u, 4096u, 4096u},
        {0u, 8192u, 8191u, 2u},
        {0u, 8192u, 8192u, 1u},
        {0u, 4095u, 2000u, 8u},
        {0u, 12288u, 4090u, 50u},
        {0u, 12288u, 100u, 0u},
        {0xffffffffu, 12288u, 100u, 1u},
        {0u, 12288u, 0xfffffffeu, 4u},
    };
    const range_fn native = (range_fn)(uintptr_t)0x100075d0u;
    for (uint32_t i = 0u; i < sizeof(cases) / sizeof(cases[0]); ++i) {
        descriptor[0] = cases[i][0];
        descriptor[1] = cases[i][1];
        uint32_t native_first = 0x12345678u;
        uint32_t native_end = 0xabcdef01u;
        uint32_t source_first = native_first;
        uint32_t source_end = native_end;
        native(cases[i][2], cases[i][3], &native_first, &native_end);
        gx8002_image_b_flash_callback_100075d0(
            cases[i][2], cases[i][3], &source_first, &source_end);
        trace[0] = i;
        trace[0] = native_first;
        trace[0] = native_end;
        trace[0] = source_first;
        trace[0] = source_end;
        if (native_first != source_first || native_end != source_end)
            return (int)(i + 1u);
    }
    return 0;
}
