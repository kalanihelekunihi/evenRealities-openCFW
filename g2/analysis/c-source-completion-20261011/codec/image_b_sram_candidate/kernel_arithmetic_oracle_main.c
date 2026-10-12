#include <stdint.h>
typedef union { double d; uint32_t w[2]; } word64;
static void emit(double value)
{
    word64 w={.d=value};
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=w.w[0];
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=w.w[1];
}
static double mul(double a,double b)
{
#ifdef SOURCE_MODE
    volatile double x=a,y=b;
    return x*y;
#else
    return ((double (*)(double,double))(uintptr_t)0x10011e50)(a,b);
#endif
}
static double add(double a,double b)
{
#ifdef SOURCE_MODE
    volatile double x=a,y=b;
    return x+y;
#else
    return ((double (*)(double,double))(uintptr_t)0x10011de4)(a,b);
#endif
}
static double sub(double a,double b)
{
#ifdef SOURCE_MODE
    volatile double x=a,y=b;
    return x-y;
#else
    return ((double (*)(double,double))(uintptr_t)0x10011e14)(a,b);
#endif
}
int main(void)
{
    volatile double x=-0.7853981415417538;
    volatile double y=0.0;
    const double s1=-1.66666666666666324348e-01;
    const double s2=8.33333333332248946124e-03;
    double z=mul(x,x);
    double v=mul(z,x);
    emit(z);
    emit(v);
    emit(mul(z,s2));
    emit(mul(v,s1));
    emit(add(x,mul(v,s1)));
    emit(sub(x,sub(mul(z,mul(0.5,y)),y)));
    return 0;
}
