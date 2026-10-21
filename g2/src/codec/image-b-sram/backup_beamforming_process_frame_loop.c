/* Native process 0x1000d6c4..0x1000db5c frame loop after ring setup.
 * The stack locals are explicit so their lifetimes and per-frame increments
 * are visible. This candidate has not yet passed a whole-entry native trace.
 */
#include <stdint.h>

struct gx8002_image_b_process_frame_state {
    uint32_t band_byte_offset,coefficient_offset,coefficient_stride;
    uint32_t selected_offset,selected_stride,frame_index,frame_count;
};
extern int gx8002_image_b_process_frame_advance_verified_chunk(
    struct gx8002_image_b_process_frame_state *);
extern void gx8002_image_b_process_diagonal_frame_verified_chunk(
    const uint32_t *,uint32_t);
extern void gx8002_image_b_process_pack_verified_chunk(
    const uint32_t *,uint32_t);
extern void gx8002_image_b_process_matrix_stage_verified_chunk(
    const uint32_t *,uint32_t,uint32_t,uint32_t);
extern int gx8002_image_b_process_adapt_stage_verified_chunk(
    const uint32_t *,uint32_t,uint32_t,uint32_t,float [14]);

void gx8002_image_b_process_frame_loop_experimental(const uint32_t *ctx)
{
    uint32_t microphones=ctx[0x04/4];
    uint32_t frames=ctx[0x18/4];
    if ((int32_t)frames<=0) return;
    uint32_t selected_row=*(const uint32_t *)(uintptr_t)ctx[0x5c/4];
    struct gx8002_image_b_process_frame_state state={
        .band_byte_offset=0u,
        .coefficient_offset=0u,
        .coefficient_stride=(microphones*2u-2u)*4u,
        .selected_offset=selected_row*microphones*8u,
        .selected_stride=microphones*ctx[0x1c/4]*8u,
        .frame_index=0u,
        .frame_count=frames,
    };
    uint32_t energy_slot_base=selected_row*frames*4u;
    float complex_scratch[14]={0};
    do {
        gx8002_image_b_process_diagonal_frame_verified_chunk(
            ctx,state.selected_offset);
        gx8002_image_b_process_pack_verified_chunk(
            ctx,state.band_byte_offset);
        gx8002_image_b_process_matrix_stage_verified_chunk(
            ctx,state.selected_offset,state.coefficient_offset,
            state.band_byte_offset);
        gx8002_image_b_process_adapt_stage_verified_chunk(
            ctx,energy_slot_base+state.band_byte_offset,
            state.coefficient_offset,state.band_byte_offset,
            complex_scratch);
    } while (gx8002_image_b_process_frame_advance_verified_chunk(&state));
}
