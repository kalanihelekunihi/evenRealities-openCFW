/* Complete native GSC complex leaf 0x1000e23c..0x1000e288.
 * Its two outputs are the negative of the ordinary complex quotient. The
 * native `fnmscs` and `fnmuls` signs were checked against CK804EF GCC's
 * emitted instructions for the corresponding C expressions. Reciprocal
 * uses the source-owned native `frecips` leaf, with no zero guard.
 */
#include <stdint.h>

extern float gx8002_image_b_native_reciprocal_f32(float x);

void gx8002_image_b_complex_negative_ratio_1000e23c(
    float output[2], const float first[2], const float second[2])
{
    float c=second[0], d=second[1];
    float a=first[0], b=first[1];
    float denominator=d*d+c*c;
    float reciprocal=gx8002_image_b_native_reciprocal_f32(denominator);
    volatile float real_product=d*b;
    float negative_real_sum=-(real_product+c*a);
    output[0]=negative_real_sum*reciprocal;

    a=first[0]; b=first[1];
    c=second[0]; d=second[1];
    volatile float imaginary_product=a*d;
    float reverse_difference=b*c-imaginary_product;
    output[1]=-(reverse_difference*reciprocal);
}
