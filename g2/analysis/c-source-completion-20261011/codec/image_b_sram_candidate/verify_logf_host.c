#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
extern float gx8002_image_b_logf_10010768(float);
static uint32_t bits(float x){uint32_t u;memcpy(&u,&x,4);return u;}
int main(void){uint32_t seed=0x15c4a870u;unsigned exact=0,near=0,bad=0,excluded=0;
for(unsigned i=0;i<30000;i++){seed=seed*1664525u+1013904223u;uint32_t v=seed&0x7fffffffu;if(v==0||v>=0x7f800000u){excluded++;continue;}float x;memcpy(&x,&v,4);
float a=gx8002_image_b_logf_10010768(x),b=logf(x);if(bits(a)==bits(b)) exact++;
else if(isfinite(a)&&isfinite(b)&&fabsf(a-b)<1.0e-6f*fmaxf(1.0f,fabsf(b)))near++;
else{if(bad<10)fprintf(stderr,"%08x got=%08x want=%08x\n",v,bits(a),bits(b));bad++;}}
printf("log host finite exact=%u near=%u excluded=%u bad=%u\n",exact,near,excluded,bad);return bad!=0;}
