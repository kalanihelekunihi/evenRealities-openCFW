/* Stock IAR 41f15c..41f270 integer digit/zero-padding helper reconstruction. */
#include <stdint.h>
#include <stddef.h>
typedef struct {uint32_t low,high,unused,digits,scratch,prefix_count,digit_count,unused1,zero_count,unused2,unused3,unused4;int32_t precision,width;uint16_t flags;uint8_t length,mode;} integer_format;
_Static_assert(offsetof(integer_format,flags)==0x38,"stock layout");
static uint64_t divide(uint64_t n,unsigned base,unsigned *remainder){
 if(base==8||base==16){unsigned shift=base==8?3:4;*remainder=(unsigned)n&(base-1);return n>>shift;}
 uint64_t q=0;unsigned r=0;for(int bit=63;bit>=0;bit--){r=(r<<1)|(unsigned)((n>>bit)&1);if(r>=10){r-=10;q|=(uint64_t)1<<bit;}}*remainder=r;return q;
}
uint64_t opencfw_format_integer_render(integer_format *s,unsigned conversion,uint32_t return_low,uint32_t return_high){
 unsigned base=conversion=='o'?8:((conversion|0x20)=='x'?16:10),pos=60;uint64_t n=((uint64_t)s->high<<32)|s->low;
 if((conversion=='d'||conversion=='i')&&(s->high&0x80000000u))n=0-n;
 uint8_t *buf=(uint8_t *)(uintptr_t)s->scratch;
 if(n==0&&s->precision==0){if(base==8&&(s->flags&8))buf[--pos]='0';}
 else{
  return_low=(return_low&0xffffff00u)|(uint8_t)conversion;
  do{unsigned digit;uint64_t q=divide(n,base,&digit);--pos;return_high=pos;buf[pos]=(uint8_t)(digit<10?digit+'0':digit+conversion-33);n=q;if(!n)break;}while(s->digits<(uint32_t)(uintptr_t)(buf+pos));
  if(base==8&&(s->flags&8)&&buf[pos]!='0')buf[--pos]='0';
 }
 s->digit_count=60-pos;s->digits=(uint32_t)(uintptr_t)(buf+pos);
 if((int32_t)s->digit_count<s->precision){s->zero_count=(uint32_t)s->precision-s->digit_count;s->flags&=0xffef;}
 else if(s->precision<0&&(s->flags&0x14)==0x10){int32_t zeros=(int32_t)((uint32_t)s->width-s->prefix_count-s->zero_count-s->digit_count);if(zeros>0)s->zero_count=(uint32_t)zeros;}
 /* Original push r2/r3 slots double as conversion-byte/index scratch,
  * then pop into r0/r1. Preserve observed raw returns; caller ignores them. */
 return ((uint64_t)return_high<<32)|return_low;
}
