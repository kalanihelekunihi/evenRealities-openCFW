#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
extern float gx8002_image_b_power_float_core_100100bc(float,float);
extern float gx8002_image_b_sqrtf_10010bcc(float);
extern float gx8002_image_b_quiet_nan_10011298(void);
extern float gx8002_image_b_fabsf_100112c4(float);
static float from(uint32_t v){float f;memcpy(&f,&v,4);return f;}
static uint32_t bits(float f){uint32_t u;memcpy(&u,&f,4);return u;}
int main(void){unsigned pass=0;
if(bits(gx8002_image_b_quiet_nan_10011298())==0x7fc00000u)pass++;
if(bits(gx8002_image_b_fabsf_100112c4(from(0xff800000u)))==0x7f800000u)pass++;
if(bits(gx8002_image_b_sqrtf_10010bcc(from(0x80000000u)))==0x80000000u)pass++;
if(bits(gx8002_image_b_sqrtf_10010bcc(from(0x7f800000u)))==0x7f800000u)pass++;
if(bits(gx8002_image_b_power_float_core_100100bc(from(0x7fc10000u),2.0f))==0x7fc00000u)pass++;
if(bits(gx8002_image_b_power_float_core_100100bc(1.0f,from(0x7fc10000u)))==0x3f800000u)pass++;
printf("native-branch special expectations %u/6\n",pass);return pass!=6;}
