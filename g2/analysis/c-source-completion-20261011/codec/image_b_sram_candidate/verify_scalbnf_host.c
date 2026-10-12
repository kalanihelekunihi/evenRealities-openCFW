#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
extern float gx8002_image_b_scalbnf_10011194(float,int);
static uint32_t bits(float x){uint32_t u;memcpy(&u,&x,4);return u;}
int main(void){uint32_t seed=0x814f5732u;int ns[]={-200,-150,-25,-1,0,1,25,100,200};unsigned good=0,excluded=0,bad=0;
for(unsigned i=0;i<20000;i++){seed=seed*1664525u+1013904223u;uint32_t v=seed;if((v&0x7f800000u)==0x7f800000u){excluded++;continue;}float x;memcpy(&x,&v,4);
for(unsigned j=0;j<sizeof(ns)/sizeof(*ns);j++){float a=gx8002_image_b_scalbnf_10011194(x,ns[j]);float b=scalbnf(x,ns[j]);if(bits(a)==bits(b))good++;else{if(bad<10)fprintf(stderr,"%08x %d got=%08x want=%08x\n",v,ns[j],bits(a),bits(b));bad++;}}}
printf("scalbn host finite exact=%u excluded_special=%u bad=%u\n",good,excluded,bad);return bad!=0;}
