/* Native GSC process 0x1000d4ec..0x1000d548 and 0x1000dd80..0x1000ddd4.
 * This selects the matrix/FFT working band from the binary32 context field
 * at +0x34. It is a process-core slice, not a definition for 0x1000d46c.
 * The unordered branch preserves the native product fields rather than
 * inventing a coefficient band for a NaN input.
 */
#include <stdint.h>

struct gx8002_image_b_process_band {
    uint32_t mode_count;         /* native stack +0x1c */
    uint32_t coefficient_bytes;  /* native r3 at 0x1000d548 */
    uint32_t band_index;         /* native r7 at 0x1000d548 */
    uint32_t active_stages;      /* native r5 at 0x1000d548 */
};

typedef union { uint32_t u; float f; } gx8002_process_float_word;

void gx8002_image_b_process_band_verified_chunk(
    const uint32_t *ctx, struct gx8002_image_b_process_band *out)
{
    gx8002_process_float_word alpha={.u=ctx[0x34/4]};
    const gx8002_process_float_word t01={.u=UINT32_C(0x3c23d70a)};
    const gx8002_process_float_word t03={.u=UINT32_C(0x3cf5c28f)};
    const gx8002_process_float_word t06={.u=UINT32_C(0x3d75c28f)};
    const gx8002_process_float_word t09={.u=UINT32_C(0x3db851ec)};
    out->active_stages=ctx[0x08/4];
    if (alpha.f<=t01.f) {
        out->mode_count=9u;
        out->coefficient_bytes=36u;
        out->band_index=59u;
    } else if (alpha.f>t01.f && alpha.f<=t03.f) {
        out->mode_count=9u;
        out->coefficient_bytes=36u;
        out->band_index=89u;
    } else if (alpha.f>t03.f && alpha.f<=t06.f) {
        out->mode_count=9u;
        out->coefficient_bytes=36u;
        out->band_index=49u;
    } else if (alpha.f>t06.f && alpha.f<=t09.f) {
        out->mode_count=9u;
        out->coefficient_bytes=36u;
        out->band_index=29u;
    } else if (alpha.f>t09.f) {
        out->mode_count=9u;
        out->coefficient_bytes=36u;
        out->band_index=29u;
    } else {
        /* All native ordered comparisons were false (including NaN). */
        out->mode_count=ctx[0x4c/4];
        out->coefficient_bytes=ctx[0x4c/4]*4u;
        out->band_index=ctx[0x50/4];
    }
}
