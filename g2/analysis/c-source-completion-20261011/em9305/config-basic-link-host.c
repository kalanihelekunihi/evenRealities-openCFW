#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static const uint8_t opencfw_em9305_config_phy_values_33449d[7]={2,1,3,1,1,1,4};
static uint32_t opencfw_em9305_radio_phy_project_3183d4(uint32_t v){return v&2?2:v&1?1:v&4;}
static uint32_t opencfw_em9305_config_limit_mpyuw(uint32_t v,uint32_t n){return (v&65535)*n;}
static uint32_t opencfw_em9305_config_link_mpywhul(uint32_t a,uint32_t b){return a*(b&65535);}
static uint32_t opencfw_em9305_config_update_mpywhl(uint32_t a,uint32_t b){return (uint32_t)((int64_t)(int32_t)a*(int16_t)b);}
static uint32_t opencfw_em9305_config_round_mpyuw(uint32_t a,uint32_t b){return (a&65535)*(b&65535);}
static uint32_t opencfw_em9305_config_link_divu_prior(uint32_t a,uint32_t b,uint32_t p){return b?a/b:p;}
static uint32_t opencfw_em9305_config_link_interval_326f2a(uint32_t v){uint32_t q=(uint32_t)(((uint64_t)v*0x1a36e3)>>31);return q+(1250*q<v);}
static uint32_t opencfw_em9305_radio_unsigned_divide_30c3a4(uint32_t a,uint32_t b){return b?a/b:0;}
static uint32_t opencfw_em9305_radio_record_timing_30c40c(uint32_t a,uint32_t b){return b?(a+b-1)/b:0;}
static uint32_t opencfw_em9305_config_basic_rounding_317efc(uint32_t a,uint32_t b,uint32_t c){uint32_t d=((a*(c-1))&255)+1,n=(a*(b+1))&255;if(d==256)d=1;return (n+d-1)/d;}
static inline uint32_t opencfw_em9305_config_link_has_remainder(uint32_t a,uint32_t b)
{return b?a%b!=0u:1u;}
static uint32_t opencfw_em9305_config_link_policy_quotient(uintptr_t input,uintptr_t link,uint32_t off)
{return opencfw_em9305_radio_unsigned_divide_30c3a4(opencfw_em9305_config_limit_mpyuw(*(volatile uint16_t *)(input+off),1000u),opencfw_em9305_config_limit_mpyuw(*(volatile uint16_t *)(link+500u),1250u));}
static uint32_t opencfw_em9305_config_link_cap46(void)
{uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;return *(volatile uint16_t *)(config+46u);}
static uint32_t opencfw_em9305_config_link_cap56(void)
{uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;return *(volatile uint8_t *)(config+56u);}
static uint32_t opencfw_em9305_config_link_phy(uint32_t value)
{uint32_t i=opencfw_em9305_radio_phy_project_3183d4(value)-2u;return (uint8_t)i<7u?opencfw_em9305_config_phy_values_33449d[(int8_t)i]:1u;}
/* Native326ed8..3272d8: complete basic link projection and distinct flagged/unflagged arithmetic paths. */
void opencfw_em9305_config_link_update_326ed8(uintptr_t link,uintptr_t input,uintptr_t row)
{
 *(volatile uint8_t *)(link+12u)=*(volatile uint8_t *)row;
 *(volatile uint16_t *)(link+482u)=*(volatile uint16_t *)(input+12u);
 uint32_t first_time=*(volatile uint32_t *)(input+4u),mode=*(volatile uint8_t *)(input+14u);
 *(volatile uint8_t *)(link+484u)=(uint8_t)mode;
 if(first_time<=1250u){first_time=1250u;*(volatile uint32_t *)(input+4u)=first_time;}
 uint32_t second_time=*(volatile uint32_t *)(input+8u);
 if(second_time<=1250u){second_time=1250u;*(volatile uint32_t *)(input+8u)=second_time;}
 uint32_t minimum=first_time<second_time?first_time:second_time;
 uint32_t maximum=minimum>5000u?minimum:5000u;
 uint32_t interval=opencfw_em9305_config_link_interval_326f2a(maximum);
 *(volatile uint16_t *)(link+500u)=(uint16_t)interval;
 if(mode==0u){uint32_t period=opencfw_em9305_config_link_mpywhul(1250u,interval);
  if(opencfw_em9305_config_link_has_remainder(minimum,period)){mode=1u;*(volatile uint8_t *)(link+484u)=1u;}
 }
 uint32_t first_length=*(volatile uint16_t *)(row+2u);
 *(volatile uint32_t *)(link+496u)=second_time;*(volatile uint32_t *)(link+492u)=first_time;
 if(mode){uint32_t a=0u,b=0u;
  if(first_length){uint32_t cap=opencfw_em9305_config_link_cap46();a=first_length+5u;if(a>cap)a=cap;}
  *(volatile uint16_t *)(link+448u)=(uint16_t)a;
  uint32_t second_length=*(volatile uint16_t *)(row+4u);
  if(second_length){uint32_t cap=opencfw_em9305_config_link_cap46();b=second_length+5u;if(b>cap)b=cap;}
  uint32_t phy=*(volatile uint8_t *)(row+6u);
  *(volatile uint16_t *)(link+488u)=(uint16_t)second_length;*(volatile uint16_t *)(link+444u)=(uint16_t)b;
  *(volatile uint16_t *)(link+486u)=(uint16_t)first_length;
  uint32_t first_phy=opencfw_em9305_config_link_phy(phy),second_phy=*(volatile uint8_t *)(row+7u);
  *(volatile uint8_t *)(link+480u)=(uint8_t)first_phy;
  *(volatile uint8_t *)(link+481u)=(uint8_t)opencfw_em9305_config_link_phy(second_phy);
 }else{uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
  uint32_t second_length=*(volatile uint16_t *)(row+4u);
  *(volatile uint16_t *)(link+486u)=(uint16_t)first_length;
  uint32_t cap=*(volatile uint16_t *)(config+46u),phy=*(volatile uint8_t *)(row+6u);
  *(volatile uint16_t *)(link+488u)=(uint16_t)second_length;
  *(volatile uint16_t *)(link+448u)=(uint16_t)(first_length<cap?first_length:cap);
  *(volatile uint16_t *)(link+444u)=(uint16_t)(second_length<cap?second_length:cap);
  uint32_t first_phy=opencfw_em9305_config_link_phy(phy),second_phy=*(volatile uint8_t *)(row+7u);
  *(volatile uint8_t *)(link+480u)=(uint8_t)first_phy;
  *(volatile uint8_t *)(link+481u)=(uint8_t)opencfw_em9305_config_link_phy(second_phy);
 }
 uint32_t cap=opencfw_em9305_config_link_cap56();
 uint32_t limit_a=opencfw_em9305_config_link_policy_quotient(input,link,16u);
 uint32_t cap_b;
 if(cap>=limit_a){limit_a=opencfw_em9305_config_link_policy_quotient(input,link,16u);cap_b=opencfw_em9305_config_link_cap56();}
 else{cap_b=opencfw_em9305_config_link_cap56();limit_a=cap_b;}
 uint32_t first_budget=opencfw_em9305_config_limit_mpyuw(*(volatile uint16_t *)(input+18u),1000u);
 uint32_t period=opencfw_em9305_config_limit_mpyuw(*(volatile uint16_t *)(link+500u),1250u);
 *(volatile uint8_t *)(link+502u)=(uint8_t)limit_a;
 uint32_t limit_b=opencfw_em9305_radio_unsigned_divide_30c3a4(first_budget,period);
 if(cap_b>=limit_b)limit_b=opencfw_em9305_config_link_policy_quotient(input,link,18u);
 else limit_b=opencfw_em9305_config_link_cap56();
 *(volatile uint8_t *)(link+503u)=(uint8_t)limit_b;
 if(mode){
  uint32_t len_a=*(volatile uint16_t *)(row+2u),den_a=1u,den_b=1u,prior;
  if(len_a){uint32_t c=opencfw_em9305_config_link_cap46();den_a=*(volatile uint16_t *)(link+486u)+5u;if(den_a>c)den_a=c;den_a&=255u;}
  uint32_t len_b=*(volatile uint16_t *)(row+4u);
  prior=len_b;
  if(len_b){uint32_t c=opencfw_em9305_config_link_cap46();prior=*(volatile uint16_t *)(link+488u)+5u;den_b=prior<c?prior:c;den_b&=255u;}
  uint32_t stored_a=*(volatile uint16_t *)(link+486u),q_a=0u,reproduced=den_a;
  if(stored_a){q_a=opencfw_em9305_config_link_divu_prior(stored_a,den_a,prior);reproduced=opencfw_em9305_config_update_mpywhl(q_a,den_a);if(reproduced<stored_a)++q_a;}
  *(volatile uint8_t *)(link+512u)=(uint8_t)q_a;
  uint32_t stored_b=*(volatile uint16_t *)(link+488u),q_b=0u;
  if(stored_b){q_b=opencfw_em9305_config_link_divu_prior(stored_b,den_b,reproduced);uint32_t product=opencfw_em9305_config_update_mpywhl(q_b,den_b);if(product<stored_b)++q_b;}
  *(volatile uint8_t *)(link+513u)=(uint8_t)q_b;
  uint32_t row_b=*(volatile uint8_t *)(row+9u),row_a=*(volatile uint8_t *)(row+8u);
  uint32_t fresh_limit=*(volatile uint8_t *)(link+502u);
  uint32_t rounded=opencfw_em9305_config_basic_rounding_317efc((q_a&255u)>(q_b&255u)?q_a&255u:q_b&255u,row_a>row_b?row_a:row_b,fresh_limit>(limit_b&255u)?fresh_limit:limit_b&255u);
  uint32_t fresh_interval=*(volatile uint16_t *)(link+500u),fresh_time=*(volatile uint32_t *)(input+4u);
  uint32_t large=opencfw_em9305_config_link_mpywhul(0xbec102u,fresh_interval);
  uint32_t scaled=opencfw_em9305_config_update_mpywhl(fresh_time,10000u);
  uint32_t small=opencfw_em9305_config_link_mpywhul(large,len_a);
  uint32_t round_first=(q_a&255u)>(q_b&255u)?q_a&255u:q_b&255u;
  uint32_t round_second=row_a>row_b?row_a:row_b;
  uint32_t round_numerator=opencfw_em9305_config_round_mpyuw(round_first,round_second+1u)&255u;
  uint32_t large_q=opencfw_em9305_config_link_divu_prior(large,scaled,row_b),small_q=opencfw_em9305_config_link_divu_prior(small,scaled,round_numerator);
  *(volatile uint8_t *)(link+504u)=(uint8_t)rounded;
  large_q+=large!=large_q*scaled;small_q+=small!=small_q*scaled;
  uint32_t size_a=opencfw_em9305_radio_record_timing_30c40c(large_q*5u+small_q,q_a&255u);
  fresh_time=*(volatile uint32_t *)(input+8u);len_b=*(volatile uint16_t *)(row+4u);
  scaled=opencfw_em9305_config_update_mpywhl(fresh_time,10000u);
  small=opencfw_em9305_config_link_mpywhul(large,len_b);
  large_q=opencfw_em9305_config_link_divu_prior(large,scaled,small_q);small_q=opencfw_em9305_config_link_divu_prior(small,scaled,len_b);
  large_q+=large!=large_q*scaled;small_q+=small!=small_q*scaled;
  uint32_t size_b=opencfw_em9305_radio_record_timing_30c40c(large_q*5u+small_q,*(volatile uint8_t *)(link+513u));
  uint32_t a=0u,b=0u;
  if(*(volatile uint16_t *)(row+2u)){uint32_t c=opencfw_em9305_config_link_cap46();a=size_a+2u;if(a>c)a=c;}
  *(volatile uint16_t *)(link+448u)=(uint16_t)a;
  if(*(volatile uint16_t *)(row+4u)){uint32_t c=opencfw_em9305_config_link_cap46();b=size_b+2u;if(b>c)b=c;}
  *(volatile uint16_t *)(link+444u)=(uint16_t)b;
 }else{
  uint32_t den_a=*(volatile uint16_t *)(link+448u),q_a=0u;
  if(den_a){uint32_t n=*(volatile uint16_t *)(link+486u);q_a=opencfw_em9305_config_link_divu_prior(n,den_a,(uint32_t)input);uint32_t product=opencfw_em9305_config_link_mpywhul(q_a,den_a);if((int32_t)product<(int32_t)n)++q_a;}
  *(volatile uint8_t *)(link+512u)=(uint8_t)q_a;
  uint32_t den_b=*(volatile uint16_t *)(link+444u),q_b=0u;
  if(den_b){uint32_t n=*(volatile uint16_t *)(link+488u);q_b=opencfw_em9305_config_link_divu_prior(n,den_b,0u);uint32_t product=opencfw_em9305_config_link_mpywhul(q_b,den_b);if((int32_t)product<(int32_t)n)++q_b;}
  *(volatile uint8_t *)(link+513u)=(uint8_t)q_b;
  uint32_t row_b=*(volatile uint8_t *)(row+9u),row_a=*(volatile uint8_t *)(row+8u),fresh_limit=*(volatile uint8_t *)(link+502u);
  *(volatile uint8_t *)(link+504u)=(uint8_t)opencfw_em9305_config_basic_rounding_317efc((q_a&255u)>(q_b&255u)?q_a&255u:q_b&255u,row_a>row_b?row_a:row_b,fresh_limit<(limit_b&255u)?fresh_limit:limit_b&255u);
 }
}

