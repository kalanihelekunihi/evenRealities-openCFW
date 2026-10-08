#include <stdint.h>
extern void *opencfw_iar_fill_native(void *,uint32_t,uint32_t);
extern void *opencfw_iar_aligned_copy_native(void *,const void *,uint32_t);
static unsigned char a[320] __attribute__((aligned(16))),b[320] __attribute__((aligned(16))),input[320] __attribute__((aligned(16)));
static uint32_t unused_call3(uint32_t fn,uint32_t x,uint32_t y,uint32_t z){return ((uint32_t(*)(uint32_t,uint32_t,uint32_t))(uintptr_t)fn)(x,y,z);}
extern uint32_t call3_record(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t *);
static uint32_t one[13],two[13];
static void write(const char*s){register uint32_t r0 __asm__("r0")=4;register const char*r1 __asm__("r1")=s;__asm__ volatile("bkpt #0xab" : "+r"(r0) :"r"(r1):"memory");}
static void number(uint32_t n){char t[12],out[12];int k=0,j=0;do{t[k++]=(char)('0'+n%10);n/=10;}while(n);while(k)out[j++]=t[--k];out[j]=0;write(out);}
static void fail(uint32_t k,uint32_t n,uint32_t i,uint32_t x,uint32_t y){write("FAIL ");number(k);write(" ");number(n);write(" ");number(i);write(" ");number(x);write(" ");number(y);write("\n");}
static const uint32_t lengths[]={0,1,2,3,4,7,8,9,15,16,17,20,21,31,32,33,40,63,64,127,256};
static const uint32_t values[]={0,1,127,128,255,0x12345678};
int main(void){uint32_t cases=0;
 for(uint32_t v=0;v<6;v++)for(uint32_t off=0;off<4;off++)for(uint32_t j=0;j<21;j++){
  uint32_t n=lengths[j];for(uint32_t i=0;i<320;i++)a[i]=b[i]=(uint8_t)(i*37+19);
  uint32_t x=call3_record(0x4560d,(uint32_t)(a+off),n,values[v],one);uint32_t y=call3_record((uint32_t)opencfw_iar_fill_native,(uint32_t)(b+off),n,values[v],two);
  if(x!=(uint32_t)(a+off)||y!=(uint32_t)(b+off)){fail(0,n,off,x-(uint32_t)a,y-(uint32_t)b);return 1;}
  if(one[1]!=one[12]||two[1]!=two[12]){fail(4,n,off,one[1]-one[12],two[1]-two[12]);return 1;}
  for(uint32_t k=2;k<10;k++)if(one[k]!=(0x4002u+k)||two[k]!=(0x4002u+k)){fail(5,n,k,one[k],two[k]);return 1;}
  if(one[10]!=two[10]||one[11]!=two[11]){fail(6,n,off,one[10],two[10]);return 1;}
  for(uint32_t i=0;i<320;i++)if(a[i]!=b[i]){fail(1,n,i,a[i],b[i]);return 1;}cases++;
 }
 for(uint32_t so=0;so<4;so++)for(uint32_t d=0;d<4;d++)for(uint32_t j=0;j<21;j++){
  uint32_t n=lengths[j],off=d*4;for(uint32_t i=0;i<320;i++){a[i]=b[i]=(uint8_t)(i*37+19);input[i]=(uint8_t)(i*13+7);}
  uint32_t x=call3_record(0x456ad,(uint32_t)(a+off),(uint32_t)(input+so*4),n,one);uint32_t y=call3_record((uint32_t)opencfw_iar_aligned_copy_native,(uint32_t)(b+off),(uint32_t)(input+so*4),n,two);
  if(x-(uint32_t)a!=y-(uint32_t)b){fail(2,n,off,x-(uint32_t)a,y-(uint32_t)b);return 1;}
  if(one[1]!=one[12]||two[1]!=two[12]){fail(4,n,off,one[1]-one[12],two[1]-two[12]);return 1;}
  for(uint32_t k=2;k<10;k++)if(one[k]!=(0x4002u+k)||two[k]!=(0x4002u+k)){fail(5,n,k,one[k],two[k]);return 1;}
  if(one[10]!=two[10]||one[11]!=two[11]){fail(6,n,off,one[10],two[10]);return 1;}
  for(uint32_t i=0;i<320;i++)if(a[i]!=b[i]){fail(3,n,i,a[i],b[i]);return 1;}cases++;
 }
 write("PASS_MEMORY ");number(cases);write("\n");return 0;
}
