#include <stdint.h>
static unsigned char pool[20u*65536u];
static uint32_t allocations,releases;
static uint32_t sizes[20];
static uint32_t hash_bytes(const void *memory,uint32_t length)
{
    const uint8_t *bytes=(const uint8_t *)memory;
    uint32_t hash=2166136261u;
    for (uint32_t i=0;i<length;++i)
        hash=(hash^bytes[i])*16777619u;
    return hash;
}
static void *test_allocate(uint32_t size)
{
    if (allocations>=20u || size>65536u) return 0;
    sizes[allocations]=size;
#ifdef CREATE_FAIL_TEMP
    if (allocations==16u) { ++allocations; return 0; }
#endif
    void *result=&pool[allocations*65536u];
    ++allocations;
    return result;
}
static void test_release(void *ptr)
{
    if ((uintptr_t)ptr<(uintptr_t)pool ||
        (uintptr_t)ptr>=(uintptr_t)(pool+sizeof pool)) {
        releases=100u;
        return;
    }
    ++releases;
}
typedef void *(*gx8002_create)(
    int,int,int,int,float,float,float,float,int,float,float,int,int,
    const int *);
#ifdef SOURCE_MODE
extern void *gx8002_image_b_beamforming_core_1000ce14(
    int,int,int,int,float,float,float,float,int,float,float,int,int,
    const int *);
