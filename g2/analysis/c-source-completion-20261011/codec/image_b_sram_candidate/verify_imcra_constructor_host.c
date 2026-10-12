#include <stdint.h>
#include <stdio.h>
#include <string.h>
extern void *gx8002_image_b_imcra_constructor_1000e784(int32_t,int32_t,void*);
volatile uint32_t gx8002_image_b_imcra_cfg_words_20016fb8[21];
volatile uint32_t gx8002_image_b_imcra_setting_2002d7b4=73;
static uint8_t *base;
static unsigned calls,good;
static float configs[21];
static float fv(uint32_t addr){return configs[(addr-0x20016fb8u)/4u];}
void gx8002_image_b_zero_100113c4(void *p,uint32_t v,uint32_t n){memset(p,(int)v,n);}
void *gx8002_image_b_imcra_a_init_1000ea74(void *p,float a,float b,float c,float d,uint32_t e,float f){calls++;if(p==base+40&&a==fv(0x20016ff4)&&b==fv(0x20016fec)&&c==fv(0x20016fe8)/160&&d==fv(0x20016ff0)/160&&e==73&&f==16000)good++;return p;}
void *gx8002_image_b_imcra_b_init_1000eb54(void *p,float a,float b,float c,float d,float e,float w,float f){calls++;if(p==base+88&&a==fv(0x20016fcc)&&b==fv(0x20016fc4)&&c==fv(0x20016fbc)&&d==fv(0x20016fb8)/160&&e==fv(0x20016fc8)/160&&w==fv(0x20016fc0)&&f==16000)good++;return p;}
void *gx8002_image_b_imcra_c_init_1000ec38(void *p,float a,float b,float c,float d,float e,float f,float g){calls++;if(p==base+140&&a==fv(0x20016fe4)&&b==fv(0x20016fdc)&&c==fv(0x20016fd8)&&d==fv(0x20016fd0)/160&&e==fv(0x20016fe0)/160&&f==fv(0x20016fd4)/160&&g==16000)good++;return p;}
void *gx8002_image_b_imcra_d_init_1000ed7c(void *p,float a,float b,float c,float d,float e){calls++;if(p==base+204&&a==fv(0x20017008)&&b==fv(0x20016ff8)/160&&c==fv(0x20017004)/160&&d==fv(0x20017000)&&e==16000)good++;return p;}
int32_t gx8002_image_b_imcra_d_finish_1000ed2c(void *p,float v){calls++;if(p==base+204&&v==fv(0x20016ffc))good++;return 0;}
int main(void){_Alignas(4) uint8_t bytes[300];base=bytes;memset(bytes,0xff,sizeof bytes);
for(unsigned i=0;i<21;i++){configs[i]=(float)(i+1);uint32_t w;memcpy(&w,&configs[i],4);gx8002_image_b_imcra_cfg_words_20016fb8[i]=w;}

void *r=gx8002_image_b_imcra_constructor_1000e784(16000,160,bytes);uint32_t *h=(uint32_t*)(void*)bytes;
unsigned pass=0;if(r==bytes)pass++;if(calls==5&&good==5)pass++;if(h[0]==16000&&h[1]==160)pass++;
if(h[6]==(uint32_t)(uintptr_t)(base+40)&&h[7]==(uint32_t)(uintptr_t)(base+88)&&h[8]==(uint32_t)(uintptr_t)(base+140)&&h[9]==(uint32_t)(uintptr_t)(base+204))pass++;
if(h[2]==0&&h[3]==0&&h[4]==0&&h[5]==0)pass++;
printf("IMCRA composite native-layout fixtures %u/5\n",pass);return pass!=5;}
float gx8002_image_b_logf_10010768(float x){return x;}
float gx8002_image_b_expf_100109c0(float x){return x;}
uint32_t gx8002_image_b_imcra_a_size_1000ea68(const void *p,int m){(void)p;return m?48u:0u;}
uint32_t gx8002_image_b_imcra_b_size_1000eb48(const void *p,int m){(void)p;return m?52u:0u;}
uint32_t gx8002_image_b_imcra_c_size_1000ec2c(const void *p,int m){(void)p;return m?64u:0u;}
