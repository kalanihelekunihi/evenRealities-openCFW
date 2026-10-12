#include <stdint.h>
typedef union { double d; uint64_t u; uint32_t w[2]; } binary64;
static void emit(double value)
{
    binary64 word={.d=value};
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=word.w[0];
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=word.w[1];
}
#ifdef SOURCE_MODE
extern double gx8002_image_b_sin_double_1000fb14(double);
extern double gx8002_image_b_cos_double_1000fbb0(double);
#endif
int main(void)
{
#ifndef SOURCE_MODE
    for (uint32_t i=0;i<0x12cu;++i)
        *(volatile uint8_t *)(uintptr_t)(0x20016f60u+i)=
            *(const volatile uint8_t *)(uintptr_t)(0x10016f60u+i);
#endif
    static const uint64_t inputs[]={
        UINT64_C(0x0000000000000000), UINT64_C(0x8000000000000000),
        UINT64_C(0x3e30000000000000), UINT64_C(0x3fe921faffffffff),
        UINT64_C(0x3fe921fb00000000), UINT64_C(0x3fe921fb00000001),
        UINT64_C(0x3fe921fb54442d18), UINT64_C(0x3fe921fb80000000),
        UINT64_C(0x3ff921fb54442d18), UINT64_C(0x400921fb54442d18),
        UINT64_C(0x401921fb54442d18), UINT64_C(0x4024000000000000),
        UINT64_C(0x4059000000000000), UINT64_C(0xbfe921fb54442d18),
        UINT64_C(0xbff921fb54442d18), UINT64_C(0xc00921fb54442d18),
    };
    for (uint32_t i=0;i<sizeof inputs/sizeof inputs[0];++i) {
        binary64 x={.u=inputs[i]};
#ifdef SOURCE_MODE
        emit(gx8002_image_b_sin_double_1000fb14(x.d));
        emit(gx8002_image_b_cos_double_1000fbb0(x.d));
#else
        emit(((double (*)(double))(uintptr_t)0x1000fb14)(x.d));
        emit(((double (*)(double))(uintptr_t)0x1000fbb0)(x.d));
#endif
    }
    return 0;
}