extern float gx8002_image_b_sin_float_1000ded0(float);
extern int gx8002_image_b_reduce_pi_over_two_1000fcfc(double,double[2]);
extern double gx8002_image_b_kernel_sin_10010f50(double,double,int);
#endif
typedef union { float f; uint32_t u; } fixture_float_word;
#ifdef CREATE_KERNEL_ORDERED
static double ordered_mul(double a,double b)
{
#ifdef SOURCE_MODE
    volatile double x=a,y=b; return x*y;
#else
    return ((double (*)(double,double))(uintptr_t)0x10011e50)(a,b);
#endif
}
static double ordered_add(double a,double b)
{
#ifdef SOURCE_MODE
    volatile double x=a,y=b; return x+y;
#else
    return ((double (*)(double,double))(uintptr_t)0x10011de4)(a,b);
#endif
}
static double ordered_sub(double a,double b)
{
#ifdef SOURCE_MODE
    volatile double x=a,y=b; return x-y;
#else
    return ((double (*)(double,double))(uintptr_t)0x10011e14)(a,b);
#endif
}
static double ordered_kernel_sin(double x,double y)
{
    const double s2=8.33333333332248946124e-03;
    const double s3=-1.98412698298579493134e-04;
    const double s4=2.75573137070700676789e-06;
    const double s5=-2.50507602534068634195e-08;
    const double s6=1.58969099521155010221e-10;
    const double positive_s1=0x1.5555555555554p-3; /* native 0x3fc5555555555554 */
    volatile double z=ordered_mul(x,x), v=ordered_mul(z,x);
    volatile double r=s6;
    r=ordered_add(s5,ordered_mul(z,r));
    r=ordered_add(s4,ordered_mul(z,r));
    r=ordered_add(s3,ordered_mul(z,r));
    r=ordered_add(s2,ordered_mul(z,r));
    volatile double half_y=ordered_mul(0.5,y);
    volatile double vr=ordered_mul(v,r);
    volatile double inner=ordered_sub(half_y,vr);
    volatile double zinner=ordered_mul(z,inner);
    volatile double minus_y=ordered_sub(zinner,y);
    volatile double v6=ordered_mul(v,positive_s1);
    volatile double expression=ordered_add(minus_y,v6);
    return ordered_sub(x,expression);
}
#endif
int main(void)
{
#ifndef SOURCE_MODE
    /* Native startup copies this initialized-data extent before math calls. */
    for (uint32_t i=0;i<0x12cu;++i)
        *(volatile uint8_t *)(uintptr_t)(0x20016f60u+i)=
            *(const volatile uint8_t *)(uintptr_t)(0x10016f60u+i);
#endif
    volatile uint32_t *ops=(volatile uint32_t *)(uintptr_t)0x2002d7a4u;
    ops[0]=(uint32_t)(uintptr_t)test_allocate;
    ops[3]=(uint32_t)(uintptr_t)test_release;
#ifdef CREATE_VARIANT_SINGLE_MIC
    const int outputs[1]={0};
#else
    const int outputs[1]={1};
#endif
#ifdef SOURCE_MODE
    uint32_t *ctx=gx8002_image_b_beamforming_core_1000ce14(
#else
    uint32_t *ctx=((gx8002_create)(uintptr_t)0x1000ce14)(
#endif
#ifdef CREATE_VARIANT_SINGLE_MIC
        8000,1,3,1,0.0f,2.0f,0.035f,1.0f,0,0.2f,0.01f,0,1,outputs);
#else
        16000,2,3,1,0.0f,2.0f,0.035f,1.0f,0,0.2f,0.01f,0,1,outputs);
#endif
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=allocations;
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=releases;
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=ctx?ctx[0x0c/4]:0;
    if (!ctx) return 1;
    for (uint32_t i=0;i<allocations;++i)
        *(volatile uint32_t *)(uintptr_t)0xffffc040u=sizes[i];
#ifndef CREATE_FAIL_TEMP
    fixture_float_word two_pi={.u=0x40c90fdbu};
    float step=two_pi.f/512.0f;
    fixture_float_word x64={.f=64.0f*step};
    fixture_float_word x192={.f=192.0f*step};
#ifdef SOURCE_MODE
    fixture_float_word trig64={.f=gx8002_image_b_sin_float_1000ded0(x64.f)};
    fixture_float_word trig192={.f=gx8002_image_b_sin_float_1000ded0(x192.f)};
#else
    fixture_float_word trig64={.f=((float (*)(float))(uintptr_t)0x1000ded0)(x64.f)};
    fixture_float_word trig192={.f=((float (*)(float))(uintptr_t)0x1000ded0)(x192.f)};
#endif
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=x64.u;
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=trig64.u;
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=x192.u;
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=trig192.u;
#ifdef CREATE_KERNEL_DETAIL
    double reduced[2]={0,0};
#ifdef SOURCE_MODE
    int quadrant=gx8002_image_b_reduce_pi_over_two_1000fcfc(
        0.785398185253143310546875,reduced);
#ifdef CREATE_KERNEL_ORDERED
    double kernel=ordered_kernel_sin(reduced[0],reduced[1]);
#else
    double kernel=gx8002_image_b_kernel_sin_10010f50(reduced[0],reduced[1],1);
#endif
#else
    int quadrant=((int (*)(double,double[2]))(uintptr_t)0x1000fcfc)(
        0.785398185253143310546875,reduced);
    double kernel=((double (*)(double,double,int))(uintptr_t)0x10010f50)(
        reduced[0],reduced[1],1);
#endif
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=(uint32_t)quadrant;
    const uint32_t *reduced_words=(const uint32_t *)(const void *)reduced;
    for (uint32_t i=0;i<4u;++i)
        *(volatile uint32_t *)(uintptr_t)0xffffc040u=reduced_words[i];
    const uint32_t *kernel_words=(const uint32_t *)(const void *)&kernel;
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=kernel_words[0];
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=kernel_words[1];
#ifndef SOURCE_MODE
#ifdef CREATE_KERNEL_ORDERED
    double reordered=ordered_kernel_sin(reduced[0],reduced[1]);
    const uint32_t *ordered_words=(const uint32_t *)(const void *)&reordered;
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=ordered_words[0];
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=ordered_words[1];
#endif
#endif
#endif
    static const uint16_t samples[9]={0,1,2,64,128,192,256,384,511};
    const uint32_t *forward=(const uint32_t *)(uintptr_t)ctx[0x70/4];
    const uint32_t *inverse=(const uint32_t *)(uintptr_t)ctx[0x74/4];
    for (uint32_t i=0;i<9u;++i)
        *(volatile uint32_t *)(uintptr_t)0xffffc040u=forward[samples[i]];
    for (uint32_t i=0;i<9u;++i)
        *(volatile uint32_t *)(uintptr_t)0xffffc040u=inverse[samples[i]];
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=
        hash_bytes((const void *)(uintptr_t)ctx[0x70/4],2048u);
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=
        hash_bytes((const void *)(uintptr_t)ctx[0x74/4],3072u);
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=
        hash_bytes((const void *)(uintptr_t)ctx[0xb8/4],3u*257u*4u);
#ifdef CREATE_DUMP_BUFFERS
    const uint32_t *full_forward=(const uint32_t *)(uintptr_t)ctx[0x70/4];
    const uint32_t *full_inverse=(const uint32_t *)(uintptr_t)ctx[0x74/4];
    const uint32_t *full_steering=(const uint32_t *)(uintptr_t)ctx[0xb8/4];
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=0x46574430u;
    for (uint32_t i=0;i<2048u/4u;++i)
        *(volatile uint32_t *)(uintptr_t)0xffffc040u=full_forward[i];
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=0x494e5630u;
    for (uint32_t i=0;i<3072u/4u;++i)
        *(volatile uint32_t *)(uintptr_t)0xffffc040u=full_inverse[i];
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=0x53545230u;
    for (uint32_t i=0;i<(3u*257u*4u)/4u;++i)
        *(volatile uint32_t *)(uintptr_t)0xffffc040u=full_steering[i];
#endif
#endif
#ifdef CREATE_FAIL_TEMP
    if (allocations!=17u || releases!=0u) return 2;
#else
    if (allocations!=17u || releases!=1u) return 2;
#endif
    if (ctx[0x04/4]!=
#ifdef CREATE_VARIANT_SINGLE_MIC
        1u
#else
        2u
#endif
        || ctx[0x08/4]!=3u || ctx[0x0c/4]!=512u)
        return 3;
    return 0;
}
