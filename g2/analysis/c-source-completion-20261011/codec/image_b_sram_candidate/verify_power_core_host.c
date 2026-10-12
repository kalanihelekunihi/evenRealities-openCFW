/* Bounded algorithm sanity only: host libm is not the C-SKY native oracle. */
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
extern float gx8002_image_b_power_float_core_100100bc(float, float);
static uint32_t bits(float f) { uint32_t u; memcpy(&u,&f,4); return u; }
int main(void) {
  static const float x[] = {0.125f,0.5f,0.75f,1.0f,1.2f,1.5f,2.0f,3.0f,8.0f,-2.0f,-3.0f};
  static const float y[] = {-8.0f,-3.0f,-1.0f,-0.5f,0.0f,0.5f,1.0f,2.0f,3.0f,8.0f};
  unsigned exact=0,near=0,skipped=0,bad=0;
  for (unsigned i=0;i<sizeof(x)/sizeof(*x);i++) for(unsigned j=0;j<sizeof(y)/sizeof(*y);j++) {
    float a=gx8002_image_b_power_float_core_100100bc(x[i],y[j]);
    float b=powf(x[i],y[j]);
    if (isnan(a)&&isnan(b)) { skipped++; continue; }
    if(bits(a)==bits(b)) exact++;
    else if(isfinite(a)&&isfinite(b)&&fabsf(a-b)<=4.0e-6f*fmaxf(1.0f,fabsf(b))) near++;
    else { fprintf(stderr,"mismatch x=%g y=%g got=%08x want=%08x\n",x[i],y[j],bits(a),bits(b)); bad++; }
  }
  printf("host sanity exact=%u near=%u nan=%u bad=%u\n",exact,near,skipped,bad);
  return bad!=0;
}
