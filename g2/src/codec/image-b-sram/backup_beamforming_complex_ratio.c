/* Complete native shared GSC arithmetic leaf 0x1000e1e8..0x1000e238.
 * Inputs are two adjacent binary32 values in each source pair. The native
 * body forms a dot product and an oriented cross product, each divided by
 * a separately evaluated squared magnitude of the second pair. It does
 * not check for a zero denominator or alter the FPU exception state.
 */
#include <stdint.h>

void gx8002_image_b_complex_ratio_1000e1e8(
    float output[2], const float first[2], const float second[2])
{
    float c=second[0], d=second[1];
    float a=first[0], b=first[1];
    volatile float real_product=d*b;
    float real_numerator=real_product+c*a;
    volatile float real_square=d*d;
    float real_denominator=real_square+c*c;
    output[0]=real_numerator/real_denominator;

    /* Reloads retain the native second quotient's independent operations. */
    c=second[0]; d=second[1];
    a=first[0]; b=first[1];
    volatile float imaginary_product=d*a;
    float imaginary_numerator=c*b-imaginary_product;
    volatile float imaginary_square=d*d;
    float imaginary_denominator=imaginary_square+c*c;
    output[1]=imaginary_numerator/imaginary_denominator;
}
