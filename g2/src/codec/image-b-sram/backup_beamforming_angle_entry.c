/* Decoded entry region 0x1000c6e8..0x1000c744 of the image-B GSC angle
 * function. This helper is intentionally a component of the future complete
 * body, not a replacement definition for entry 0x1000c6e8. Native takes a
 * count in r1, a signed-halfword input pointer in r2, and stores radians to
 * context+0x64 before setting context+0x60. The mismatch edge calls the
 * diagnostic and returns -1 without reading the input or setting ready.
 */
#include <stdint.h>

extern int gx8002_image_b_heap_log_10009934(const char *format, ...);

int gx8002_image_b_angle_entry_verified_prefix(void *state, int count,
                                                const int16_t *degrees)
{
    uint32_t *ctx = (uint32_t *)state;
    int32_t expected = (int32_t)ctx[0x1c / 4];
    if (expected != count) {
        (void)gx8002_image_b_heap_log_10009934(
            "You must set the beamforming_angle_num equal as you set before");
        ctx[0x60 / 4] = 0;
        return -1;
    }
    if (expected > 0) {
        uint32_t target_word = ctx[0x64 / 4];
        float *radians = (float *)(uintptr_t)target_word;
        const float pi = 0x1.921fb6p+1f; /* native 0x40490fdb */
        for (int i = 0; i < expected; ++i)
            radians[i] = ((float)degrees[i] / 180.0f) * pi;
    }
    ctx[0x60 / 4] = 1;
    return 0; /* continue the native body at 0x1000c746 */
}
