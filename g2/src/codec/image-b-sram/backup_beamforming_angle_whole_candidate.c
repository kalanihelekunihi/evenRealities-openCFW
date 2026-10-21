/* Experimental composition of native GSC angle CFG 0x1000c6e8..0x1000cc1a.
 * It remains under a distinct symbol until path-complete native/C effects
 * have been qualified. Genuine product operation table and output allocation
 * stay as typed source/link contracts; no default memory is invented.
 */
#include <stdint.h>
#include "backup_beamforming_angle_work.h"

extern volatile uint32_t gx8002_image_b_dsp_config_2002d7a4[4];
extern int gx8002_image_b_angle_entry_verified_prefix(
    void *state, int count, const int16_t *degrees);
extern int gx8002_image_b_angle_allocations_verified_chunk(
    const uint32_t *ctx, void *(*allocate)(uint32_t),
    struct gx8002_image_b_angle_work *work);
extern void gx8002_image_b_angle_geometry_verified_chunk(
    const uint32_t *ctx, struct gx8002_image_b_angle_geometry *out);
extern float gx8002_image_b_angle_spacing_verified_chunk(
    uint32_t mic_count, float distance, float increment, float *positions);
extern void gx8002_image_b_angle_sine_matrix_verified_chunk(
    const float *radians, int32_t angle_count, const float *positions,
    int32_t mic_count, float *scratch, float *matrix);
extern void gx8002_image_b_angle_nonzero_mode_verified_chunk(
    const float *radians, uint32_t angle_count, float *angle_vector,
    float *matrix);
extern void gx8002_image_b_sin_float_array_1000dee0(
    float *output, const float *input, int count);
extern void gx8002_image_b_angle_sweep_verified_chunk(
    int32_t angle_count, int32_t mic_count, float steering_radians,
    const float *positions, float *scratch, float *matrix);
extern void gx8002_image_b_angle_linear_sweep_verified_chunk(
    int32_t angle_count, float steering_radians,
    float *angle_vector, float *matrix);
extern void gx8002_image_b_angle_phase_table_verified_chunk(
    const float *matrix, int32_t angle_count, int32_t mic_count,
    int32_t frame_count, float scaled_distance, float *scratch,
    float *sines, float *cosines, float *table);
extern void gx8002_image_b_angle_table_verified_chunk(
    const float *matrix, int32_t angle_count, int32_t mic_count,
    int32_t frame_count, float increment, float *scratch,
    float *sines, float *cosines, float *table);

int gx8002_image_b_beamforming_angles_whole_candidate(
    void *state, int angle_count, const int16_t *degrees)
{
    uint32_t *ctx=(uint32_t *)state;
    int first=gx8002_image_b_angle_entry_verified_prefix(
        state,angle_count,degrees);
    if (first<0) return first;
    void *(*allocate)(uint32_t)=(void *(*)(uint32_t))
        (uintptr_t)gx8002_image_b_dsp_config_2002d7a4[0];
    void (*release)(void *)=(void (*)(void *))
        (uintptr_t)gx8002_image_b_dsp_config_2002d7a4[3];
    struct gx8002_image_b_angle_work w;
    if (!gx8002_image_b_angle_allocations_verified_chunk(ctx,allocate,&w))
        return 0;
    struct gx8002_image_b_angle_geometry g;
    gx8002_image_b_angle_geometry_verified_chunk(ctx,&g);
    int32_t mic_count=(int32_t)w.mic_count;
    int32_t frames=(int32_t)w.state_word_0x18;
    float *matrix=(float *)w.mic_angle_matrix;
    float *scratch=(float *)w.mic_vector_a;
    float *sines=(float *)w.mic_vector_b;
    float *cosines=(float *)w.mic_vector_c;
    float *angle_vector=(float *)w.angle_vector;
    float *positions=(float *)w.angle_vector_b;
    float *radians=(float *)(uintptr_t)ctx[0x64/4];
    float *table=(float *)(uintptr_t)ctx[0xa4/4];
    uint32_t ready=ctx[0x60/4];

    if (w.state_word_0x30 != 0) {
        if (ready != 0) {
            if (angle_count>0)
                gx8002_image_b_angle_nonzero_mode_verified_chunk(
                    radians,(uint32_t)angle_count,angle_vector,matrix);
            else
                gx8002_image_b_sin_float_array_1000dee0(
                    matrix,angle_vector,angle_count);
        } else {
            gx8002_image_b_angle_linear_sweep_verified_chunk(
                angle_count,g.steering_radians,angle_vector,matrix);
        }
        if (frames>0 && angle_count>0)
            gx8002_image_b_angle_table_verified_chunk(
                matrix,angle_count,mic_count,frames,g.increment,
                angle_vector,sines,cosines,table);
    } else {
        float scaled=gx8002_image_b_angle_spacing_verified_chunk(
            w.mic_count,w.distance,g.increment,positions);
        if (ready != 0) {
            if (angle_count>0)
                gx8002_image_b_angle_sine_matrix_verified_chunk(
                    radians,angle_count,positions,mic_count,scratch,matrix);
        } else if (angle_count>0) {
            gx8002_image_b_angle_sweep_verified_chunk(
                angle_count,mic_count,g.steering_radians,positions,
                scratch,matrix);
        }
        if (frames>0 && angle_count>0)
            gx8002_image_b_angle_phase_table_verified_chunk(
                matrix,angle_count,mic_count,frames,scaled,
                scratch,sines,cosines,table);
    }

    release(w.angle_vector);
    release(w.mic_vector_a);
    release(w.mic_vector_b);
    release(w.mic_vector_c);
    release(w.mic_angle_matrix);
    release(w.angle_vector_b);
    return 0;
}
