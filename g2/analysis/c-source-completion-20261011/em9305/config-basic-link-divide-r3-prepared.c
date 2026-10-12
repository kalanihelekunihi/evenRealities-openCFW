/* Native 30c40c tail enters 30c3a4. Capture authentic R3 for the
 * later DIVU destination-preservation path at 3271be. Not an ABI return. */
static uint32_t opencfw_em9305_config_link_timing_r3(uint32_t length,uint32_t unit,uint32_t prior)
{
 uint32_t n=length+unit-1u;
 if(n<unit)return prior;
 uint32_t high=0u,low=unit,mask=1u,r3;
 do {
  high=(high<<1)|(low>>31);low<<=1;
  r3=n>=low;
  mask<<=1;
  __asm__ volatile("" ::: "memory");
 }while(high==0u && r3);
 if(mask==0u)return r3;
 for(;;){
  r3=high>>1;
  uint32_t old_mask=mask;
  high=r3;mask>>=1;
  if(old_mask<=3u)return r3;
 }
}
