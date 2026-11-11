#include <stdint.h>
/* SEGGER_RTT's two fixed ID copies are the last application references that
 * pulled an executable Newlib archive member into the strict source link. */
__attribute__((noinline,optnone))
char *strcpy(char *restrict destination,const char *restrict source)
{
 char *const start=destination;
 do {*destination++=*source;} while (*source++);
 return start;
}
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

/* Native continuation remains at the terminator after exhaustion. */
uint8_t *volatile r1_strtok_cursor
 __attribute__((section(".bss.r1.libc.strtok.cursor"),aligned(4)));
uint8_t *r1_native_strtok(uint8_t *input,const uint8_t *delimiters)
{
 if(!input)input=r1_strtok_cursor;
 uint8_t *start=0;
 while(*input){
  const uint8_t *d=delimiters;while(*d && *d!=*input)++d;
  if(!*d && !start)start=input;
  else if(*d && start){*input++=0;r1_strtok_cursor=input;return start;}
  ++input;
 }
 r1_strtok_cursor=input;return start;
}
