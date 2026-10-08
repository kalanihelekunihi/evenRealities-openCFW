/* Independently reconstructed class4/5/6 configuration children from locked
 * bootloader f89a4c46. Hz-like constants are raw values until units are proved.
 * Generator children remain explicit dependencies; no vendor source import. */
#include <stdint.h>
#include <stddef.h>
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
extern uint32_t opencfw_boot_startup_hf2_generate(uint32_t,uint32_t,uint32_t,uint32_t *);
extern uint32_t opencfw_boot_startup_pll_generate(uint8_t *,uint32_t,uint32_t);
extern uint32_t opencfw_bl_clock_request_id2(uint8_t);
extern uint32_t opencfw_bl_clock_request_id3(uint8_t);
extern uint32_t opencfw_bl_clock_release_id2(uint8_t);
extern uint32_t opencfw_bl_clock_release_id3(uint8_t);
/* Same already reconstructed82-byte leaf as clock_class_provider5.c. */
uint32_t opencfw_boot_startup_hf2_apply(const uint8_t *config){
 if(!config)return 6;
 W(0x4000404c)|=7u;
 W(0x40004048)=(W(0x40004048)&0xdfffffffu)|((config[0]&1u)<<29);
 W(0x40004050)=(W(0x40004050)&0xfffffffcu)|(config[1]&3u);
 W(0x40004050)=(W(0x40004050)&0x80000003u)|(((*(const uint32_t *)(const void *)(config+4))&0x1fffffffu)<<2);
 W(0x40004048)|=1u;return 0;
}
static uint32_t save(void){uint32_t v;__asm__ volatile("mrs %0,primask\n cpsid i":"=r"(v)::"memory");return v;}
static void restore(uint32_t v){__asm__ volatile("msr primask,%0"::"r"(v):"memory");}
static uint32_t users(unsigned c){uint32_t a=W(0x20026e74+c*8),b=W(0x20026e78+c*8),n=0;while(a){n+=a&1;a>>=1;}while(b){n+=b&1;b>>=1;}return n;}
static void copy12(uint32_t dest,const void *src){volatile uint8_t *q=(volatile uint8_t *)(uintptr_t)dest;const uint8_t *p=src;for(unsigned i=0;i<12;i++)q[i]=p[i];}
static uint32_t hf1_apply(uint32_t v){W(0x40004020)=v|1;return 0;}
static uint32_t hf1_default(void){W(0x40004020)&=~1u;return 0;}
static uint32_t hf2_default(void){W(0x40004048)&=~1u;return 0;}
uint32_t opencfw_boot_startup_select4(uint32_t value,const uint32_t *input){
 uint32_t local[3]={0x25b800,0,0},status=0;
 if(value!=0&&value!=48000000)return 5;
 if(value&&input==NULL){uint32_t reference=W(0x20000088);if(!reference)return 7;uint32_t quotient;__asm__("udiv %0,%1,%2":"=r"(quotient):"r"(value),"r"(reference));local[0]=(local[0]&~0xfff00u)|((quotient&0xfffu)<<8);input=local;}
 uint32_t irq=save();
 if(users(4)){
  status=3;
  if((value==0||value==48000000)&&(W(0x20027030)==0||W(0x20027030)==48000000)){
   status=value?hf1_apply(input[0]):hf1_default();
   if(status)(void)hf1_apply(W(0x20026fec));
  }
 }else if(value!=W(0x20027030)){
  (void)hf1_default();B(0x2002719c)=0;W(0x20027044)=0;
 }
 if(!status){if(value)copy12(0x20026fec,input);W(0x20027030)=value;B(0x20000550)=1;}
 restore(irq);return status;
}
uint32_t opencfw_boot_startup_select5(uint32_t value,const uint8_t *input){
 uint32_t local[3]={0x200,0xc49ba,0};uint8_t *bytes=(uint8_t *)local;uint32_t status=0,hot=0;
 uint32_t compatible=(value==0||value==250000000)&&(W(0x20027034)==0||W(0x20027034)==250000000);
 if(value!=0&&value!=196608000&&value!=250000000)return 5;
 if(value){
  if(input==NULL){uint32_t reference=W(0x20000080);if(reference)bytes[0]=0;else{reference=W(0x2000008c);if(!reference)return 7;bytes[0]=1;}status=opencfw_boot_startup_hf2_generate(reference,value,bytes[1],&local[1]);input=bytes;}
  else{if(input[0]==0&&!W(0x20000080))return 7;if(input[0]==1&&!W(0x2000008c))return 7;}
 }
 if(status)return status;
 uint32_t irq=save();if(users(5)){if(compatible)hot=1;else status=3;}
 if(!status){if(value)copy12(0x20026ff8,input);W(0x20027034)=value;B(0x20000551)=1;}
 restore(irq);
 if(hot){
  if(B(0x20026ff8)==0)(void)opencfw_bl_clock_request_id2(0x36);else(void)opencfw_bl_clock_request_id3(0x36);
  irq=save();
  if(users(5)){
   if(W(0x20027034)==0)status=hf2_default();
   else{status=opencfw_boot_startup_hf2_apply((const uint8_t *)0x20026ff8);if(!status){if(B(0x20026ff8)==0)(void)opencfw_bl_clock_release_id3(0x36);else(void)opencfw_bl_clock_release_id2(0x36);}}
   if(status||W(0x20027034)==0){(void)opencfw_bl_clock_release_id3(0x36);(void)opencfw_bl_clock_release_id2(0x36);}
  }else{(void)opencfw_bl_clock_release_id2(0x36);(void)opencfw_bl_clock_release_id3(0x36);}
  restore(irq);
 }
 return status;
}
uint32_t opencfw_boot_startup_select6(uint32_t value,const uint8_t *input){
 uint32_t local[3]={0,0,0},status=0;uint8_t *bytes=(uint8_t *)local;
 if(input==NULL){uint32_t reference=W(0x20000080);if(reference)bytes[0]=0;else{reference=W(0x2000008c);if(!reference)return 7;bytes[0]=1;}status=opencfw_boot_startup_pll_generate(bytes,reference,value);input=bytes;}
 else{if(input[0]==0&&!W(0x20000080))return 7;if(input[0]==1&&!W(0x2000008c))return 7;}
 if(status)return status;
 uint32_t irq=save();if(users(6))status=3;
 if(!status){copy12(0x20027004,input);W(0x20027038)=value;B(0x2002719a)=1;}
 restore(irq);return status;
}
