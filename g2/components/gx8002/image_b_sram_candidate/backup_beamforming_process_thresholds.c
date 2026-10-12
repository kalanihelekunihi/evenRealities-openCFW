/* Native GSC process 0x1000d5bc..0x1000d648. For each eligible spectral
 * band, divide two complex halfword pairs and increment the ring-row
 * counter only when the imaginary ratio lies strictly between the two
 * corresponding coefficient bounds. This is a process slice, not d46c.
 */
#include <stdint.h>

extern void gx8002_image_b_complex_ratio_1000e1e8(
    float output[2], const float first[2], const float second[2]);

void gx8002_image_b_process_thresholds_verified_chunk(
    const int16_t *first, const int16_t *second,
    const float *coefficient_rows, int16_t *ring_row,
    int32_t first_band, int32_t final_band)
{
    for (int32_t band=first_band;band<=final_band;++band) {
        /* Native r1 points to stack+0x5c (the second stream); r2 points
         * to stack+0x64 (the first stream). */
        float numerator[2]={ (float)(uint16_t)second[0],
                             (float)(uint16_t)second[1] };
        float denominator[2]={ (float)(uint16_t)first[0],
                               (float)(uint16_t)first[1] };
        float quotient[2];
        gx8002_image_b_complex_ratio_1000e1e8(
            quotient,numerator,denominator);
        float imaginary=quotient[1];
        if (coefficient_rows[0]<imaginary && imaginary<coefficient_rows[8])
            ring_row[1]=(int16_t)((uint16_t)ring_row[1]+1u);
        first+=2;
        second+=2;
        coefficient_rows+=12;
    }
}
