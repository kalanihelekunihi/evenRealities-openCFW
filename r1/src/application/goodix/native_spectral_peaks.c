/* Native maximum/index0x929d6 and peak selection0x74190. Preserve raw
 * float payloads, VCMPE status, radius skips, capacity-clamped insertion
 * and live count/index/value aliases. No inline assembly or owned state.
 */
#include <stdint.h>
#include <stddef.h>
extern void *memmove(void *,const void *,size_t);
static uint32_t W(uintptr_t p,uint32_t i){return *(const volatile uint32_t *)(p+i*4u);}
static void S(uintptr_t p,uint32_t i,uint32_t v){*(volatile uint32_t *)(p+i*4u)=v;}
static float value(uint32_t b){union{uint32_t u;float f;}v={.u=b};return v.f;}
static uint32_t bits(float f){union{uint32_t u;float f;}v={.f=f};return v.u;}
static uint32_t compare(uint32_t a,uint32_t b)
{
 uint32_t fp=__builtin_arm_get_fpscr();
 if(fp&(1u<<24)){
  if((a&0x7fffffffu)&&(a&0x7fffffffu)<0x800000u){a&=0x80000000u;fp|=128;}
  if((b&0x7fffffffu)&&(b&0x7fffffffu)<0x800000u){b&=0x80000000u;fp|=128;}
 }
 uint32_t flags;
 if((a&0x7fffffffu)>0x7f800000u||(b&0x7fffffffu)>0x7f800000u){flags=0x30000000u;fp|=1;}
 else if(a==b||!((a|b)&0x7fffffffu))flags=0x60000000u;
 else{uint32_t less=(a>>31)!=(b>>31)?a>>31:(a>>31)?a>b:a<b;flags=less?0x80000000u:0x20000000u;}
 __builtin_arm_set_fpscr((fp&0x0fffffffu)|flags);return flags;
}

void r1_goodix_native_maximum_index(const void *input,uint32_t count,void *maximum,void *index)
{
 uintptr_t p=(uintptr_t)input;uint32_t best=W(p,0),selected=0;
 for(uint32_t remaining=count-1u;remaining;--remaining){uint32_t i=count-remaining,current=W(p,i);if(compare(best,current)==0x80000000u){best=current;selected=i;}}
 S((uintptr_t)maximum,0,best);S((uintptr_t)index,0,selected);
}
__attribute__((noinline)) static float multiply(float a,float b){return a*b;}
static uint32_t minimum(uint32_t a,uint32_t b){return (int32_t)a<(int32_t)b?a:b;}
void r1_goodix_native_peak_select(float weight,const void *input,uint32_t count,int32_t begin,int32_t end,int32_t radius,int32_t capacity,void *indices,void *values,void *selected_count)
{
 uintptr_t p=(uintptr_t)input,ix=(uintptr_t)indices,out=(uintptr_t)values,n=(uintptr_t)selected_count;uint32_t maximum=0,unused=0;
 r1_goodix_native_maximum_index(input,count,&maximum,&unused);S(n,0,0);
 for(uint32_t current=(uint32_t)begin;(int32_t)current<end;){
  uint32_t low=current-(uint32_t)radius,upper=current+(uint32_t)radius;
  if((int32_t)low<=0)low=0;uint32_t high=minimum(upper,count-1u);
  for(uint32_t i=low;(int32_t)i<(int32_t)high;++i){
   if((int32_t)i<(int32_t)current&&compare(W(p,i),W(p,i+1u))==0x20000000u)goto reject;
   if((int32_t)i>=(int32_t)current&&compare(W(p,i),W(p,i+1u))==0x80000000u)goto reject;
  }
  uint32_t threshold=bits(multiply(weight,value(maximum))),candidate=W(p,current),relation=compare(candidate,threshold);
  if(relation!=0x80000000u&&relation!=0x30000000u){
   uint32_t total=W(n,0),i=total-1u;
   while((int32_t)i>=0){uint32_t c=compare(candidate,W(p,W(ix,i)));if(c==0x80000000u||c==0x60000000u)break;--i;}
   uint32_t position=minimum(i+1u,(uint32_t)capacity-1u);
   uint32_t move=minimum(total-position,(uint32_t)capacity-position-1u);
   memmove((void *)(ix+(position+1u)*4u),(const void *)(ix+position*4u),move*4u);S(ix,position,current);
   total=W(n,0);S(n,0,minimum(total+1u,(uint32_t)capacity));
  }
  current=upper+1u;continue;
 reject:++current;
 }
 for(uint32_t i=0;(int32_t)i<(int32_t)W(n,0);++i)S(out,i,W(p,W(ix,i)));
}
