#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
extern void *gx8002_image_b_imcra_a_init_1000ea74(void*,float,float,float,float,uint32_t,float);
extern uint32_t gx8002_image_b_imcra_a_size_1000ea68(const void*,int);
extern uint32_t gx8002_image_b_imcra_b_size_1000eb48(const void*,int);
extern uint32_t gx8002_image_b_imcra_c_size_1000ec2c(const void*,int);
void gx8002_image_b_zero_100113c4(void *p,uint32_t v,uint32_t n){memset(p,(int)v,n);}
float gx8002_image_b_logf_10010768(float x){return logf(x);}
float gx8002_image_b_expf_100109c0(float x){return expf(x);}
int main(void){_Alignas(4) unsigned char b[48];memset(b,0xff,sizeof b);unsigned pass=0;
if(gx8002_image_b_imcra_a_size_1000ea68(b,0)==0&&gx8002_image_b_imcra_a_size_1000ea68(b,2)==48)pass++;
if(gx8002_image_b_imcra_b_size_1000eb48(b,0)==0&&gx8002_image_b_imcra_b_size_1000eb48(b,2)==52)pass++;
if(gx8002_image_b_imcra_c_size_1000ec2c(b,0)==0&&gx8002_image_b_imcra_c_size_1000ec2c(b,2)==64)pass++;
if(gx8002_image_b_imcra_a_init_1000ea74(b,0.1f,0.2f,0.3f,0.4f,7,16000.0f)==b)pass++;
float *f=(float*)(void*)b;uint32_t *w=(uint32_t*)(void*)b;
if(f[0]==0.1f&&f[1]==0.2f&&f[2]==0.3f&&f[3]==0.4f)pass++;
if(w[4]==7&&w[5]==16000&&b[0x2c]==1)pass++;
if(f[8]==expf(-logf(9.0f)/(16000.0f*0.3f)))pass++;
if(f[9]==expf(-logf(9.0f)/(16000.0f*0.4f)))pass++;
if(w[6]==0&&w[7]==0&&w[10]==0)pass++;
printf("IMCRA A constructor host native-layout fixtures %u/9\n",pass);return pass!=9;}
