#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
extern int32_t gx8002_image_b_imcra_d_finish_1000ed2c(void*,float);
float gx8002_image_b_power_float_100100a4(float a,float b){return powf(a,b);}
int main(void){_Alignas(4) unsigned char b[64];unsigned pass=0;memset(b,0xa5,sizeof b);
if(gx8002_image_b_imcra_d_finish_1000ed2c(b,1.0f)==-1&&b[0x3c]==0xa5)pass++;
if(gx8002_image_b_imcra_d_finish_1000ed2c(b,-81.0f)==0&&((float*)(void*)b)[15]==0.0f)pass++;
if(gx8002_image_b_imcra_d_finish_1000ed2c(b,-40.0f)==0&&((float*)(void*)b)[4]==-40.0f&&fabsf(((float*)(void*)b)[15]-0.01f)<1e-8f)pass++;
printf("IMCRA D finish native-branch fixtures %u/3\n",pass);return pass!=3;}
