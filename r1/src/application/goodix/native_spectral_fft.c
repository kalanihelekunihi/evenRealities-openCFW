/* Native complex transform0x768b8, permutation0x36eb4, reversal0x85ca4
 * and real transform0x75e1c. Explicit coefficient input replaces the hidden
 * incoming-R9 dependency of non-256 calls; the256-point path owns its table.
 * Caller storage includes the two live mirrored-tail words.
 */
#include <stdint.h>
#include <stddef.h>
extern void __aeabi_memclr(void *,size_t);
extern float r1_native_sqrtf(float);
static uint32_t W(uintptr_t p,uint32_t i){return *(const volatile uint32_t *)(p+i*4u);}
static void S(uintptr_t p,uint32_t i,uint32_t v){*(volatile uint32_t *)(p+i*4u)=v;}
static float value(uint32_t b){union{uint32_t u;float f;}v={.u=b};return v.f;}
static uint32_t bits(float f){union{uint32_t u;float f;}v={.f=f};return v.u;}
static float F(uintptr_t p,uint32_t i){return value(W(p,i));}
static void SF(uintptr_t p,uint32_t i,float f){S(p,i,bits(f));}
__attribute__((noinline)) static float add(float a,float b){return a+b;}
__attribute__((noinline)) static float subtract(float a,float b){return a-b;}
__attribute__((noinline)) static float multiply(float a,float b){return a*b;}
static float negate(float f){return value(bits(f)^0x80000000u);}
static uint32_t lsl(uint32_t v,uint32_t count){count&=255u;return count<32u?v<<count:0;}
/* Native VMLS negates the rounded product before addition. Plain VSUB
 * preserves a selected product NaN sign and therefore is not equivalent. */
__attribute__((noinline)) static float multiply_subtract(float accumulator,float a,float b)
{return add(accumulator,negate(multiply(a,b)));}
uint32_t r1_goodix_native_reverse_low_bits(uint32_t input,uint32_t count)
{
 uint32_t output=0;
 while((int32_t)(--count)>=0){output|=lsl(input&1u,count);input=(input>>1)|(input&0x80000000u);}
 return output;
}
void r1_goodix_native_complex_permute(void *buffer,uint32_t width)
{
 uintptr_t p=(uintptr_t)buffer;uint32_t count=lsl(1,width);
 for(uint32_t i=0;(int32_t)i<(int32_t)count;++i){
  uint32_t j=r1_goodix_native_reverse_low_bits(i,width);
  if((int32_t)j>(int32_t)i){
   uint32_t b=W(p,j*2u),a=W(p,i*2u),imaginary=W(p,i*2u+1u);
   S(p,i*2u,b);b=W(p,j*2u+1u);S(p,i*2u+1u,b);S(p,j*2u,a);S(p,j*2u+1u,imaginary);
  }
 }
}
static void butterfly(uintptr_t p,uint32_t a,uint32_t b,float cosine,float sine)
{
 float br=F(p,b*2u),ar=F(p,a*2u),ai=F(p,a*2u+1u),bi=F(p,b*2u+1u);
 float real_sum=add(ar,br),real_difference=subtract(ar,br),imaginary_difference=subtract(ai,bi),imaginary_sum=add(bi,ai);
 float x=multiply(real_difference,cosine),y=multiply(imaginary_difference,sine),z=multiply(imaginary_difference,cosine),w=multiply(real_difference,sine);
 SF(p,a*2u,real_sum);SF(p,a*2u+1u,imaginary_sum);
 float real=add(x,y),imaginary=subtract(z,w);SF(p,b*2u,real);SF(p,b*2u+1u,imaginary);
}
void r1_goodix_native_complex_transform(void *buffer,uint32_t count,const void *coefficients,uint32_t step)
{
 uintptr_t p=(uintptr_t)buffer,t=(uintptr_t)coefficients;uint32_t half=count>>1,span=half,index=0,a=0;
 for(uint32_t remaining=half;remaining;--remaining){
  uint32_t other;float cosine;
  if(remaining>=32u){cosine=F(t,index);other=half-index;}
  else{cosine=negate(F(t,count-index));other=index-half;}
  float sine=F(t,other);butterfly(p,a,a+half,cosine,sine);index+=step;++a;
 }
 step=(step<<1)&0xffffu;
 for(uint32_t blocks=half;blocks>2u;blocks>>=1){
  uint32_t stride=span;span>>=1;index=0;
  for(uint32_t group=0;group<span;++group){
   uint32_t other;float cosine;
   if(group<=(span>>1)){cosine=F(t,index);other=half-index;}
   else{cosine=negate(F(t,count-index));other=index-half;}
   float sine=F(t,other);index+=step;
   for(uint32_t i=group;i<count;i+=stride)butterfly(p,i,i+span,cosine,sine);
  }
  step=(step<<1)&0xffffu;
 }
 for(uint32_t i=0;i<count;i+=2u){
  float a_real=F(p,i*2u),b_real=F(p,i*2u+2u),sum=add(a_real,b_real),difference=subtract(a_real,b_real);
  float a_imaginary=F(p,i*2u+1u),b_imaginary=F(p,i*2u+3u);SF(p,i*2u,sum);
  float imaginary_difference=subtract(a_imaginary,b_imaginary),imaginary_sum=add(b_imaginary,a_imaginary);
  SF(p,i*2u+1u,imaginary_sum);SF(p,i*2u+2u,difference);SF(p,i*2u+3u,imaginary_difference);
 }
}
static const uint32_t native_cosine[65]={
 0x3f800000u,0x3f7fec43u,0x3f7fb10fu,0x3f7f4e6du,0x3f7ec46du,0x3f7e1324u,0x3f7d3aacu,0x3f7c3b28u,
 0x3f7b14beu,0x3f79c79du,0x3f7853f8u,0x3f76ba07u,0x3f74fa0bu,0x3f731447u,0x3f710908u,0x3f6ed89eu,
 0x3f6c835eu,0x3f6a09a7u,0x3f676bd8u,0x3f64aa59u,0x3f61c598u,0x3f5ebe05u,0x3f5b941au,0x3f584853u,
 0x3f54db31u,0x3f514d3du,0x3f4d9f02u,0x3f49d112u,0x3f45e403u,0x3f41d870u,0x3f3daef9u,0x3f396842u,
 0x3f3504f3u,0x3f3085bbu,0x3f2beb4au,0x3f273656u,0x3f226799u,0x3f1d7fd1u,0x3f187fc0u,0x3f13682au,
 0x3f0e39dau,0x3f08f59bu,0x3f039c3du,0x3efc5d27u,0x3ef15aeau,0x3ee63375u,0x3edae880u,0x3ecf7bcau,
 0x3ec3ef15u,0x3eb8442au,0x3eac7cd4u,0x3ea09ae5u,0x3e94a031u,0x3e888e93u,0x3e78cfccu,0x3e605c13u,
 0x3e47c5c2u,0x3e2f10a2u,0x3e164083u,0x3dfab273u,0x3dc8bd36u,0x3d96a905u,0x3d48fb2fu,0x3cc90ab0u,
 0x00000000u,
};
/* The explicit final parameter represents the stock non-256 incoming R9.
 * The observed 256-point path always selects its owned coefficient table. */
