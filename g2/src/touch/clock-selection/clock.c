/* Independent locked ARM32 source-clock family61f0..6462 and5d70.
 * SDK6.10 provides semantic labels; compiled stock branches govern behavior. */
#include "clock.h"
static uint8_t *ptr(const uint8_t *c,unsigned n){return *(uint8_t *const *)(c+n);}
static uint16_t u16(const uint8_t *c,unsigned n){return *(const uint16_t *)(c+n);}
static uint32_t shr(uint32_t x,uint32_t n){n&=255u;return n>=32?0:x>>n;}
static uint32_t shl(uint32_t x,uint32_t n){n&=255u;return n>=32?0:x<<n;}
uint32_t touch_poly_period(uint32_t p){uint32_t size=65535u,mask=32768u;while(size>1 && !(p&mask)){size>>=1;mask>>=1;}return size;}
uint32_t touch_dither_value(uint32_t bits,uint32_t scale){return shl(1,(bits&3u)+scale+1u);}
uint32_t touch_dither_limit(uint32_t div,uint32_t min,uint32_t percent,uint32_t scale){uint32_t a=shr((div*percent)/100u,scale),b=shr(div-min,scale);return a>b?b:a;}
uint32_t touch_ssc_run(uint32_t mode,uint32_t dither,uint32_t limit,uint32_t period,uint32_t conversions){
 uint32_t src=dither<=limit?1u:0u;
 if(mode!=2){if(conversions<period)src=0;if(mode==0 && conversions%period)src=0;}
 return src;
}
uint32_t touch_prs_auto(const uint8_t *runtime,const uint8_t *c){const uint8_t *i=ptr(c,8);uint32_t total=u16(runtime,44)+i[77];return(total>=((touch_poly_period(u16(i,60))+1u)>>2)?2u:0u)|8u;}
uint32_t touch_ssc_auto(const uint8_t *w,const uint8_t *c){
 const uint8_t *runtime=ptr(w,0),*i=ptr(c,8);uint32_t total=u16(runtime,44)+i[77];if(total>=65536u)total=65535u;
 uint32_t minimum=(w[122]==1 || w[122]==10)?8u:4u;
 uint32_t limit=touch_dither_limit(u16(runtime,14),minimum,w[135],i[78]);
 return touch_ssc_run(w[136],touch_dither_value(runtime[56]&~128u,i[78]),limit,touch_poly_period(u16(i,60)),total)|4u;
}
uint32_t touch_lfsr_auto(const uint8_t *w,const uint8_t *c){
 const uint8_t *runtime=ptr(w,0),*i=ptr(c,8);uint32_t minimum=(w[122]==1 || w[122]==10)?8u:0u;
 uint32_t limit=touch_dither_limit(u16(runtime,14),minimum,w[135],i[78]);
 return (limit>15?3u:limit>7?2u:limit>3?1u:0u)|128u;
}
uint32_t touch_initialize_source_clock(uint8_t *c){
 uint8_t *w=ptr(c,12);uint32_t status=0,minimum=0;
 for(unsigned j=0;j<3;j++,w+=144){
  uint8_t *runtime=ptr(w,0);uint32_t original=runtime[33],ssc_auto=original&4u;
  if(ssc_auto || (original&3u)==1){if(runtime[56]&128u)runtime[56]=(uint8_t)touch_lfsr_auto(w,c);if(ssc_auto)runtime[33]=(uint8_t)touch_ssc_auto(w,c);}
  else if(original&8u)runtime[33]=(uint8_t)touch_prs_auto(runtime,c);
  if(w[122]==1 || w[122]==10)minimum=8u;else status=1u;
  /* Original source byte is retained for this test after automatic update. */
  if((original&3u)==1)minimum+=touch_dither_value(runtime[56]&~128u,ptr(c,8)[78]);
  if(u16(runtime,14)<minimum || u16(runtime,14)>4096u){status=0x800u;break;}
 }
 return status;
}
uint32_t touch_timer_cycles(uint32_t interval,const uint8_t *c){
 uint32_t value=(interval * *(const uint32_t *)(ptr(c,8)+44))>>14;
 if(value)value--;return value>=65536u?65535u:value;
}
