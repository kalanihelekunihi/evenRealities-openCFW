#include <stdint.h>
static uint32_t ctx[0xb4/4+1];
static int16_t degrees[2]={-30,30};
typedef int (*gx8002_native_angle)(void *,int,const int16_t *);
#ifdef SOURCE_MODE
extern int gx8002_image_b_beamforming_angles_1000c6e8(
    void *,int,const int16_t *);
#endif
int main(void)
{
    ctx[0x1c/4]=2u;
    ctx[0x60/4]=7u;
#ifdef SOURCE_MODE
    int result=gx8002_image_b_beamforming_angles_1000c6e8(
        ctx,1,degrees);
#else
    int result=((gx8002_native_angle)(uintptr_t)0x1000c6e8)(
        ctx,1,degrees);
#endif
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=(uint32_t)result;
    *(volatile uint32_t *)(uintptr_t)0xffffc040u=ctx[0x60/4];
    if (result!=-1) return 1;
    if (ctx[0x60/4]!=0u) return 2;
    return 0;
}