static unsigned char ex[656];static void h(unsigned o,unsigned v){uint16_t x=v;memcpy(ex+o,&x,2);}static void w(unsigned o,uint32_t v){memcpy(ex+o,&v,4);}static unsigned ceiling(unsigned a,unsigned b){return b?a/b+(a%b!=0):0;}
int main(void){if(mmap((void*)0x800000,0x40000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;unsigned cases=0;
for(unsigned a=0;a<256;++a)for(unsigned b=0;b<256;++b)for(unsigned mode=0;mode<3;++mode){memset((void*)0x810000,0xa5,656);memset((void*)0x811000,0,32);memset((void*)0x812000,0,10);memset((void*)0x813000,0,64);*(uint32_t*)0x805cac=0x813000;*(uint16_t*)0x81302e=123;*(uint8_t*)0x813038=15;*(uint16_t*)0x81100c=0xfedc;*(uint32_t*)0x811004=5000;*(uint32_t*)0x811008=5000;*(uint8_t*)0x81100e=mode;*(uint16_t*)0x811010=4000;*(uint16_t*)0x811012=3000;*(uint8_t*)0x812000=239;*(uint16_t*)0x812002=a;*(uint16_t*)0x812004=b;*(uint8_t*)0x812006=1;*(uint8_t*)0x812007=2;*(uint8_t*)0x812008=3;*(uint8_t*)0x812009=7;memcpy(ex,(void*)0x810000,656);
ex[12]=239;h(482,0xfedc);ex[484]=mode;h(500,4);w(492,5000);w(496,5000);h(486,a);h(488,b);ex[480]=1;ex[481]=2;ex[502]=15;ex[503]=15;
unsigned da=mode?(a?((a+5)<123?a+5:123)&255:1):a<123?a:123,db=mode?(b?((b+5)<123?b+5:123)&255:1):b<123?b:123;unsigned qa=ceiling(a,da),qb=ceiling(b,db);ex[512]=qa;ex[513]=qb;ex[504]=opencfw_em9305_config_basic_rounding_317efc(qa>qb?qa:qb,7,15);
if(mode){uint32_t large=0xbec102u*4,small_a=large*a,small_b=large*b,den=5000*10000;uint32_t ca=ceiling(large,den)*5+ceiling(small_a,den),cb=ceiling(large,den)*5+ceiling(small_b,den);unsigned pa=a?ceiling(ca,qa)+2:0,pb=b?ceiling(cb,qb)+2:0;h(448,pa<123?pa:123);h(444,pb<123?pb:123);}else{h(448,da);h(444,db);}
opencfw_em9305_config_link_update_326ed8(0x810000,0x811000,0x812000);if(memcmp(ex,(void*)0x810000,656)){printf("FAIL %u %u %u\n",a,b,mode);return 3;}++cases;}
printf("PASS %u\n",cases);}
