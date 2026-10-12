#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
extern float gx8002_image_b_sqrtf_10010bcc(float);
static uint32_t bits(float x) { uint32_t u; memcpy(&u,&x,4);return u; }
int main(void) {
    uint32_t s=0x12345678; unsigned exact=0, special=0, bad=0;
    for(unsigned i=0;i<50000;i++) {
      s=s*1664525u+1013904223u;
      uint32_t word=s&0x7fffffffu; if(word>=0x7f800000u) {special++;continue;}
      float x; memcpy(&x,&word,4);
      float got=gx8002_image_b_sqrtf_10010bcc(x),ref=sqrtf(x);
      if(bits(got)==bits(ref)) exact++;
      else { if(bad<10)fprintf(stderr,"%08x got %08x want %08x\n",word,bits(got),bits(ref));bad++; }
    }
    printf("sqrt host finite exact=%u excluded_special=%u bad=%u\n",exact,special,bad);
    return bad!=0;
}
