/* Native3099cc..309aa2: keep incidental native R0, fresh count reads and
 * each feature pair store. Provider presence is runtime, never assumed. */
uint32_t opencfw_em9305_init_features_3099cc(uint32_t incoming)
{
 (void)incoming;
 uint32_t r0=*(volatile uint32_t *)(uintptr_t)0x802960u;
 uint32_t second=*(volatile uint32_t *)(uintptr_t)0x802958u;
 uint32_t flags=3u,missing=(r0==0u)||(second==0u);
 uint32_t first=*(volatile uint32_t *)(uintptr_t)0x802954u;
 uint32_t third=*(volatile uint32_t *)(uintptr_t)0x80295cu;
 uint32_t high=0u;
 if(r0==0u)flags=0u;
 if(!missing)flags|=0xc0003300u;
 *(volatile uint32_t *)(uintptr_t)0x805b48u=flags;
 *(volatile uint32_t *)(uintptr_t)0x805b4cu=high;
 if(r0!=0u&&first!=0u){
  uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
  flags|=0x2000008cu;
  *(volatile uint32_t *)(uintptr_t)0x805b4cu=high;
  r0=*(volatile uint8_t *)(config+34u);
  *(volatile uint32_t *)(uintptr_t)0x805b48u=flags;
  if(r0>=2u){high|=448u;*(volatile uint32_t *)(uintptr_t)0x805b48u=flags;*(volatile uint32_t *)(uintptr_t)0x805b4cu=high;}
 }
 if(second!=0u){
  r0=flags|0x30u;
  *(volatile uint32_t *)(uintptr_t)0x805b4cu=high;
  *(volatile uint32_t *)(uintptr_t)0x805b48u=r0;
  if(first==0u)return r0;
  uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
  *(volatile uint32_t *)(uintptr_t)0x805b4cu=high;
  uint32_t count=*(volatile uint8_t *)(config+34u);
  r0=flags|0x0f000070u;
  *(volatile uint32_t *)(uintptr_t)0x805b48u=r0;
  if(count>=2u){r0=flags|0x1f000070u;*(volatile uint32_t *)(uintptr_t)0x805b4cu=high;*(volatile uint32_t *)(uintptr_t)0x805b48u=r0;}
  flags=r0;
  if(third!=0u){flags=r0|0x00c00000u;*(volatile uint32_t *)(uintptr_t)0x805b4cu=high;*(volatile uint32_t *)(uintptr_t)0x805b48u=flags;}
 }
 r0=first==0u;
 if(missing||r0!=0u)return r0;
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 *(volatile uint32_t *)(uintptr_t)0x805b4cu=high;
 uint32_t count=*(volatile uint8_t *)(config+34u);
 r0=flags|0x003fcc00u;
 *(volatile uint32_t *)(uintptr_t)0x805b48u=r0;
 if(count>=2u){high|=575u;*(volatile uint32_t *)(uintptr_t)0x805b48u=r0;*(volatile uint32_t *)(uintptr_t)0x805b4cu=high;}
 return r0;
}
/* Native308ff8..30902c: independent fresh publication reads, BMSKN27
 * tests bits28..31; preserve incoming R0 when no branch rewrites it. */
uint32_t opencfw_em9305_init_features_308ff8(uint32_t incoming)
{
 uint32_t r0=incoming,flags=*(volatile uint32_t *)(uintptr_t)0x805b34u;
 if((flags&(1u<<8u))!=0u){r0=*(volatile uint32_t *)(uintptr_t)0x805b54u;r0|=1u<<9u;*(volatile uint32_t *)(uintptr_t)0x805b54u=r0;}
 if((flags&(1u<<14u))!=0u){r0=*(volatile uint32_t *)(uintptr_t)0x805b54u;r0|=1u<<15u;*(volatile uint32_t *)(uintptr_t)0x805b54u=r0;}
 uint32_t first=*(volatile uint32_t *)(uintptr_t)0x805b30u;
 if((flags&(1u<<5u))!=0u){r0=*(volatile uint32_t *)(uintptr_t)0x805b54u;r0|=1u<<6u;*(volatile uint32_t *)(uintptr_t)0x805b54u=r0;}
 if((first&0xf0000000u)!=0u){r0=*(volatile uint32_t *)(uintptr_t)0x805b54u;r0|=1u;*(volatile uint32_t *)(uintptr_t)0x805b54u=r0;}
 return r0;
}
