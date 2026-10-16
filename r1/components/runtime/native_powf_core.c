#include <stdint.h>
extern uint32_t r1_native_floating_environment_control(void);
extern uint32_t r1_binary32_classify_bits(uint32_t,uint32_t,uint32_t,uint32_t);
extern void r1_native_errno_set(uint32_t);
extern float r1_math_high_square32(void);
extern float r1_math_low_square32(void);
/* Ordered VFP arithmetic is the recovered reduced logarithm/product/exp core.
 * Integer input words and live FP operands are supplied by the dispatcher. */
__attribute__((section(".r1.math.powf_prefix"),used))
const uint32_t r1_powf_prefix[8]={0x0,0xc0801000,0x3eaaaaab,0x3d800000,0x3e4ce27e,0x4238b000,0xbbb89ad4,0x4238aa3b};
__attribute__((section(".r1.math.powf_exponential"),used))
const uint32_t r1_powf_exponential[3]={0x376359fc,0x3a75ffc9,0x3d317218};
__attribute__((section(".r1.math.powf_scaling"),used))
const uint32_t r1_powf_scaling[5]={0x42fc0000,0x42fe0000,0x4b000000,0x43400000,0x4d000000};
__attribute__((section(".r1.math.powf_near_one"),used))
const uint32_t r1_powf_near_one[3]={0x41b8b000,0xbb389ad4,0x41b8aa3b};
__attribute__((section(".r1.math.powf_log_table"),used))
const uint32_t r1_powf_log_table[32]={0x0,0x0,0x3fb30000,0x3a7dbeb2,0x402e0000,0x3851cfdf,0x407e0000,0xbafa51bf,0x40a4e000,0xbac3da19,0x40c8e000,0xb98aedc2,0x40eb4000,0xba2c1fcd,0x41061000,0xbafaff2a,0x4115c000,0x37d1cfdf,0x4124d000,0x3a70979a,0x41335000,0x368e4789,0x41414000,0x389d5be7,0x414eb000,0xb9980ac0,0x415ba000,0x3a948f55,0x41683000,0xbac092da,0x41744000,0x3ac6b362};
__attribute__((section(".r1.math.powf_exp_head"),used))
const uint32_t r1_powf_exp_head[16]={0x0,0x39ac367d,0x39383c7d,0x38f4dceb,0x397e0a32,0x39264c12,0x39ed6a9b,0x3983eea4,0x391e667f,0x398a39f6,0x3965422b,0x391182a4,0x391f995b,0x39cdeec3,0x37c6e7dd,0x392fa2a5};
__attribute__((section(".r1.math.powf_exp_scale"),used))
const uint32_t r1_powf_exp_scale[16]={0x3f800000,0x3f85aac3,0x3f8b95c2,0x3f91c3d3,0x3f9837f0,0x3f9ef532,0x3fa5fed7,0x3fad583f,0x3fb504f3,0x3fbd08a4,0x3fc5672a,0x3fce248c,0x3fd744fd,0x3fe0ccdf,0x3feac0c7,0x3ff5257d};
__attribute__((section(".r1.math.powf_exp_tail"),used))
const uint32_t r1_powf_exp_tail[16]={0x3f800000,0x3f85a000,0x3f8b9000,0x3f91c000,0x3f983000,0x3f9ef000,0x3fa5f000,0x3fad5000,0x3fb50000,0x3fbd0000,0x3fc56000,0x3fce2000,0x3fd74000,0x3fe0c000,0x3feac000,0x3ff52000};
typedef union{uint32_t bits;float value;} encoded_float;
static float value(uint32_t bits){encoded_float x={.bits=bits};return x.value;}
static uint32_t bits(float value){encoded_float x={.value=value};return x.bits;}
#define BINARY(name,instruction) static float name(float a,float b){float r;__asm__ volatile(instruction " %0,%1,%2":"=t"(r):"t"(a),"t"(b));return r;}
BINARY(add,"vadd.f32")
BINARY(sub,"vsub.f32")
BINARY(mul,"vmul.f32")
BINARY(divide,"vdiv.f32")
BINARY(negative_mul,"vnmul.f32")
static float madd(float r,float a,float b){__asm__ volatile("vmla.f32 %0,%1,%2":"+t"(r):"t"(a),"t"(b));return r;}
static float msub(float r,float a,float b){__asm__ volatile("vmls.f32 %0,%1,%2":"+t"(r):"t"(a),"t"(b));return r;}
static float absolute(float x){__asm__ volatile("vabs.f32 %0,%0":"+t"(x));return x;}
static float from_integer(uint32_t x){float r=value(x);__asm__ volatile("vcvt.f32.s32 %0,%0":"+t"(r));return r;}
static uint32_t to_integer(float x){__asm__ volatile("vcvt.s32.f32 %0,%0":"+t"(x));return bits(x);}
static float to_encoded_unsigned(float x){__asm__ volatile("vcvt.u32.f32 %0,%0":"+t"(x));return x;}
static uint32_t zero_carry(float x){uint32_t status;__asm__ volatile("vcmpe.f32 %1,#0.0\n\tvmrs %0,fpscr":"=r"(status):"t"(x));return(status>>29)&1u;}
static float rounded(float x){return value((bits(x)+0x800u)&~0xfffu);}
static float signed_error(float sign,uint32_t overflow){r1_native_errno_set(2);float result=overflow ? r1_math_high_square32() : r1_math_low_square32();return value((bits(sign)&0x80000000u)|(bits(result)&0x7fffffffu));}
float r1_powf_reduced(uint32_t input,int32_t adjustment,float base,float exponent,float sign)
{
 float s0=base,s2=1.0f,s3,s4,s5,s6=value(r1_powf_prefix[2]),s7,s8,log_high,log_low;
 if(input+r1_powf_prefix[1]<=0x2000u){
  s0=sub(s0,s2);s2=0.25f;s4=value(r1_powf_near_one[1]);
  s6=msub(s6,s0,s2);s2=0.5f;s3=mul(s0,s0);s2=msub(s2,s0,s6);s3=negative_mul(s3,s2);
  s2=mul(s0,value(r1_powf_near_one[0]));s0=mul(s0,s4);s4=value(r1_powf_near_one[2]);s0=madd(s0,s3,s4);
  s3=add(s2,s0);log_high=rounded(s3);s2=sub(s2,log_high);log_low=add(s2,s0);
 }else{
  uint32_t bucket=(input+0x40000u)>>19,index=bucket&15u;
  int32_t exponent_word=(int32_t)((bucket>>4)&255)-127;
  input-=(uint32_t)exponent_word<<23;adjustment+=exponent_word;
  s4=from_integer(index);s0=value(input);s5=value(r1_powf_prefix[3]);s3=madd(s2,s4,s5);s7=s3;
  s5=add(s0,s7);s4=sub(s0,s7);s3=rounded(s5);s7=sub(s7,s3);s8=add(s7,s0);s7=divide(s2,s5);
  s0=rounded(mul(s4,s7));s4=msub(s4,s0,s3);s4=msub(s4,s0,s8);s5=mul(s4,s7);s3=add(s0,s5);s4=mul(s3,s3);
  s7=value(r1_powf_prefix[4]);s6=madd(s6,s4,s7);s6=mul(s6,s4);s4=mul(s0,s2);s2=mul(s5,s2);s2=madd(s2,s6,s3);
  s0=rounded(add(s4,s2));s3=sub(s4,s0);s4=add(s3,s2);s3=mul(s0,value(r1_powf_prefix[5]));s2=mul(s0,value(r1_powf_prefix[6]));s2=madd(s2,s4,value(r1_powf_prefix[7]));
  s0=rounded(add(s3,s2));s3=sub(s3,s0);s4=add(s3,s2);
  float table_high=value(r1_powf_log_table[2*index]),table_low=value(r1_powf_log_table[2*index+1]);
  s5=from_integer((uint32_t)adjustment<<4);s2=add(s4,table_low);s2=add(s2,s0);s2=add(s2,table_high);s2=add(s2,s5);log_high=rounded(s2);
  s2=sub(log_high,s5);s2=sub(s2,table_high);s0=sub(s2,s0);s0=sub(s0,table_low);log_low=sub(s4,s0);
 }
 float exponent_high=rounded(exponent),exponent_low=sub(exponent,exponent_high),product_low=value(r1_powf_prefix[0]);
 (void)r1_native_floating_environment_control();
 s0=mul(log_high,exponent_high);float magnitude=absolute(s0);uint32_t encoded=bits(magnitude);
 if((int32_t)encoded>(int32_t)0x45800000u && (encoded<<1)<=0xff000000u){exponent_high=value((bits(s0)&0x80000000u)|0x45800000u);}
 else{s3=mul(log_high,exponent_low);s2=add(exponent_high,exponent_low);s3=madd(s3,log_low,s2);s2=add(s0,s3);exponent_high=rounded(s2);s0=sub(s0,exponent_high);product_low=add(s0,s3);}
 (void)r1_native_floating_environment_control();
 s0=add(exponent_high,product_low);s0=add(zero_carry(s0) ? 0.5f : -0.5f,s0);
 uint32_t integral=to_integer(s0);int32_t scale=(int32_t)integral>>4;
 float scale_float=from_integer((uint32_t)scale);s0=from_integer(integral);s0=sub(exponent_high,s0);s0=add(s0,product_low);
 s2=madd(value(r1_powf_exponential[1]),s0,value(r1_powf_exponential[0]));s3=madd(value(r1_powf_exponential[2]),s0,s2);s0=mul(s3,s0);
 uint32_t index=integral&15u;s2=madd(value(r1_powf_exp_head[index]),value(r1_powf_exp_scale[index]),s0);s2=add(s2,value(r1_powf_exp_tail[index]));
 magnitude=absolute(scale_float);encoded=bits(magnitude);
 if((int32_t)encoded<(int32_t)r1_powf_scaling[0] && (encoded<<1)<=0xff000000u){
  s0=mul(add(scale_float,value(r1_powf_scaling[1])),value(r1_powf_scaling[2]));s3=mul(sign,s2);return mul(to_encoded_unsigned(s0),s3);
 }
 if((int32_t)encoded>=(int32_t)r1_powf_scaling[3] || (encoded<<1)>0xff000000u)return signed_error(sign,zero_carry(scale_float));
 int32_t integral_scale=(int32_t)to_integer(scale_float);s3=mul(sign,s2);
 uint32_t biased=(uint32_t)integral_scale+((uint32_t)integral_scale>>31);int32_t first=(int32_t)biased>>1;
 s0=value(((uint32_t)first<<23)+0x3f800000u);s3=mul(s0,s3);int32_t second=integral_scale-first;
 float result=mul(s3,value(((uint32_t)second<<23)+0x3f800000u));encoded=bits(result);
 if((encoded<<1)==0xff000000u)return signed_error(sign,1);
 if((encoded<<1)==0)return signed_error(sign,0);
 if(r1_binary32_classify_bits(encoded,0,0,0)==4)(void)r1_math_low_square32();
 return result;
}
