/* Independent original48cc and IIR4fde. Explicit unsigned product preserves
 * stock32-bit multiplication before signed division. No analog scan dependency. */
#include "slider.h"
static uint32_t divide(uint32_t n,uint32_t d){uint32_t q=0;for(unsigned k=32;k;k--){unsigned i=k-1;if(d<=(n>>i)){n-=d<<i;q+=1u<<i;}}return q;}
static int32_t signed_divide(int32_t n,int32_t d){return n<0?-(int32_t)divide(0u-(uint32_t)n,(uint32_t)d):(int32_t)divide((uint32_t)n,(uint32_t)d);}
uint32_t touch_position_iir(uint32_t sample,uint32_t prior,uint32_t coefficient){return (sample*coefficient+prior*(256u-coefficient))>>8;}
void touch_linear_centroid(uint8_t *t,const uint8_t *w){
 uint32_t n=*(const uint16_t *)(w+56),config=*(const uint32_t *)(w+48);if(n<3)n=3;
 if((config&3u)!=1)return;
 const uint8_t *s=*(const uint8_t **)(w+4);uint32_t peak=0,maxsum=0,index=0xffffffffu;int32_t numerator=0;
 for(uint32_t i=0;i<n;i++){uint32_t d=*(const uint16_t *)(s+10*i+4);if(d>peak)peak=d;}
 for(uint32_t i=0;i<n;i++)if(*(const uint16_t *)(s+10*i+4)==peak){
  uint32_t left=i?*(const uint16_t *)(s+10*(i-1)+4):0,right=i+1<n?*(const uint16_t *)(s+10*(i+1)+4):0;
  uint32_t sum=peak+left+right;if(sum>maxsum){maxsum=sum;index=i;numerator=(int32_t)right-(int32_t)left;}
 }
 if(index==0xffffffffu || !maxsum){t[4]=0;return;}
 uint32_t scaled=(uint32_t)*(const uint16_t *)(w+52)<<8,multiplier=divide(scaled,(config&256u)?n:n-1),offset=(config&256u)?multiplier>>1:0;
 int32_t fraction=signed_divide((int32_t)((uint32_t)numerator*multiplier),(int32_t)maxsum);
 uint32_t result=index*multiplier+offset+(uint32_t)fraction;
 t[4]=1;**(uint16_t **)t=(uint16_t)((result+127u)>>8);
}
