/* Stock 0x35508: nearest charger ladder and register-one update. */
#include <stdint.h>
extern float r1_native_compare_absf(float);
extern uint32_t r1_yhm_register_read_native(uint32_t,uint32_t,uint8_t *);
extern uint32_t r1_yhm_register_write_native(uint32_t,uint32_t,const uint8_t *);
const float r1_yhm_ladder_multipliers[8] __attribute__((section(".r1.yhm.ladder.table")))={0.5f,0.2f,0.7f,0.9f,1.0f,1.5f,2.0f,3.0f};
uint32_t r1_yhm_ladder_native(float target)
{
 /* A non-writing provider has a defined zero low-bit fallback. */
 uint8_t scratch=0;
 const float scale=20.080322265625f;
 uint32_t selected=0;
 float best=r1_native_compare_absf(target-scale*0.5f);
 for (uint32_t index=1;index<8;index++) {
  volatile float scaled=scale*((const volatile float *)r1_yhm_ladder_multipliers)[index];
  float candidate=r1_native_compare_absf(target-scaled);
  if (candidate<best) {best=candidate;selected=index;}
 }
 (void)r1_yhm_register_read_native(1,1,&scratch);
 scratch=(uint8_t)((scratch&0x1fu)|(selected<<5));
 (void)r1_yhm_register_write_native(1,1,&scratch);
 return selected;
}
uint32_t r1_native_charger_ladder_set(float target) { return r1_yhm_ladder_native(target); }
