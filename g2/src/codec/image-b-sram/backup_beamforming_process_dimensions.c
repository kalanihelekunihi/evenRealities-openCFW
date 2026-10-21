/* GSC process 0x1000d47e..0x1000d4e6: frame-local integer dimensions.
 * This is a source slice, not the complete 0x1000d46c process provider.
 * All arithmetic here is the native 32-bit wraparound arithmetic. The
 * signed branch decisions that consume these values remain in the caller.
 */
#include <stdint.h>

struct gx8002_image_b_process_dimensions {
    uint32_t microphones;          /* native stack +0x14, ctx +0x04 */
    uint32_t stages;               /* stack +0x24, ctx +0x08 */
    uint32_t frames;               /* stack +0x38, ctx +0x18 */
    uint32_t angles;               /* stack +0x28, ctx +0x1c */
    uint32_t twice_frames;         /* stack +0x44 */
    uint32_t twice_microphones;    /* stack +0x4c */
    uint32_t microphones_minus_one;/* stack +0x18 */
    uint32_t twice_microphones_minus_two; /* stack +0x3c */
    uint32_t twice_mic_angle;      /* stack +0x48 */
    uint32_t stage_shift_product;  /* stack +0x50, ctx +0x10 * stages */
    uint32_t mode_count;           /* stack +0x1c, ctx +0x4c */
    uint32_t angle_defaults;       /* stack +0x2c, ctx +0xa8 */
};

void gx8002_image_b_process_dimensions_verified_chunk(
    const uint32_t *ctx, struct gx8002_image_b_process_dimensions *out)
{
    uint32_t microphones=ctx[0x04/4];
    uint32_t stages=ctx[0x08/4];
    uint32_t frames=ctx[0x18/4];
    uint32_t angles=ctx[0x1c/4];
    out->microphones=microphones;
    out->stages=stages;
    out->frames=frames;
    out->angles=angles;
    out->twice_frames=frames+frames;
    out->twice_microphones=microphones+microphones;
    out->microphones_minus_one=microphones-1u;
    out->twice_microphones_minus_two=(microphones+microphones)-2u;
    out->twice_mic_angle=(microphones*angles)*2u;
    out->stage_shift_product=ctx[0x10/4]*stages;
    out->mode_count=ctx[0x4c/4];
    out->angle_defaults=ctx[0xa8/4];
}
