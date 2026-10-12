/* Native GSC process 0x1000db34..0x1000db5c outer-frame transition.
 * These fields correspond to live native stack slots, not guessed product
 * defaults. The caller must initialize them from the d46c prologue and
 * d6c4-d726 setup before the first frame.
 */
#include <stdint.h>

struct gx8002_image_b_process_frame_state {
    uint32_t band_byte_offset;       /* stack+0x10 */
    uint32_t coefficient_offset;     /* stack+0x1c */
    uint32_t coefficient_stride;     /* stack+0x44 */
    uint32_t selected_offset;        /* stack+0x20 */
    uint32_t selected_stride;        /* stack+0x40 */
    uint32_t frame_index;            /* stack+0x2c */
    uint32_t frame_count;            /* stack+0x38 */
};

int gx8002_image_b_process_frame_advance_verified_chunk(
    struct gx8002_image_b_process_frame_state *state)
{
    state->band_byte_offset+=4u;
    state->coefficient_offset+=state->coefficient_stride;
    state->selected_offset+=state->selected_stride;
    state->frame_index+=1u;
    return state->frame_count!=state->frame_index;
}
