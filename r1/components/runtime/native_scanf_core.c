#include <stdint.h>
extern int32_t r1_native_scanf_integer(int32_t,void *,uint32_t,volatile uint32_t *);
extern int32_t r1_native_scanf_string(int32_t,void *,volatile uint32_t *,const uint32_t *,uint32_t);
typedef int32_t (*input_fn)(void *);
typedef uint32_t (*format_fn)(volatile uint32_t *,uint32_t);
typedef uint32_t (*space_fn)(uint32_t);
static uint32_t format(volatile uint32_t *d,uint32_t advance){return ((format_fn)(uintptr_t)d[5])(d+3,advance);}
static int32_t get(void *input,volatile uint32_t *d){return ((input_fn)(uintptr_t)d[6])(input);}
static void unget(void *input,volatile uint32_t *d){((input_fn)(uintptr_t)d[7])(input);}
static uint32_t space(uint32_t ch,volatile uint32_t *d){return ((space_fn)(uintptr_t)d[8])(ch);}
/* Native data literal at 0x286f0, not a generic libc width policy. */
__attribute__((section(".r1.scanf.width_limit"),used))
const uint32_t r1_native_scanf_width_limit=UINT32_C(0x0ccccccc);
int32_t r1_native_scanf_core(void *input,volatile uint32_t *d)
{
 uint32_t assignments=0,consumed=0,first_conversion=1;
 /* Source descriptor initialization guarantees d[4]==0. Alternate descriptor
  * modes expose native private-frame state and remain a separate ABI gate. */
 uint32_t set[8];
 for(;;){
  uint32_t ch=format(d,1);
  if(!ch)return (int32_t)assignments;
  if(ch!='%'){
   if(space(ch,d)){
    do{ch=format(d,1);}while(space(ch,d));
    format(d,UINT32_MAX);
    int32_t input_ch;while((input_ch=get(input,d),space((uint32_t)input_ch,d)))++consumed;
    unget(input,d);
   }else{
    int32_t input_ch=get(input,d);
    if((uint32_t)input_ch!=ch){unget(input,d);return input_ch==-1 && !assignments ? -1 : (int32_t)assignments;}
    ++consumed;
   }
   continue;
  }
  uint32_t flags=0,width=0;
  if(format(d,0)=='*'){format(d,1);flags=1;}
  for(;;){
   ch=format(d,1);
   if(ch-48u>=10u)break;
   if((int32_t)width>(int32_t)r1_native_scanf_width_limit)return (int32_t)assignments;
   width=width*10u+ch-48u;
   if((int32_t)width<0)return (int32_t)assignments;
   flags|=0x10;
  }
  if(!(flags&0x10))width=INT32_MAX;
  if(ch=='l'){ch=format(d,1);if(ch=='l'){flags|=2;ch=format(d,1);}else flags|=4;}
  else if(ch=='L'){flags|=0x20;ch=format(d,1);}
  else if(ch=='h'){ch=format(d,1);if(ch=='h'){flags|=0x800;ch=format(d,1);}else flags|=8;}
  else if(ch=='j'){flags|=2;ch=format(d,1);}
  else if(ch=='t' || ch=='z')ch=format(d,1);
  d[1]=flags;d[2]=width;
  if(ch=='%'){
   int32_t input_ch=get(input,d);
   if(input_ch!='%'){unget(input,d);return input_ch==-1 && !assignments ? -1 : (int32_t)assignments;}
   ++consumed;continue;
  }
  if(ch=='n'){
   if(!(flags&1)){
    uint32_t arguments=d[0];d[0]=arguments+4;
    volatile void *out=(volatile void *)(uintptr_t)*(const volatile uint32_t *)(uintptr_t)arguments;
    if(flags&0x800)*(volatile uint8_t *)out=(uint8_t)consumed;
    else if(flags&8)*(volatile uint16_t *)out=(uint16_t)consumed;
    else if(flags&2){((volatile uint32_t *)out)[0]=consumed;((volatile uint32_t *)out)[1]=(int32_t)consumed<0 ? UINT32_MAX : 0;}
    else *(volatile uint32_t *)out=consumed;
   }
   continue;
  }
  int32_t status=-2;
  switch(ch){
   case 'A':case 'a':case 'E':case 'e':case 'F':case 'f':case 'G':case 'g':
    /* Authenticated NOP call sites return the preset -2; this image has no
     * floating scanf implementation on these paths. */
    break;
   case 'd':case 'u':case 'i':case 'o':case 'x':case 'X':case 'p':{
    uint32_t radix=ch=='i' ? 0 : ch=='o' ? 8 : ch=='x' || ch=='X' || ch=='p' ? 16 : 10;
    if(ch=='p')d[1]=flags&~UINT32_C(0x80e);else d[1]=flags|0x40;
    if(ch=='p' || !(flags&2))status=r1_native_scanf_integer(-2,input,radix,d);
    /* Long-long integer call sites are also authenticated NOPs. */
    break;
   }
   case 'c':case 's':case '[':{
    uint32_t character_mode=ch=='c';const uint32_t *selection=0;
    if(character_mode){if(!(flags&0x10))d[2]=1;}
    else if(ch=='['){
     uint32_t entry=format(d,1),invert=entry=='^';
     if(invert)entry=format(d,1);
     if(!d[4])for(uint32_t i=0;i<8;++i)set[i]=0;
     do{
      if(!entry)return (int32_t)assignments;
      if(!d[4]){
       int32_t signed_entry=(int32_t)entry,quotient=signed_entry/32,remainder=signed_entry-quotient*32;
       uint32_t shift=(uint32_t)remainder&255u;
       set[quotient]|=shift<32 ? UINT32_C(1)<<shift : 0;
      }
      entry=format(d,1);
     }while(entry!=']');
     if(invert)for(uint32_t i=0;i<8;++i)set[i]=~set[i];
     selection=set;
    }
    status=r1_native_scanf_string(-2,input,d,selection,character_mode);break;
   }
   default:return (int32_t)assignments;
  }
  if(status<0)return status==-1 && first_conversion ? -1 : (int32_t)assignments;
  if(!(flags&1))++assignments;
  consumed+=(uint32_t)status;first_conversion=0;
 }
}
