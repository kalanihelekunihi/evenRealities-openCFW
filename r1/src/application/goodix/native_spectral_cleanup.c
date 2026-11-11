/* Native spectral sign cleanup0x72fb8 and scale/window copy0x32744.
 * The latter includes shared tail0x92924. Fixed125-sample sensor window
 * coefficients are data, not executable firmware. Preserve live aliases.
 */
#include <stdint.h>
#include <stddef.h>
extern void *memmove(void *,const void *,size_t);
static uint32_t word(uintptr_t p,uint32_t index){return *(const volatile uint32_t *)(p+index*4u);}
static void put(uintptr_t p,uint32_t index,uint32_t bits){*(volatile uint32_t *)(p+index*4u)=bits;}
static float number(uint32_t bits){union{uint32_t u;float f;}v={.u=bits};return v.f;}
static uint32_t bits(float number){union{uint32_t u;float f;}v={.f=number};return v.u;}
/* VCMPE.F32 against zero: preserve flags even when a sample is a NaN or
 * a denormal flushed only for comparison. Input memory is never rewritten. */
static uint32_t compare_zero(uint32_t value)
{
 uint32_t fp=__builtin_arm_get_fpscr(),magnitude=value&0x7fffffffu,flags;
 if((fp&(1u<<24))&&magnitude&&magnitude<0x800000u){magnitude=0;fp|=128;}
 if(magnitude>0x7f800000u){flags=0x30000000u;fp|=1;}
 else if(!magnitude)flags=0x60000000u;
 else flags=(value>>31)?0x80000000u:0x20000000u;
 __builtin_arm_set_fpscr((fp&0x0fffffffu)|flags);return flags;
}
void r1_goodix_native_zero_masked_runs(const void *input,uint32_t count,const void *mask,void *output)
{
 uintptr_t in=(uintptr_t)input,out=(uintptr_t)output,m=(uintptr_t)mask;uint32_t current=0;
 while((int32_t)current<(int32_t)count){
  if(*(const volatile uint8_t *)(m+current)!=1){put(out,current,word(in,current));++current;continue;}
  uint32_t left=current;
  if(compare_zero(word(in,left))==0x20000000u){
   while((int32_t)left>=0&&compare_zero(word(in,left))==0x20000000u){put(out,left,0);--left;}
   left=current+1u;
   while((int32_t)left<(int32_t)count&&compare_zero(word(in,left))==0x20000000u){put(out,left,0);++left;}
   current=left-1u;
  }
  if(compare_zero(word(in,current))==0x80000000u){
   while((int32_t)left>=0&&compare_zero(word(in,left))==0x80000000u){put(out,left,0);--left;}
   ++current;
   while((int32_t)current<(int32_t)count&&compare_zero(word(in,current))==0x80000000u){put(out,current,0);++current;}
   --current;
  }
  ++current;
 }
}
/* Native periodic window:125 samples, the extent used by the sensor path. */
static const uint32_t native_window[125]={
 0x00000000u,0x3aa58b3fu,0x3ba57215u,0x3c39ecf6u,0x3ca50721u,0x3d00af1du,0x3d38df7au,0x3d7af20fu,
 0x3da35d68u,0x3dce04c0u,0x3dfd52c1u,0x3e189507u,0x3e34b3c4u,0x3e52f449u,0x3e734224u,0x3e8ac493u,
 0x3e9cd984u,0x3eafd3f6u,0x3ec3a7dbu,0x3ed8485au,0x3eeda815u,0x3f01dca5u,0x3f0d36c6u,0x3f18db27u,
 0x3f24c22fu,0x3f30e443u,0x3f3d3975u,0x3f49b9e9u,0x3f565d6cu,0x3f631bdfu,0x3f6feceeu,0x3f7cc87au,
 0x3f84d307u,0x3f8b3eb4u,0x3f91a31au,0x3f97fc1au,0x3f9e4599u,0x3fa47b81u,0x3faa99d9u,0x3fb09c99u,
 0x3fb67fedu,0x3fbc4007u,0x3fc1d92bu,0x3fc747b6u,0x3fcc8827u,0x3fd1971cu,0x3fd67150u,0x3fdb139du,
 0x3fdf7affu,0x3fe3a4a5u,0x3fe78ddeu,0x3feb341eu,0x3fee9507u,0x3ff1ae71u,0x3ff47e5au,0x3ff702e6u,
 0x3ff93a82u,0x3ffb23bcu,0x3ffcbd4du,0x3ffe0631u,0x3ffefda0u,0x3fffa2e8u,0x3ffff5a5u,0x3ffff5a5u,
 0x3fffa2e8u,0x3ffefda0u,0x3ffe0631u,0x3ffcbd4du,0x3ffb23bcu,0x3ff93a82u,0x3ff702e6u,0x3ff47e5au,
 0x3ff1ae71u,0x3fee9507u,0x3feb341eu,0x3fe78ddeu,0x3fe3a4a5u,0x3fdf7affu,0x3fdb139du,0x3fd67150u,
 0x3fd1971cu,0x3fcc8827u,0x3fc747b6u,0x3fc1d92bu,0x3fbc4007u,0x3fb67fedu,0x3fb09c99u,0x3faa99d9u,
 0x3fa47b81u,0x3f9e4599u,0x3f97fc1au,0x3f91a31au,0x3f8b3eb4u,0x3f84d307u,0x3f7cc87au,0x3f6feceeu,
 0x3f631bdfu,0x3f565d6cu,0x3f49b9e9u,0x3f3d3975u,0x3f30e443u,0x3f24c22fu,0x3f18db27u,0x3f0d36c6u,
 0x3f01dca5u,0x3eeda815u,0x3ed8485au,0x3ec3a7dbu,0x3eafd3f6u,0x3e9cd984u,0x3e8ac493u,0x3e734224u,
 0x3e52f449u,0x3e34b3c4u,0x3e189507u,0x3dfd52c1u,0x3dce04c0u,0x3da35d68u,0x3d7af20fu,0x3d38df7au,
 0x3d00af1du,0x3ca50721u,0x3c39ecf6u,0x3ba57215u,0x3aa58b3fu,
};
void r1_goodix_native_scale_copy(const void *input,uint32_t count,uint32_t mode,void *output,void *factor)
{
 *(volatile uint32_t *)factor=0x3f800000u;
 if(mode!=1){memmove(output,input,count*4u);return;}
 *(volatile uint32_t *)factor=0x3fc00000u;
 uintptr_t in=(uintptr_t)input,out=(uintptr_t)output,window=(uintptr_t)native_window;
 while(count){
  float sample=number(word(in,0));in+=4u;
  float weight=number(word(window,0));window+=4u;
  put(out,0,bits(sample*weight));out+=4u;--count;
 }
}
