/* Mechanical semantic reconstruction of41e936..41ef8c, not host snprintf.
 * Decimal digit budgets and rounding retain stock behavior/limitations. */
#include "record.h"
#include <stddef.h>
extern uint64_t opencfw_fp_mul(uint64_t,uint64_t),opencfw_fp_sub(uint64_t,uint64_t),opencfw_fp_div(uint64_t,uint64_t),opencfw_fp_frexp(uint64_t,int *),opencfw_fp_pow10(uint64_t,unsigned),opencfw_fp_from_i32(int32_t),opencfw_fp_from_u32(uint32_t);
extern int32_t opencfw_fp_i32(uint64_t);extern uint32_t opencfw_fp_u32(uint64_t);
static void copy(uint8_t *dst,const uint8_t *src,int n){while(n-->0)*dst++=*src++;}
static int round_digits(uint8_t **start,int count,int available,unsigned half,unsigned zero,unsigned maximum,int *exponent,int carry){
 if(count<0)return count;
 unsigned trim=count<available&&(*start)[count]>=half?maximum:zero;int j=count;
 while((*start)[--j]==trim)count--;
 if(trim==maximum)(*start)[j]++;
 if(j<0){(*start)--;*exponent+=carry;count++;}
 return count;
}
static void append(format_record *r,unsigned c){uint8_t *p=(uint8_t *)(uintptr_t)r->digits;p[r->digit_count++]=(uint8_t)c;}
int opencfw_format_float_render(format_record *r,unsigned c,uint32_t **cursor,uint8_t *frame){
 uint32_t *args=(uint32_t *)(((uintptr_t)*cursor+7)&~(uintptr_t)7);uint64_t raw=((uint64_t)args[1]<<32)|args[0];*cursor=args+2;r->low=args[0];r->high=args[1];*(uint32_t *)(void *)(frame+0xb0)=args[0];*(uint32_t *)(void *)(frame+0xb4)=args[1];
 uint8_t *scratch=(uint8_t *)(uintptr_t)r->scratch;
 if(raw>>63)scratch[r->prefix_count++]='-';else if(r->flags&2)scratch[r->prefix_count++]='+';else if(r->flags&1)scratch[r->prefix_count++]=' ';
 r->digits=(uint32_t)(uintptr_t)(scratch+r->prefix_count);uint64_t magnitude=raw&UINT64_C(0x7fffffffffffffff);unsigned lower=c|32;
 if((magnitude>>52)==0x7ff){const uint8_t *text=(const uint8_t *)((magnitude&UINT64_C(0xfffffffffffff))?(c>='a'&&c<='z'?"nan":"NAN"):(c>='a'&&c<='z'?"inf":"INF"));copy((uint8_t *)(uintptr_t)r->digits,text,3);r->digit_count=3;return 0;}
 if(lower!='a'){if(r->precision<0)r->precision=6;else if(r->precision==0&&lower=='g')r->precision=1;}
 int exponent;uint64_t fraction=opencfw_fp_frexp(raw,&exponent);fraction&=UINT64_C(0x7fffffffffffffff);
 if(lower=='a'){uint8_t *p=(uint8_t *)(uintptr_t)r->digits;p[0]='0';p[1]=(c=='a'?'x':'X');r->digits+=2;r->prefix_count+=2;}
 uint8_t *buffer=frame+0x84;uint8_t *digits=buffer+1;int count=0;
 if(!magnitude){exponent=0;}
 else if(lower=='a'){
  int need=r->precision<0?33:(int32_t)((uint32_t)r->precision+1);int budget=(int32_t)((uint32_t)need+1);buffer[0]=0;exponent-=4;
  /* The stock comparison helper treats both signs of zero as zero. Under
   * round-toward-minus-infinity an exact subtraction can produce -0. */
  while(budget>0&&(fraction&UINT64_C(0x7fffffffffffffff))){fraction+=UINT64_C(28)<<52;int32_t part=opencfw_fp_i32(fraction);budget-=7;
   if(budget>0)fraction=opencfw_fp_sub(fraction,opencfw_fp_from_i32(part));
   for(int j=6;j>=0;j--){digits[count+j]=(uint8_t)((uint32_t)part&15);part>>=4;}count+=7;
  }
  int keep=count<=need?count:need;keep=round_digits(&digits,keep,count,8,0,15,&exponent,4);count=keep;
  for(int i=count-1;i>=0;i--)digits[i]=(uint8_t)(digits[i]<10?digits[i]+'0':digits[i]+c-10);
  if(r->precision<0)r->precision=count-1;
 }else{
  exponent=exponent*30103/100000;int scale=7-exponent;uint64_t value=scale>0?opencfw_fp_pow10(magnitude,(unsigned)scale):opencfw_fp_div(magnitude,opencfw_fp_pow10(UINT64_C(0x3ff0000000000000),(unsigned)-scale));
  int budget=(int32_t)((uint32_t)r->precision+(uint32_t)(lower=='f'?exponent+10:6));if(budget>20)budget=20;buffer[0]='0';
  /* Stock consumes prior bytes when no digits were generated. The entry
   * frame/pointer at+0xac bounds this scan and preserves the physical input. */
  while(budget>0){uint32_t part=opencfw_fp_u32(value);uint32_t original=part;for(int j=7;j>=0;j--){digits[count+j]=(uint8_t)('0'+part%10);part/=10;}count+=8;budget-=8;
   if(budget>0)value=opencfw_fp_mul(opencfw_fp_sub(value,opencfw_fp_from_u32(original)),UINT64_C(0x4197d78400000000));
  }
  while(*digits=='0'){digits++;count--;exponent--;}
  int keep=(int32_t)((uint32_t)r->precision+(uint32_t)(lower=='f'?exponent+1:lower=='e'?1:0));if(count<keep)keep=count-1;count=round_digits(&digits,keep,count,'5','0','9',&exponent,1);
 }
 unsigned decimal=**(volatile uint8_t **)(uintptr_t)0x2000053c;int precision=r->precision;
 if((int16_t)count<=0){digits=(uint8_t *)"0";count=1;}
 int fixed=lower=='f';if(fixed)exponent++;
 else if(lower=='g'){
  if((int16_t)exponent>=-4&&(int16_t)exponent<precision){fixed=1;exponent++;if(!(r->flags&8)&&count<=precision)precision=count;precision-=(int16_t)exponent;if(precision<0)precision=0;}
  else{if(count<precision&&!(r->flags&8))precision=count;precision--;if(precision<0)precision=0;c=(c=='g'?'e':'E');}
 }else if(c=='a')c='p';else if(c=='A')c='P';
 uint8_t *out=(uint8_t *)(uintptr_t)r->digits;
 if(fixed){
  int places=(int16_t)exponent;
  if(places<=0){append(r,'0');if(precision>0||(r->flags&8))append(r,decimal);int leading=places;if(precision+places<0)leading=-precision;r->middle_zeros=(uint32_t)-leading;int available=precision+leading;if(available<count)count=available;r->trailer_count=(int16_t)count;copy(out+r->digit_count,digits,(int16_t)count);r->trailing_zeros=(uint32_t)(available-(int16_t)count);}
  else if((int16_t)count<places){copy(out+r->digit_count,digits,(int16_t)count);r->digit_count+=(int16_t)count;r->middle_zeros=places-(int16_t)count;if(precision>0||(r->flags&8)){out[r->digit_count]=(uint8_t)decimal;r->trailer_count++;}r->trailing_zeros=precision;}
  else{copy(out+r->digit_count,digits,places);r->digit_count+=places;count-=exponent;if(precision>0||(r->flags&8))append(r,decimal);if(precision<(int16_t)count)count=precision;copy(out+r->digit_count,digits+places,(int16_t)count);r->digit_count+=(int16_t)count;r->middle_zeros=precision-(int16_t)count;}
 }else{
  append(r,*digits++);if(precision>0||(r->flags&8)){append(r,decimal);if(precision>0){count--;if(precision<(int16_t)count)count=precision;copy(out+r->digit_count,digits,(int16_t)count);r->digit_count+=(int16_t)count;r->middle_zeros=precision-(int16_t)count;}}
  uint8_t *tail=out+r->digit_count,*begin=tail;*tail++=(uint8_t)c;int e=(int16_t)exponent;*tail++=e<0?'-':'+';if(e<0)e=-e;uint8_t numbers[6];int n=0;while((int16_t)e>0){numbers[n++]=(uint8_t)(e%10);e/=10;}if(n<=1&&(c|32)=='e')*tail++='0';if(!n)*tail++='0';else while(n)*tail++=(uint8_t)('0'+numbers[--n]);r->trailer_count=(uint32_t)(tail-begin);
 }
 if((r->flags&0x14)==0x10){uint32_t total=r->prefix_count+r->digit_count+r->middle_zeros+r->trailer_count+r->trailing_zeros;if((int32_t)total<r->width)r->leading_zeros=(uint32_t)r->width-total;}
 return 0;
}
