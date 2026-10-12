#include <stdint.h>

extern int32_t gx8002_image_b_audio_out_set_db_1000602c(
    volatile uint8_t *, int32_t);

int main(void)
{
    volatile uint32_t *const trace =
        (volatile uint32_t *)(uintptr_t)0xffffc040u;
    static const int32_t values[] = {-20, -18, -17, -1, 0, 1, 17, 18, 20};
    int32_t (*const native)(volatile uint8_t *, int32_t) =
        (int32_t (*)(volatile uint8_t *, int32_t))(uintptr_t)0x1000602cu;
    for (uint32_t i = 0; i < sizeof(values) / sizeof(values[0]); ++i) {
        volatile uint8_t first[32], second[32];
        for (uint32_t j = 0; j < 32u; ++j) first[j] = second[j] = 0u;
        int32_t native_result = native(first, values[i]);
        int32_t source_result =
            gx8002_image_b_audio_out_set_db_1000602c(second, values[i]);
        uint16_t native_saved =
            *(volatile uint16_t *)(volatile void *)(first + 0x12u);
        uint16_t source_saved =
            *(volatile uint16_t *)(volatile void *)(second + 0x12u);
        trace[0] = i;
        trace[0] = (uint32_t)native_result;
        trace[0] = (uint32_t)source_result;
        trace[0] = native_saved;
        trace[0] = source_saved;
        if (native_result != source_result || native_saved != source_saved)
            return (int32_t)(i + 1u);
    }
    return 0;
}