void r1_goodix_native_real_transform(void *buffer,uint32_t input_count,uint32_t transform_count,const void *incoming_table)
{
 uintptr_t p=(uintptr_t)buffer,t=(uintptr_t)incoming_table;
 uint32_t half=(uint32_t)((int32_t)transform_count/2);
 uint32_t quarter=(half>>1)|(half&0x80000000u);
 if((int32_t)input_count<(int32_t)transform_count)__aeabi_memclr((void *)(p+input_count*4u),(transform_count-input_count)*4u);
 if(transform_count==256u){t=(uintptr_t)native_cosine;r1_goodix_native_complex_transform(buffer,128,(const void *)t,2);r1_goodix_native_complex_permute(buffer,7);}
 float nyquist=value(bits(subtract(F(p,0),F(p,1)))&0x7fffffffu);
 for(uint32_t i=0;(int32_t)i<=(int32_t)half/2;++i){
  uintptr_t a=p+i*8u,b=p+(half-i)*8u;
  float ar=F(a,0),br=F(b,0),ai=F(a,1),bi=F(b,1);
  float sum_real=add(ar,br),sum_imaginary=add(ai,bi),cosine=F(t,i);
  float real=sum_real,imaginary=subtract(ai,bi),difference=subtract(br,ar);
  real=add(real,multiply(sum_imaginary,cosine));imaginary=add(imaginary,multiply(difference,cosine));
  float sine=F(t,quarter-i);real=add(real,multiply(difference,sine));imaginary=multiply_subtract(imaginary,sum_imaginary,sine);
  SF(a,0,r1_native_sqrtf(add(multiply(real,real),multiply(imaginary,imaginary))));
  cosine=F(t,i);real=sum_real;imaginary=subtract(bi,ai);difference=subtract(ar,br);
  real=multiply_subtract(real,sum_imaginary,cosine);sine=F(t,quarter-i);imaginary=multiply_subtract(imaginary,difference,cosine);
  real=add(real,multiply(difference,sine));imaginary=multiply_subtract(imaginary,sum_imaginary,sine);
  SF(b,0,r1_native_sqrtf(add(multiply(real,real),multiply(imaginary,imaginary))));
 }
 for(uint32_t i=1;(int32_t)i<(int32_t)half;++i)SF(p,i,multiply(F(p,i*2u),0.5f));
 S(p,0,0);SF(p,half,nyquist);
}

