/* Decoded angle body 0x1000c746..0x1000c7ea and failure at 0x1000cc34.
 * This is a component of the full GSC angle function, not its provider.
 * Native reads allocator from product operation table 0x2002d7a4; the
 * eventual composed body must supply that source-owned callback. Allocation
 * order and the all-six nonzero check are preserved, including allocations
 * made before an earlier null result is noticed.
 */
#include <stdint.h>
#include "backup_beamforming_angle_work.h"

extern int gx8002_image_b_heap_log_10009934(const char *format, ...);

int gx8002_image_b_angle_allocations_verified_chunk(
    const uint32_t *ctx, void *(*allocate)(uint32_t bytes),
    struct gx8002_image_b_angle_work *work)
{
    uint32_t mic_count=ctx[0x04/4];
    uint32_t angle_count=ctx[0x24/4];
    uint32_t mic_angle_count=mic_count*angle_count;
    work->mic_count=mic_count;
    work->angle_count=angle_count;
    work->mic_angle_count=mic_angle_count;
    work->state_word_0x18=ctx[0x18/4];
    work->state_word_0x30=ctx[0x30/4];
    work->frame_ratio=(float)(int32_t)ctx[0]/(float)(int32_t)ctx[0x14/4];
    union { uint32_t u; float f; } value;
    value.u=ctx[0x20/4]; work->gain=value.f;
    value.u=ctx[0x3c/4]; work->distance=value.f;
    value.u=ctx[0x34/4]; work->alpha=value.f;
    work->angle_vector=allocate(angle_count*4u);
    work->mic_vector_a=allocate(mic_count*4u);
    work->mic_vector_b=allocate(mic_count*4u);
    work->mic_vector_c=allocate(mic_count*4u);
    work->mic_angle_matrix=allocate(mic_angle_count*4u);
    work->angle_vector_b=allocate(angle_count*4u);
    if (!work->angle_vector || !work->mic_vector_a || !work->mic_vector_b ||
        !work->mic_vector_c || !work->mic_angle_matrix ||
        !work->angle_vector_b) {
        (void)gx8002_image_b_heap_log_10009934(
            "[error], malloc x or y_real or y_imag or cosine_x or mic_position failed. %s, %d\n",
            "lvp/vma/lavaliermic/gsc.c", 0x127);
        return 0;
    }
    return 1; /* native success continues at 0x1000c7ee */
}
