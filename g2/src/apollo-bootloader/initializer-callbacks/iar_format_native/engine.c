/* Independent recovery of stock 41e47a nonfloating dispatch/emission paths.
 * No full-engine/production completeness claim until floating/termination close. */
#include "engine.h"
#include "format_parser.h"
#include "integer_cursor.h"
#include "record.h"
extern uint64_t opencfw_format_integer_render(void *,unsigned,uint32_t,uint32_t);
extern void opencfw_format_abort_contract(void);
static int constraint(const char *message){
 typedef void (*handler)(const char *,void *,unsigned);
 handler fn=*(handler volatile *)(uintptr_t)0x20027190;
 if(fn)fn(message,0,34);else opencfw_format_abort_contract();return 34;
}
static int put(opencfw_format_put callback,void **context,uint32_t *count,unsigned byte){
 *context=callback(*context,byte);if(!*context)return -1;(*count)++;return 0;
}
static int bytes(opencfw_format_put callback,void **context,uint32_t *count,const uint8_t *p,uint32_t n){while(n--)if(put(callback,context,count,*p++))return -1;return 0;}
static int repeat(opencfw_format_put callback,void **context,uint32_t *count,unsigned byte,int32_t n){while(n-->0)if(put(callback,context,count,byte))return -1;return 0;}
int32_t opencfw_iar_format_core(opencfw_format_put callback,void *context,const char *format,uint32_t **cursor,unsigned mode,uint8_t *frame){
 format_record *record=(format_record *)(void *)(frame+8);
 #define rec (*record)
 *(uint32_t *)(void *)(frame+0xac)=(uint32_t)(uintptr_t)(frame+0x42);
 uint32_t count=0;
 while(*format){
  if(*format!='%'){if(put(callback,&context,&count,(uint8_t)*format++))return -1;continue;}
  opencfw_format_spec spec;const char *conversion=opencfw_format_parse(format,cursor,&spec);unsigned c=(uint8_t)*conversion;format=conversion+1;
  uint8_t *scratch=frame+0x48;rec=(format_record){0};rec.context=(uint32_t)(uintptr_t)context;rec.scratch=rec.digits=(uint32_t)(uintptr_t)scratch;rec.precision=spec.precision;rec.width=spec.width;rec.flags=spec.flags;rec.length=spec.length;rec.mode=(uint8_t)mode;
  if(c=='%'){scratch[rec.prefix_count++]='%';}
  else if(c=='s'){
   const uint8_t *p=(const uint8_t *)(uintptr_t)*(*cursor)++;rec.digits=(uint32_t)(uintptr_t)p;
   if(!p){if((uint8_t)mode){constraint("printf_s: bad %s argument");return -1;}/* Stock fallback points to empty literal; digit_count stays zero. */}
   else{uint32_t n=0;if(rec.precision<0){while(p[n])n++;}else while(n<(uint32_t)rec.precision&&p[n])n++;rec.digit_count=n;}
  }else if(c=='c'){scratch[0]=(uint8_t)*(*cursor)++;rec.prefix_count=1;}
  else if(c=='n'){
   if((uint8_t)mode){constraint("printf_s: %n disallowed");return -1;}
   uintptr_t target=*(*cursor)++;if(!target){constraint("printf: bad %n argument");return -1;}
   if(rec.length=='b')*(volatile uint8_t *)target=(uint8_t)count;
   else if(rec.length=='h')*(volatile uint16_t *)target=(uint16_t)count;
   else if(rec.length=='j'||rec.length=='q'){((volatile uint32_t *)target)[0]=count;((volatile uint32_t *)target)[1]=(int32_t)count<0?UINT32_MAX:0;}
   else *(volatile uint32_t *)target=count;
  }else if(c=='d'||c=='i'||c=='u'||c=='o'||c=='x'||c=='X'||c=='p'){
   if(c=='p'){rec.low=*(*cursor)++;rec.high=0;c='x';}
   else{uint32_t words[2];opencfw_format_integer_fetch(cursor,rec.length,c=='d'||c=='i',words);rec.low=words[0];rec.high=words[1];
    if(c=='d'||c=='i'){if((int32_t)rec.high<0)scratch[rec.prefix_count++]='-';else if(rec.flags&2)scratch[rec.prefix_count++]='+';else if(rec.flags&1)scratch[rec.prefix_count++]=' ';}
    else if((rec.flags&8)&&(rec.low||rec.high)&&((c|32)=='x')){scratch[rec.prefix_count++]='0';scratch[rec.prefix_count++]=(uint8_t)c;}
   }
   rec.digits=(uint32_t)(uintptr_t)(scratch+rec.prefix_count);opencfw_format_integer_render(&rec,c,0,0);
  }else if(c=='a'||c=='A'||c=='e'||c=='E'||c=='f'||c=='F'||c=='g'||c=='G'){
   int status=opencfw_format_float_render(&rec,c,cursor,frame);if(status)return status;
  }else{scratch[rec.prefix_count++]='%';if(c)scratch[rec.prefix_count++]=(uint8_t)c;}
  int32_t spaces=(int32_t)((uint32_t)rec.width-rec.prefix_count-rec.digit_count-rec.trailer_count-rec.leading_zeros-rec.middle_zeros-rec.trailing_zeros);
  if(!(rec.flags&4)&&repeat(callback,&context,&count,' ',spaces))return -1;
  if(bytes(callback,&context,&count,scratch,rec.prefix_count))return -1;
  if(repeat(callback,&context,&count,'0',(int32_t)rec.leading_zeros))return -1;
  if(bytes(callback,&context,&count,(const uint8_t *)(uintptr_t)rec.digits,rec.digit_count))return -1;
  if(repeat(callback,&context,&count,'0',(int32_t)rec.middle_zeros))return -1;
  if(bytes(callback,&context,&count,(const uint8_t *)(uintptr_t)(rec.digits+rec.digit_count),rec.trailer_count))return -1;
  if(repeat(callback,&context,&count,'0',(int32_t)rec.trailing_zeros))return -1;
  if((rec.flags&4)&&repeat(callback,&context,&count,' ',spaces))return -1;
 }
 return (int32_t)count;
 #undef rec
}
/* Compiler-required record clear; independently compiled byte stores. */
void __aeabi_memclr4(void *dst,unsigned n){volatile uint8_t *p=dst;while(n--)*p++=0;}
