/* Native GSC angle table traversal 0x1000cb1e..0x1000cbd2.
 * Frame index lives in fr8 as integer bits and increments after every
 * complete angle sweep. The scalar at matrix[angle] is multiplied by frame
 * phase and each microphone index, sent through vector sin then cos, and interleaved into
 * the context+0xa4 complex table. Caller supplies source-owned allocation.
 * This remains a component of the complete 0x1000c6e8 function.
 */
#include <stdint.h>

extern void gx8002_image_b_sin_float_array_1000dee0(
    float *output, const float *input, int count);
extern void gx8002_image_b_cos_float_array_1000df0c(
    float *output, const float *input, int count);

void gx8002_image_b_angle_table_verified_chunk(
    const float *matrix, int32_t angle_count, int32_t mic_count,
    int32_t frame_count, float increment, float *scratch,
    float *sines, float *cosines, float *table)
{
    for (int32_t frame=0; frame<frame_count; ++frame) {
        float phase=(float)frame*increment;
        for (int32_t angle=0; angle<angle_count; ++angle) {
            float angle_scalar=matrix[angle];
            for (int32_t mic=0; mic<mic_count; ++mic) {
                float value=phase*angle_scalar;
                scratch[mic]=value*(float)mic;
            }
            gx8002_image_b_sin_float_array_1000dee0(
                sines,scratch,mic_count);
            gx8002_image_b_cos_float_array_1000df0c(
                cosines,scratch,mic_count);
            float *slot=table+
                ((uint32_t)frame*(uint32_t)angle_count+
                 (uint32_t)angle)*(uint32_t)mic_count*2u;
            for (int32_t mic=0; mic<mic_count; ++mic) {
                slot[2*mic]=sines[mic];
                slot[2*mic+1]=cosines[mic];
            }
        }
    }
}
