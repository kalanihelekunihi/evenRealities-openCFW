/* Native motion accumulation0x61c48 and signed16 window0x6652a.
 * Preserve wrapped integer squares, live sample reloads and encoded math.
 * Explicit integer FP conversions retain saturation/status without C UB.
 */
#include <stdint.h>
#include <stddef.h>
extern void *memmove(void *,const void *,size_t);
extern float r1_native_sqrtf(float);
extern double r1_native_atan(double);
extern uint64_t r1_binary32_to_binary64_bits(uint32_t);
extern uint64_t r1_format_double_multiply_bits(uint64_t,uint64_t);
extern uint64_t r1_format_double_divide_bits(uint64_t,uint64_t);
extern uint32_t r1_log_double_to_float_bits(uint64_t);
static uint32_t W(uintptr_t p,uint32_t o){return *(const volatile uint32_t *)(p+o);}
static uint16_t H(uintptr_t p,uint32_t o){return *(const volatile uint16_t *)(p+o);}
static void SH(uintptr_t p,uint32_t o,uint16_t v){*(volatile uint16_t *)(p+o)=v;}
static float F(uintptr_t p,uint32_t o){return *(const volatile float *)(p+o);}
static void SF(uintptr_t p,uint32_t o,float v){*(volatile float *)(p+o)=v;}
static uint32_t bits(float v){union{float f;uint32_t u;}x={.f=v};return x.u;}
static float number(uint32_t v){union{float f;uint32_t u;}x={.u=v};return x.f;}
void r1_goodix_native_s16_window_push(void *record,uint32_t value)
{
 uintptr_t p=(uintptr_t)record;uint32_t count=H(p,4),capacity=H(p,6);uintptr_t values=W(p,0);
 if(count<capacity){SH(values,count*2u,(uint16_t)value);SH(p,4,(uint16_t)(H(p,4)+1u));}
 else{memmove((void *)values,(const void *)(values+2u),capacity*2u-2u);SH(W(p,0),H(p,6)*2u-2u,(uint16_t)value);}
}
static uint32_t truncate_bits(uint32_t value)
{
    uint32_t fp=__builtin_arm_get_fpscr();
    uint32_t magnitude=value&0x7fffffffu;
    uint32_t exponent=magnitude>>23;
    uint32_t fraction=magnitude&0x7fffffu;
    uint32_t sign=value>>31;
    uint32_t result=0,flags=0;
    if (exponent==255) {
        flags=1;
        if (!fraction) result=sign?0x80000000u:0x7fffffffu;
    } else if (exponent==0) {
        if (fraction) flags=(fp&(1u<<24))?128u:16u;
    } else if (exponent<127) {
        flags=16;
    } else if (exponent>158 || (exponent==158 && (!sign || fraction))) {
        result=sign?0x80000000u:0x7fffffffu;flags=1;
    } else {
        uint32_t significand=fraction|0x800000u;
        if (exponent<150) {
            uint32_t shift=150-exponent;
            result=significand>>shift;
            if (significand&((1u<<shift)-1u)) flags=16;
        } else result=significand<<(exponent-150);
        if (sign) result=0u-result;
    }
    __builtin_arm_set_fpscr(fp|flags);
    return result;
}
__attribute__((noinline)) static float ordered_add(float a,float b){return a+b;}
__attribute__((noinline)) static float divide(float a,float b){return a/b;}
void r1_goodix_spo2_motion_accumulate(const volatile uint32_t *raw,uint32_t sequence,const void *descriptor,volatile uint32_t *output)
{
 uintptr_t r=(uintptr_t)raw,p=(uintptr_t)output;
 uint32_t y=W(r,4),square_y=y*y;
 uint32_t z=W(r,8);float yy=(float)(int32_t)square_y;
 float x=(float)(int32_t)W(r,0),zz=(float)(int32_t)(z*z);
 float magnitude=r1_native_sqrtf(ordered_add(ordered_add(yy,x*x),zz));
 y=W(r,4);yy=(float)(int32_t)(y*y);x=(float)(int32_t)W(r,0);
 float horizontal=r1_native_sqrtf(ordered_add(yy,x*x));
 z=W(r,8);float angle=90.0f;
 if(z){
  float ratio=divide(horizontal,(float)(int32_t)z);
  union{double d;uint64_t u;} v={.u=r1_binary32_to_binary64_bits(bits(ratio))};v.d=r1_native_atan(v.d);
  uint64_t scaled=r1_format_double_multiply_bits(v.u,UINT64_C(0x4066800000000000));
  scaled=r1_format_double_divide_bits(scaled,UINT64_C(0x400921ff2e48e8a7));angle=number(r1_log_double_to_float_bits(scaled));
  if((int32_t)z<0)angle=ordered_add(angle,180.0f);
 }
 if(!sequence)SF(p,0,magnitude);
 uint32_t delta=truncate_bits(bits(magnitude-F(p,0)));
 r1_goodix_native_s16_window_push((void *)(p+4),delta&0xffffu);SF(p,0,magnitude);
 uint32_t period=W((uintptr_t)descriptor,92),remainder=period?sequence%period:sequence;
 if(!remainder)SF(p,12,0);
 float sum=ordered_add(F(p,12),angle);SF(p,12,sum);
 if(remainder==period-1u)r1_goodix_native_s16_window_push((void *)(p+16),truncate_bits(bits(divide(sum,(float)(int32_t)period)))&0xffffu);
}
