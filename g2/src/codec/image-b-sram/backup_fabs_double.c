/* Native image-B 0x1000fc58 clears binary64 sign bit and returns. */
#include <stdint.h>
typedef union { double value; uint64_t bits; } image_b_fabs_word;
double gx8002_image_b_fabs_double_1000fc58(double x)
{
    image_b_fabs_word word = {.value = x};
    word.bits &= UINT64_C(0x7fffffffffffffff);
    return word.value;
}
