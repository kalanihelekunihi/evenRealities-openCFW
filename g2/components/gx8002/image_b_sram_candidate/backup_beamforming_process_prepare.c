/* Native GSC process 0x1000d548..0x1000d5bc: first scratch/ring clear.
 * The product global at 0x2002d7a0 is supplied as an observed word by the
 * future full process caller. This chunk does not substitute a ring value.
 * The native unsigned division by ctx+0x48 is intentionally unguarded.
 */
#include <stdint.h>

extern void gx8002_image_b_dsp_clear_1000f1ac(
    uint32_t value, int16_t *destination, uint32_t count);

struct gx8002_image_b_process_prepare {
    uint32_t first_threshold_address;  /* stack +0x0c */
    uint32_t second_threshold_address; /* stack +0x10 */
    uint32_t coefficient_address;       /* stack +0x40 */
    uint32_t ring_row_address;          /* native r4 */
};

void gx8002_image_b_process_prepare_verified_chunk(
    const uint32_t *ctx, uint32_t observed_ring_counter,
    uint32_t mode_count, int32_t active_stages,
    struct gx8002_image_b_process_prepare *out)
{
    out->first_threshold_address=ctx[0x78/4]+36u;
    out->second_threshold_address=ctx[0x7c/4]+36u;
    out->coefficient_address=ctx[0xa4/4]+mode_count*48u+12u;
    gx8002_image_b_dsp_clear_1000f1ac(
        0u,(int16_t *)(uintptr_t)ctx[0xb4/4],(uint32_t)active_stages+1u);
    out->ring_row_address=0u;
    if (active_stages>0) {
        uint32_t row=observed_ring_counter/ctx[0x48/4];
        row=observed_ring_counter-row*ctx[0x48/4];
        out->ring_row_address=ctx[0xac/4]+row*ctx[0x1c/4]*2u;
        gx8002_image_b_dsp_clear_1000f1ac(
            0u,(int16_t *)(uintptr_t)out->ring_row_address,
            ctx[0x1c/4]);
    }
}
