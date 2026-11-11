/* Native multiscale peak selection: signed row minimum,packed matrix,
 * unordered comparison policy,plateau ties and live output accumulation. */
#include "native_peak_selection.h"
#include <stdint.h>
#include <stddef.h>
extern void *goodix_mem_malloc(int32_t);
extern void goodix_mem_free(void *);
extern void *memset(void *,int,size_t);
static uint32_t W(uintptr_t p,uint32_t o){return *(const volatile uint32_t *)(p+o);}
static uint32_t H(uintptr_t p,uint32_t o){return *(const volatile uint16_t *)(p+o);}
static void S(uintptr_t p,uint32_t o,uint32_t v){*(volatile uint32_t *)(p+o)=v;}
static void SH(uintptr_t p,uint32_t o,uint32_t v){*(volatile uint16_t *)(p+o)=(uint16_t)v;}
__attribute__((noinline)) static uint32_t compare(uint32_t a,uint32_t b)
{
 uint32_t fp=__builtin_arm_get_fpscr(),flags;
 if(fp&(1u<<24)){
  if((a&0x7fffffffu)&&(a&0x7fffffffu)<0x800000u){a&=0x80000000u;fp|=128u;}
  if((b&0x7fffffffu)&&(b&0x7fffffffu)<0x800000u){b&=0x80000000u;fp|=128u;}
 }
 if((a&0x7fffffffu)>0x7f800000u||(b&0x7fffffffu)>0x7f800000u){flags=0x30000000u;fp|=1u;}
 else if(a==b||!((a|b)&0x7fffffffu))flags=0x60000000u;
 else{int less=(a>>31)!=(b>>31)?(a>>31)!=0:((a>>31)?a>b:a<b);flags=less?0x80000000u:0x20000000u;}
 __builtin_arm_set_fpscr((fp&0x0fffffffu)|flags);return flags;
}

void r1_goodix_native_minimum_row(const void *input,uint32_t count,void *output)
{
 uintptr_t p=(uintptr_t)input,out=(uintptr_t)output;int32_t minimum=(int16_t)H(p,0);SH(out,0,0);
 for(uint32_t i=1;i<count;i=(i+1u)&65535u){int32_t value=(int16_t)H(p,i*2u);if(value<minimum){minimum=value;SH(out,0,i);}}
}
static void set(uintptr_t p,uint32_t bit){volatile uint8_t *b=(volatile uint8_t *)(p+(bit>>3));*b=(uint8_t)(*b|(1u<<(bit&7u)));}
static uint32_t get(uintptr_t p,uint32_t bit){return (*(const volatile uint8_t *)(p+(bit>>3))>>(bit&7u))&1u;}
void r1_goodix_native_peak_mask(const void *descriptor,const void *input,void *output)
{
 uintptr_t d=(uintptr_t)descriptor,v=(uintptr_t)input,out=(uintptr_t)output;uint32_t n=H(d,0),rows=H(d,2),bytes=(n*rows)/8u+1u;uintptr_t bits=(uintptr_t)goodix_mem_malloc((int32_t)bytes);memset((void *)bits,0,bytes);
 for(uint32_t r=0;r<rows;++r){
  for(uint32_t i=0;i<=r;++i)set(bits,r*n+i);
  uint32_t end=n-r-1u;
  for(uint32_t i=r+1u;i<end;++i){uint32_t sample=W(v,i*4u);uint32_t left=compare(sample,W(v,(i-r-1u)*4u));if((left&0x60000000u)!=0x20000000u||(compare(sample,W(v,(i+r+1u)*4u))&0x60000000u)!=0x20000000u)set(bits,r*n+i);}
  for(uint32_t i=end;i<n;++i)set(bits,r*n+i);
 }
 uintptr_t sums=(uintptr_t)goodix_mem_malloc((int32_t)(rows*2u));
 for(uint32_t r=0;r<rows;++r)for(uint32_t i=0;i<n;++i)SH(sums,r*2u,H(sums,r*2u)+get(bits,r*n+i));
 uint16_t best=0;r1_goodix_native_minimum_row((void *)sums,rows,&best);goodix_mem_free((void *)sums);
 for(uint32_t i=0;i<n;++i)for(uint32_t r=0;r<=(uint32_t)best;++r)SH(out,i*2u,H(out,i*2u)+get(bits,r*n+i));
 goodix_mem_free((void *)bits);
}
void r1_goodix_native_peak_indices(const void *input,int32_t length,int32_t begin,int32_t capacity,void *indices,void *count)
{
 uintptr_t v=(uintptr_t)input,ix=(uintptr_t)indices,out=(uintptr_t)count;uintptr_t mask=(uintptr_t)goodix_mem_malloc((int32_t)((uint32_t)length*2u));uint16_t descriptor[2]={(uint16_t)length,37};r1_goodix_native_peak_mask(descriptor,input,(void *)mask);int32_t selected=0;
 for(int32_t i=1;i<length;++i){int32_t value=(int16_t)H(mask,(uint32_t)i*2u);int candidate=value==0;if(!candidate&&i>0&&H(mask,(uint32_t)(i-1)*2u)==1u&&value==1)candidate=compare(W(v,(uint32_t)(i-1)*4u),W(v,(uint32_t)i*4u))==0x60000000u;
  if(candidate&&(int32_t)((uint32_t)begin+1u)<i&&selected<capacity){SH(ix,(uint32_t)selected*2u,(uint32_t)i);selected=(int16_t)(selected+1);}}
 S(out,0,(uint32_t)selected);goodix_mem_free((void *)mask);
}
