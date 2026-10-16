#include <stdint.h>
extern uint32_t r1_native_scanf_digit(uint32_t,uint32_t);
typedef int32_t (*input_callback)(void *);
typedef int32_t (*space_callback)(int32_t);
static int32_t get(void *input,volatile uint32_t *descriptor){return ((input_callback)(uintptr_t)descriptor[6])(input);}
static void unget(void *input,volatile uint32_t *descriptor){((input_callback)(uintptr_t)descriptor[7])(input);}
static int32_t space(int32_t ch,volatile uint32_t *descriptor){return ((space_callback)(uintptr_t)descriptor[8])(ch);}
int32_t r1_native_scanf_input_getc(volatile uint32_t *input)
{
 uint32_t remaining=input[1];
 if(remaining){uint32_t current=input[0];uint32_t ch=*(const volatile uint8_t *)(uintptr_t)current;
  if(ch){input[0]=current+1;input[1]=remaining-1;return (int32_t)ch;}}
 input[3]=1;return -1;
}
int32_t r1_native_scanf_input_ungetc(volatile uint32_t *input)
{
 uint32_t remaining=input[1];
 if(remaining){uint32_t eof=input[3],current=input[0];
  if(!eof && input[2]!=current){input[0]=current-1;input[1]=remaining+1;return 0;}}
 return -1;
}
static volatile void *next_output(volatile uint32_t *descriptor)
{
 uint32_t arguments=descriptor[0];descriptor[0]=arguments+4;
 return (volatile void *)(uintptr_t)*(const volatile uint32_t *)(uintptr_t)arguments;
}
int32_t r1_native_scanf_integer(int32_t initial,void *input,uint32_t radix,volatile uint32_t *descriptor)
{
 (void)initial;
 uint32_t flags=descriptor[1],width=descriptor[2],consumed=UINT32_MAX,value=0;int32_t ch;
 do{++consumed;ch=get(input,descriptor);}while(space(ch,descriptor));
 if(ch==-1)return -1;
 flags&=~UINT32_C(0x600);
 if((int32_t)width>0){
  if((flags&0x40) && (ch=='+' || ch=='-')){
   if(ch=='-')flags|=0x400;
   ++consumed;ch=get(input,descriptor);--width;
   if((int32_t)width<=0)goto default_radix;
  }
  if(ch=='0'){
   --width;flags|=0x200;++consumed;ch=get(input,descriptor);
   if((int32_t)width>0 && (ch=='x' || ch=='X')){
    if(radix==0 || radix==16){--width;flags&=~UINT32_C(0x200);++consumed;ch=get(input,descriptor);radix=16;}
   }else if(radix==0)radix=8;
   goto digits;
  }
 }
default_radix:
 if(!radix)radix=10;
digits:
 while((int32_t)width>0){
  uint32_t digit=r1_native_scanf_digit((uint32_t)ch,radix);if((int32_t)digit<0)break;
  value=value*radix+digit;--width;flags|=0x200;++consumed;ch=get(input,descriptor);
 }
 unget(input,descriptor);
 if(!(flags&0x200))return -2;
 if(!(flags&1)){
  if((flags&0x40) && (flags&0x400))value=0-value;
  volatile void *out=next_output(descriptor);
  if(flags&0x800)*(volatile uint8_t *)out=(uint8_t)value;
  else if(flags&8)*(volatile uint16_t *)out=(uint16_t)value;
  else *(volatile uint32_t *)out=value;
 }
 return (int32_t)consumed;
}
int32_t r1_native_scanf_string(int32_t initial,void *input,volatile uint32_t *descriptor,const uint32_t *set,uint32_t character_mode)
{
 (void)initial;
 uint32_t flags=descriptor[1],width=descriptor[2],consumed=0;volatile uint8_t *output=0;
 int32_t ch=get(input,descriptor);
 if(!set && !character_mode){while(space(ch,descriptor)){++consumed;ch=get(input,descriptor);}}
 if(ch==-1)return -1;
 if(!(flags&1))output=next_output(descriptor);
 while((int32_t)width>0 && ch!=-1){
  if(set){
   /* Native signed quotient/remainder with ARM register shift semantics. */
   int32_t quotient=ch/32,remainder=ch-quotient*32;uint32_t shift=(uint32_t)remainder&255;
   if(!(set[quotient]&(shift<32 ? UINT32_C(1)<<shift : 0)))break;
  }else if(!character_mode && space(ch,descriptor))break;
  if(!(flags&1))*output++=(uint8_t)ch;
  ++consumed;--width;ch=get(input,descriptor);
 }
 unget(input,descriptor);
 if(!character_mode && (int32_t)consumed>0 && !(flags&1))*output=0;
 if((int32_t)descriptor[2]<=(int32_t)width || (character_mode && width))return -2;
 return (int32_t)consumed;
}
