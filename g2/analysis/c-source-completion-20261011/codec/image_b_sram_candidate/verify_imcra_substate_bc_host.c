#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
extern void *gx8002_image_b_imcra_b_init_1000eb54(void*,float,float,float,float,float,float,float);
extern void *gx8002_image_b_imcra_c_init_1000ec38(void*,float,float,float,float,float,float,float);
void gx8002_image_b_zero_100113c4(void *p,uint32_t v,uint32_t n){memset(p,(int)v,n);}
float gx8002_image_b_logf_10010768(float x){return logf(x);}
float gx8002_image_b_expf_100109c0(float x){return expf(x);}
int main(void){_Alignas(4) unsigned char b[52],c[64];memset(b,0xff,sizeof b);memset(c,0xff,sizeof c);unsigned pass=0;
if(gx8002_image_b_imcra_b_init_1000eb54(b,1,2,3,0.25f,0.5f,0.75f,16000)==b)pass++;
float *bf=(float*)(void*)b;uint32_t *bw=(uint32_t*)(void*)b;
if(bf[0]==1&&bf[1]==2&&bf[2]==3&&bf[3]==0.25f&&bf[4]==0.5f&&bf[5]==0.75f)pass++;
if(bw[6]==16000&&b[0x30]==1&&bw[7]==0&&bw[8]==0&&bw[11]==0)pass++;
if(bf[9]==expf(-logf(9.0f)/(16000.0f*0.25f))&&bf[10]==expf(-logf(9.0f)/(16000.0f*0.5f)))pass++;
if(gx8002_image_b_imcra_c_init_1000ec38(c,1,2,3,0.25f,0.5f,0.75f,16000)==c)pass++;
float *cf=(float*)(void*)c;uint32_t *cw=(uint32_t*)(void*)c;
if(cf[0]==1&&cf[1]==2&&cf[2]==3&&cf[3]==0.25f&&cf[4]==0.5f&&cf[5]==0.75f)pass++;
if(cw[6]==16000&&c[0x3c]==1&&cw[7]==0&&cw[8]==0&&cw[12]==0&&cw[13]==0&&cw[14]==0)pass++;
if(cf[9]==expf(-logf(9.0f)/(16000.0f*0.25f))&&cf[10]==expf(-logf(9.0f)/(16000.0f*0.5f)))pass++;
if(((int32_t*)c)[11]==12000)pass++;
printf("IMCRA B/C native-layout host fixtures %u/9\n",pass);return pass!=9;}
