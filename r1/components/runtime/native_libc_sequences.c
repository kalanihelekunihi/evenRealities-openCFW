#include <stdint.h>
typedef int32_t (*r1_comparator)(const void *,const void *);
void r1_native_qsort(uint8_t *base,uint32_t count,uint32_t width,r1_comparator compare)
{
 if(count<2 || width==0)return;
 int32_t high=(int32_t)(count-1),low=0,direction=-1;
 while(high>low){
  uint8_t *left=base+(uint32_t)low*width,*right=base+(uint32_t)high*width;
  if(compare(left,right)<=0){if(direction<0)--high;else ++low;}
  else{
   for(uint32_t n=0;n<width;++n){uint8_t a=left[n],b=right[n];left[n]=b;right[n]=a;}
   direction=-direction;
  }
 }
 r1_native_qsort(base,(uint32_t)low,width,compare);
 r1_native_qsort(base+((uint32_t)high+1)*width,count-(uint32_t)high-1,width,compare);
}
uint8_t *r1_native_strcat(uint8_t *destination,const uint8_t *source)
{
 uint8_t *out=destination;while(*out)++out;
 uint8_t ch;do{ch=*source++;*out++=ch;}while(ch);
 return destination;
}
uint8_t *r1_native_strncpy(uint8_t *destination,const uint8_t *source,uint32_t length)
{
 uint8_t *out=destination;
 while(length--){uint8_t ch=*source;*out++=ch;if(ch)++source;}
 return destination;
}
int32_t r1_native_memcmp(const uint8_t *a,const uint8_t *b,uint32_t length)
{
 for(uint32_t i=0;i<length;++i){int32_t difference=(int32_t)a[i]-(int32_t)b[i];if(difference)return difference;}
 return 0;
}
/* Native continuation remains at the terminator after exhaustion. */
static uint8_t *volatile *const token_cursor=(uint8_t *volatile *)0x20007db4u;
uint8_t *r1_native_strtok(uint8_t *input,const uint8_t *delimiters)
{
 if(!input)input=*token_cursor;
 uint8_t *start=0;
 while(*input){
  const uint8_t *d=delimiters;while(*d && *d!=*input)++d;
  if(!*d && !start)start=input;
  else if(*d && start){*input++=0;*token_cursor=input;return start;}
  ++input;
 }
 *token_cursor=input;return start;
}
