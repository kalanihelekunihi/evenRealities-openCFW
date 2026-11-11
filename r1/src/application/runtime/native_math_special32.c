#include <stdint.h>
#if defined(__clang__)
#define NATIVE_FP __attribute__((noinline))
#else
#define NATIVE_FP __attribute__((noinline,noclone))
#endif
static float as_float(uint32_t bits)
{ union {uint32_t bits;float value;} x={.bits=bits};return x.value; }
static NATIVE_FP float divide32(float a,float b){return a/b;}
static NATIVE_FP float square32(float value){return value*value;}
float r1_math_divzero32(void){return divide32(1.0f,0.0f);}
float r1_math_self_add32(float value){return value+value;}
float r1_math_add32(float a,float b){return a+b;}
float r1_math_invalid32(void){return divide32(0.0f,0.0f);}
float r1_math_high_square32(void){return square32(as_float(0x70000000u));}
float r1_math_low_square32(void){return square32(as_float(0x10000000u));}
