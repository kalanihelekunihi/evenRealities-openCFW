/* Native SpO2 peak-grid, extrema selection and rolling histories.
 * One implementation per native entry; portable scratch-buffer primitives
 * remain separate APIs. Preserve live loads and hardware FP flag predicates. */
#include "native_spo2_ratio.h"
#include <stdint.h>
#include <stddef.h>
extern void *goodix_mem_malloc(int32_t);
extern void goodix_mem_free(void *);
extern void *memmove(void *,const void *,size_t);
extern void __aeabi_memclr(void *,size_t);
static uint32_t W(uintptr_t p,uint32_t o){return *(const volatile uint32_t *)(p+o);}
static uint16_t H(uintptr_t p,uint32_t o){return *(const volatile uint16_t *)(p+o);}
static void S(uintptr_t p,uint32_t o,uint32_t v){*(volatile uint32_t *)(p+o)=v;}
static void SH(uintptr_t p,uint32_t o,uint16_t v){*(volatile uint16_t *)(p+o)=v;}
static float F(uint32_t b){union{uint32_t u;float f;}v={.u=b};return v.f;}
static uint32_t B(float f){union{uint32_t u;float f;}v={.f=f};return v.u;}
__attribute__((noinline)) static float multiply(float a,float b){volatile float result=a*b;return result;}
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
static int hi(uint32_t f){return (f&0x20000000u)&&!(f&0x40000000u);}
static int lt(uint32_t f){return ((f>>31)^((f>>28)&1u))!=0;}
static int gt(uint32_t f){return !(f&0x40000000u)&&!lt(f);}
static uint8_t bit(uintptr_t p,uint32_t i){return (uint8_t)((*(const volatile uint8_t *)(p+(uint32_t)((int32_t)i>>3))>>(i&7u))&1u);}
static void put_bit(uintptr_t p,uint32_t i,int set)
{
 volatile uint8_t *q=(volatile uint8_t *)(p+(uint32_t)((int32_t)i>>3));uint8_t v=*q,m=(uint8_t)(1u<<(i&7u));*q=set?(uint8_t)(v|m):(uint8_t)(v&~m);
}
void r1_goodix_native_peak_grid(const void *input,uint32_t count,uint32_t rows,uint32_t plateau,uint32_t mode,void *matrix)
{
 uintptr_t in=(uintptr_t)input,out=(uintptr_t)matrix;float factor=mode==1u?-1.0f:1.0f;uint32_t base=0;
 for(uint32_t row=0;(int32_t)row<(int32_t)rows;++row){
  uint32_t left=(int32_t)row<=(int32_t)(count-1u)?row:count-1u;
  uint32_t right=count-row-1u;if((int32_t)right<=0)right=0;
  for(uint32_t x=0;(int32_t)x<=(int32_t)left;++x)put_bit(out,base+x,1);
  for(uint32_t x=left+1u;(int32_t)x<(int32_t)right;++x){
   uint32_t a=B(multiply(F(W(in,x*4u)),factor));
   uint32_t l=W(in,(x-row-1u)*4u);uint32_t r=W(in,(x+row+1u)*4u);
   uint32_t b=B(multiply(F(l),factor));uint32_t f=compare(a,b);
   uint32_t c=B(multiply(F(r),factor));
   int peak=hi(f);if(peak)peak=hi(compare(a,c));put_bit(out,base+x,!peak);
  }
  for(uint32_t x=right;(int32_t)x<(int32_t)count;++x)put_bit(out,base+x,1);
  base+=count;
 }
 for(uint32_t x=0;(int32_t)x<(int32_t)count;++x){
  uint32_t last=UINT32_MAX;
  for(uint32_t radius=0;(int32_t)radius<(int32_t)plateau;){
   if((int32_t)x<(int32_t)(radius+1u)||(int32_t)(x+radius+1u)>=(int32_t)count)break;
   uint32_t a=B(multiply(F(W(in,x*4u)),factor));
   uint32_t l=W(in,(x-radius-1u)*4u);uint32_t r=W(in,(x+radius+1u)*4u);
   uint32_t b=B(multiply(F(l),factor));uint32_t f=compare(b,a);
   uint32_t c=B(multiply(F(r),factor));if(!(f&0x40000000u))break;
   f=compare(a,c);if(lt(f))break;
   f=compare(a,c);last=radius;if(gt(f))break;radius=last+1u;
  }
  if(last+1u && !bit(out,(last+1u)*count+x))for(uint32_t radius=0;(int32_t)radius<=(int32_t)last;++radius)put_bit(out,radius*count+x,0);
 }
}
void r1_goodix_native_int32_max_index(const void *input,uint32_t count,void *maximum,void *index)
{
 uintptr_t p=(uintptr_t)input;uint32_t value=W(p,0),winner=0,left=count-1u;p+=4u;
 while(left){uint32_t v=W(p,0);p+=4u;if((int32_t)value<(int32_t)v){value=v;winner=count-left;}--left;}
 S((uintptr_t)maximum,0,value);S((uintptr_t)index,0,winner);
}
void r1_goodix_native_peak_collapse(const void *matrix,uint32_t count,uint32_t rows,void *flags)
{
 uintptr_t in=(uintptr_t)matrix,out=(uintptr_t)flags;
 for(uint32_t x=0;(int32_t)x<(int32_t)count;++x)for(uint32_t row=0;(int32_t)row<(int32_t)rows;++row)if(bit(in,row*count+x)){*(volatile uint8_t *)(out+x)=1;break;}
}
uint32_t r1_goodix_native_peak_rank(const void *matrix,uint32_t count,uint32_t rows,uint32_t first)
{
 uint32_t length=rows-first+1u;uintptr_t scores=(uintptr_t)goodix_mem_malloc((int32_t)(length*4u));
 int32_t row=(int16_t)(first-1u);
 while(row<(int32_t)rows){uint32_t slot=(uint32_t)row-first+1u;
  for(uint32_t x=0;(int32_t)x<(int32_t)count;++x)S(scores,slot*4u,W(scores,slot*4u)+(bit((uintptr_t)matrix,(uint32_t)row*count+x)?0u:1u));
  row=(int16_t)((uint32_t)row+1u);
 }
 uint32_t maximum=0,index=0;r1_goodix_native_int32_max_index((void *)scores,length,&maximum,&index);goodix_mem_free((void *)scores);return index+first;
}
void r1_goodix_native_peak_columns(const void *input,uint32_t count,const void *configuration,uint32_t mode,void *flags)
{
 uintptr_t cfg=(uintptr_t)configuration;uint32_t rows=W(cfg,0),plateau=W(cfg,4),first=W(cfg,8),product=rows*count;
 uint32_t size=1u+(uint32_t)((int32_t)(product+((uint32_t)((int32_t)product>>31)>>29))>>3);
 void *matrix=goodix_mem_malloc((int32_t)size);__aeabi_memclr(matrix,size);
 r1_goodix_native_peak_grid(input,count,rows,plateau,mode,matrix);
 uint32_t selected=r1_goodix_native_peak_rank(matrix,count,rows,first);r1_goodix_native_peak_collapse(matrix,count,selected,flags);goodix_mem_free(matrix);
}
void r1_goodix_native_peak_select_indices(const void *input,uint32_t count,const void *configuration,uint32_t capacity,uint32_t mode,void *indices,void *index_count)
{
 S((uintptr_t)index_count,0,0);uintptr_t flags=(uintptr_t)goodix_mem_malloc((int32_t)count),out=(uintptr_t)indices,number=(uintptr_t)index_count;
 r1_goodix_native_peak_columns(input,count,configuration,mode,(void *)flags);
 for(uint32_t x=0;(int32_t)x<(int32_t)count;++x)if(!*(const volatile uint8_t *)(flags+x)){
  uint32_t n=W(number,0);if((int32_t)n<(int32_t)capacity){S(out,n*4u,x);S(number,0,W(number,0)+1u);}
  else{memmove((void *)out,(const void *)(out+4u),capacity*4u-4u);S(out,capacity*4u-4u,x);}
 }
 goodix_mem_free((void *)flags);
}
void r1_goodix_native_word_window_push(void *record,uint32_t value)
{
 uintptr_t p=(uintptr_t)record;uint32_t n=H(p,4),capacity=H(p,6);uintptr_t buffer=W(p,0);
 if(n<capacity){S(buffer,n*4u,value);SH(p,4,(uint16_t)(H(p,4)+1u));}
 else{memmove((void *)buffer,(const void *)(buffer+4u),capacity*4u-4u);S(W(p,0),(uint32_t)H(p,6)*4u-4u,value);}
}
void r1_goodix_native_peak_history_append(const void *indices,uint32_t count,uint32_t iteration,void *record)
{
 uintptr_t in=(uintptr_t)indices,p=(uintptr_t)record;uint32_t offset=(iteration-5u)*25u,cursor=H(p,8),last=0,n=H(p,4);
 if(n)last=W(W(p,0),n*4u-4u);SH(p,10,0);
 for(uint32_t x=0;(int32_t)x<(int32_t)count;++x){uint32_t value=W(in,x*4u)+offset;
  if((int32_t)value>(int32_t)last){if((int32_t)cursor>0&&H(p,4)==H(p,6))--cursor;r1_goodix_native_word_window_push(record,value);SH(p,10,(uint16_t)(H(p,10)+1u));}
 }
 SH(p,8,(uint16_t)cursor);n=H(p,4);
 while(n>cursor){if((int32_t)W(W(p,0),cursor*4u)>=(int32_t)offset){SH(p,8,(uint16_t)cursor);break;}++cursor;}
}
void r1_goodix_native_peak_histories_update(const void *input,uint32_t count,uint32_t iteration,const void *configuration,uint32_t capacity,void *records)
{
 uint32_t number=0;void *indices=goodix_mem_malloc((int32_t)(capacity*4u));
 r1_goodix_native_peak_select_indices(input,count,configuration,capacity,0,indices,&number);r1_goodix_native_peak_history_append(indices,number,iteration,records);
 number=0;__aeabi_memclr(indices,capacity*4u);
 r1_goodix_native_peak_select_indices(input,count,configuration,capacity,1,indices,&number);r1_goodix_native_peak_history_append(indices,number,iteration,(void *)((uintptr_t)records+12u));goodix_mem_free(indices);
}
uint32_t r1_goodix_spo2_ratio(void *context,uint32_t iteration,const void *descriptor)
{
 (void)descriptor;uintptr_t record=W((uintptr_t)context,0);uint32_t offset=(uint32_t)H(record,0xdc)*4u-500u;
 uint32_t configuration[3]={36,2,1};uintptr_t input=W(record,0xd8)+offset,history=W((uintptr_t)context,0x1c);
 r1_goodix_native_peak_histories_update((void *)input,125,iteration,configuration,20,(void *)history);return 0;
}
