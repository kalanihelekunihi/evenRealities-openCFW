/* Native 0x1000d8ce..0x1000db34, including inactive 0x1000dd64 jump.
 * That jump rejoins at 0x1000da9c: both paths run the second matrix and
 * residual pass. Caller supplies slot/selection/band offsets and scratch.
 */
#include <stdint.h>

extern void gx8002_image_b_process_energy_stat_verified_chunk(
    const uint32_t *,uint32_t);
extern float gx8002_image_b_process_block_scale_verified_chunk(
    const uint32_t *,uint32_t,float *);
extern void gx8002_image_b_process_coeff_update_verified_chunk(
    const uint32_t *,uint32_t,const float [14],float);
extern void gx8002_image_b_complex_matrix_1000e0b8(
    float *,const float *,const float *,int32_t,int32_t,int32_t,int32_t);
extern void gx8002_image_b_process_residual_verified_chunk(
    const uint32_t *,uint32_t);

int gx8002_image_b_process_adapt_stage_verified_chunk(
    const uint32_t *ctx, uint32_t energy_slot_byte_offset,
    uint32_t coefficient_selection_byte_offset,
    uint32_t band_byte_offset, float complex_scratch[14])
{
    int32_t modes=(int32_t)ctx[0x08/4];
    const uint16_t *scratch_flags=(const uint16_t *)(uintptr_t)ctx[0xb4/4];
    int32_t updated_columns=(int32_t)ctx[0x04/4]-1;
    int active=0;
    if (scratch_flags[(uint32_t)modes]!=0u) {
        gx8002_image_b_process_energy_stat_verified_chunk(
            ctx,energy_slot_byte_offset);
        float scale=gx8002_image_b_process_block_scale_verified_chunk(
            ctx,energy_slot_byte_offset,complex_scratch);
        if (updated_columns>0) {
            gx8002_image_b_process_coeff_update_verified_chunk(
                ctx,coefficient_selection_byte_offset,complex_scratch,scale);
            active=1;
        }
    }
    gx8002_image_b_complex_matrix_1000e0b8(
        (float *)(uintptr_t)ctx[0xd0/4],
        (const float *)(uintptr_t)
            (ctx[0xc4/4]+coefficient_selection_byte_offset),
        (const float *)(uintptr_t)ctx[0xcc/4],
        updated_columns,1,updated_columns,modes);
    gx8002_image_b_process_residual_verified_chunk(ctx,band_byte_offset);
    return active;
}
