#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <math.h>
#include <stdio.h>
#include <assert.h>
extern void *gx8002_image_b_imcra_d_init_1000ed7c(void *,float,float,float,float,float);
static int calls, zero_calls, pow_calls, log_calls, exp_calls;
void gx8002_image_b_zero_100113c4(void *p,uint32_t v,uint32_t n){assert(v==0&&n==64);zero_calls++; if(p)memset(p,0,n);}
float gx8002_image_b_power_float_100100a4(float b,float e){assert(b==10.0f);pow_calls++;return e+100.0f;}
float gx8002_image_b_logf_entry_100100ac(float x){assert(x==9.0f);log_calls++;return 4.0f;}
double gx8002_image_b_exp_double_1000f84c(double x){assert(x<0);exp_calls++;return 0.125+(double)exp_calls;}
int main(void){unsigned char b[64];memset(b,0x55,sizeof b);assert(gx8002_image_b_imcra_d_init_1000ed7c(b,2.0f,3.0f,4.0f,5.0f,8.0f)==b);assert(zero_calls==1&&pow_calls==1&&log_calls==2&&exp_calls==2);float *p=(float*)b;assert(p[0]==2.0f&&p[1]==3.0f&&p[2]==4.0f&&p[3]==5.0f);assert(p[5]==8.0f&&p[6]==40.0f&&p[7]==100.1f&&p[8]==1.125f&&p[9]==2.125f);assert(gx8002_image_b_imcra_d_init_1000ed7c(NULL,1,2,3,4,5)==NULL);assert(zero_calls==2&&pow_calls==1&&log_calls==2&&exp_calls==2);puts("2/2 IMCRA D native-layout fixtures");return 0;}
