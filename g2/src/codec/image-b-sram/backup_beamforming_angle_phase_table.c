/* Composes native zero-mode GSC phase table traversal c91a..ca7a.
 * The outer frame counter starts at zero at c936, the inner angle counter
 * at c952, matrix rows advance mic_count*4 bytes, and output slots advance
 * mic_count*8 bytes. The two children preserve source-owned sin/cos calls,
 * C-SKY frecips, and target FMA instruction classes.
 */
#include <stdint.h>

extern void gx8002_image_b_angle_phase_vectors_verified_chunk(
    const float *matrix_row, int32_t mic_count, int32_t frame_index,
    float scaled_distance, float *scratch, float *sines, float *cosines);
extern void gx8002_image_b_angle_normalize_verified_chunk(
    const float *sines, const float *cosines, int32_t mic_count,
    float *complex_pairs);

void gx8002_image_b_angle_phase_table_verified_chunk(
    const float *matrix, int32_t angle_count, int32_t mic_count,
    int32_t frame_count, float scaled_distance, float *scratch,
    float *sines, float *cosines, float *table)
{
    for (int32_t frame=0; frame<frame_count; ++frame) {
        for (int32_t angle=0; angle<angle_count; ++angle) {
            const float *row=matrix+(uint32_t)angle*(uint32_t)mic_count;
            float *slot=table+
                ((uint32_t)frame*(uint32_t)angle_count+
                 (uint32_t)angle)*(uint32_t)mic_count*2u;
            gx8002_image_b_angle_phase_vectors_verified_chunk(
                row,mic_count,frame,scaled_distance,scratch,sines,cosines);
            gx8002_image_b_angle_normalize_verified_chunk(
                sines,cosines,mic_count,slot);
        }
    }
}
