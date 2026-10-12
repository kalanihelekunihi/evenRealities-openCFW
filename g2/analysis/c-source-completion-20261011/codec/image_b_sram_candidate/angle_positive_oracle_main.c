#include <stdint.h>
static uint32_t ctx[0xb4/4+1];
static float radians[4];
#ifdef ANGLE_PRODUCT
#define ANGLE_THREE 1
#define ANGLE_FRAME 1
#endif
#ifdef ANGLE_PRODUCT_GEOMETRY
#define ANGLE_PRODUCT 1
#define ANGLE_THREE 1
#define ANGLE_FRAME 1
#define ANGLE_GEOMETRY 1
#endif
#ifdef ANGLE_PRODUCT_THREE_MICS
#define ANGLE_PRODUCT 1
#define ANGLE_THREE 1
#define ANGLE_FRAME 1
#endif
#ifdef ANGLE_PRODUCT_GEOMETRY_THREE_MICS
#define ANGLE_PRODUCT_GEOMETRY 1
#define ANGLE_PRODUCT 1
#define ANGLE_THREE 1
#define ANGLE_FRAME 1
#define ANGLE_GEOMETRY 1
#endif
#ifdef ANGLE_FRAME
static float phase_table[4096];
#endif
#ifdef ANGLE_THREE
static const int16_t degrees[3]={-30,0,30};
#else
static const int16_t degrees[1]={30};
#endif
static unsigned char pool[6u*65536u];
static uint32_t allocations,releases;
static void *test_allocate(uint32_t size)
{
    if (allocations>=6u || size>65536u) return 0;
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
typedef int (*gx8002_native_angle)(void *,int,const int16_t *);
#ifdef SOURCE_MODE
extern int gx8002_image_b_beamforming_angles_whole_candidate(
    void *,int,const int16_t *);
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
    ctx[0]=16000u;
    ctx[0x04/4]=
#ifdef ANGLE_PRODUCT
#if defined(ANGLE_PRODUCT_THREE_MICS) || defined(ANGLE_PRODUCT_GEOMETRY_THREE_MICS)
        3u;
#else
        2u;
#endif
#else
        1u;
#endif
    ctx[0x14/4]=16000u;
#ifdef ANGLE_FRAME
    ctx[0x18/4]=
#ifdef ANGLE_PRODUCT
        2u;
#else
        1u;
#endif
    ctx[0xa4/4]=(uint32_t)(uintptr_t)phase_table;
#else
    ctx[0x18/4]=0u;
#endif
#if defined(ANGLE_ONE) || defined(ANGLE_THREE)
#ifdef ANGLE_THREE
    ctx[0x1c/4]=3u;
    ctx[0x24/4]=3u;
#else
    ctx[0x1c/4]=1u;
    ctx[0x24/4]=1u;
#endif
    ctx[0x64/4]=(uint32_t)(uintptr_t)radians;
#else
    ctx[0x1c/4]=0u;
    ctx[0x24/4]=0u;
#endif
    ctx[0x28/4]=0u;
#ifdef ANGLE_PRODUCT
    ctx[0x28/4]=0x3f490fdbu; /* pi/4, nonzero phase increment */
    ctx[0x34/4]=0x3f800000u; /* native geometry multiplier */
#endif
#ifdef ANGLE_PRODUCT_GEOMETRY
    ctx[0x3c/4]=0x3d0f5c29u; /* product microphone distance, 0.035f */
#endif
#ifdef ANGLE_GEOMETRY
    ctx[0x30/4]=0u;
#else
    ctx[0x30/4]=1u;
#endif
#ifdef ANGLE_READY
    ctx[0x60/4]=1u;
#else
    ctx[0x60/4]=0u;
#endif
#ifdef SOURCE_MODE
    int result=gx8002_image_b_beamforming_angles_whole_candidate(
        ctx,
#if defined(ANGLE_ONE) || defined(ANGLE_THREE)
#ifdef ANGLE_THREE
        3,degrees);
#else
        1,degrees);
#endif
#else
        0,0);
#endif
#else
    int result=((gx8002_native_angle)(uintptr_t)0x1000c6e8)(
        ctx,
#if defined(ANGLE_ONE) || defined(ANGLE_THREE)
#ifdef ANGLE_THREE
        3,degrees);
#else
        1,degrees);
#endif
#else
        0,0);
#endif
#endif
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=(uint32_t)result;
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=allocations;
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=releases;
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=ctx[0x60/4];
#if defined(ANGLE_ONE) || defined(ANGLE_THREE)
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=
        *(const uint32_t *)(const void *)radians;
#ifdef ANGLE_THREE
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=
        *(const uint32_t *)(const void *)(radians+1);
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=
        *(const uint32_t *)(const void *)(radians+2);
#endif
#endif
#ifdef ANGLE_FRAME
    for (uint32_t i=0;i<16u;++i)
        *(volatile uint32_t *)(uintptr_t)0xffffc040u=
            ((const uint32_t *)(const void *)phase_table)[i];
    uint32_t table_hash=0u;
    const uint8_t *bytes=(const uint8_t *)(const void *)phase_table;
    for (uint32_t i=0;i<
#ifdef ANGLE_PRODUCT
#if defined(ANGLE_PRODUCT_THREE_MICS) || defined(ANGLE_PRODUCT_GEOMETRY_THREE_MICS)
        144u
#else
        96u
#endif
#else
        256u
#endif
        ;++i)
        table_hash=(table_hash*16777619u)^bytes[i];
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=table_hash;
#endif
#ifdef ANGLE_PRODUCT_GEOMETRY
    for (uint32_t a=0;a<6u;++a) {
        *(volatile uint32_t *)(uintptr_t)0xffffc040u=0x6000u+a;
        for (uint32_t j=0;j<4u;++j)
            *(volatile uint32_t *)(uintptr_t)0xffffc040u=
                ((const uint32_t *)(const void *)&pool[a*65536u])[j];
    }
#endif
    if (result!=0) return 1;
    if (allocations!=6u || releases!=6u) return 2;
    if (ctx[0x60/4]!=1u) return 3;
#ifdef ANGLE_THREE
    if (radians[0]>-0.523f || radians[0]<-0.524f ||
        radians[1]!=0.0f || radians[2]<0.523f || radians[2]>0.524f)
        return 4;
#elif defined(ANGLE_ONE)
    if (radians[0]<0.523f || radians[0]>0.524f) return 4;
#endif
    return 0;
}
