#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned limit_calls;
uintptr_t opencfw_em9305_config_link_find_31abc0(uint32_t id,uint32_t slot){if(id!=7||slot>=16)__builtin_trap();return 0x820000u+slot*656u;}
static uint32_t opencfw_em9305_config_basic_stride(uint32_t i){return i*10u;}
static uint32_t opencfw_em9305_config_update_mpywhl(uint32_t a,uint32_t b){return (uint32_t)((int64_t)(int32_t)a*(int16_t)b);}
uint32_t opencfw_em9305_config_channel_ready_3186a0(uintptr_t c){if(c!=0x813000)__builtin_trap();return 0x123;}
uint32_t opencfw_em9305_config_basic_limit_31855c(uintptr_t link,uintptr_t input,uint32_t selector){if(input!=0x810000)__builtin_trap();if(selector){if(link<0x820000||link>=0x823000)__builtin_trap();}else if(link!=1)__builtin_trap();++limit_calls;return 1;}
/* Native3185e8..318670: two PHY contributions, feature reads remain separately live. */
uint32_t opencfw_em9305_config_link_time_3185e8(uint32_t first_phy,uint32_t second_phy,uint32_t first_length,uint32_t second_length)
{
 uint32_t sum=0u;
 if(first_phy==1u)sum=(first_length<<3u)+112u;
 else if(first_phy==2u)sum=60u+(first_length<<2u);
 else if(first_phy==3u){uint32_t n=first_length+4u;
  sum=(*(volatile uint8_t *)(uintptr_t)0x805a86u&16u)?(n<<4u)+462u:(n<<6u)+720u;
 }
 sum+=150u;
 if(second_phy==1u)sum+=(second_length<<3u)+112u;
 else if(second_phy==2u)sum+=(second_length<<2u)+60u;
 else if(second_phy==3u){uint32_t n=second_length+4u;
  sum+=(*(volatile uint8_t *)(uintptr_t)0x805a86u&16u)?(n<<4u)+462u:(n<<6u)+720u;
 }
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 return sum+*(volatile uint16_t *)(config+54u)+150u;
}
/* Native318670..31869e: early second-slot gate, equality and first empty attachment. R1 preserved by native routine. */
uint32_t opencfw_em9305_config_attach_link_318670(uintptr_t channel,uintptr_t link)
{
 if(*(volatile uint32_t *)(channel+92u))return 0u;
 for(uint32_t i=0u;i<2u;++i){uintptr_t cell=channel+88u+i*4u;uint32_t value=*(volatile uint32_t *)cell;
  if(value==(uint32_t)link)return 1u;
  if(value==0u){*(volatile uint32_t *)cell=(uint32_t)link;return 1u;}
 }
 return 0u;
}
/* Native3185a8..3185e8: captured count/id/row base and full timing sum. */
uint32_t opencfw_em9305_config_basic_link_sum_3185a8(uintptr_t input)
{
 uint32_t count=*(volatile uint8_t *)(input+20u),total=0u;
 if(count){uintptr_t rows=*(volatile uint32_t *)(input+24u);uint32_t id=*(volatile uint8_t *)input;
  for(uint32_t i=0u;i<count;++i){uintptr_t link=opencfw_em9305_config_link_find_31abc0(id,*(volatile uint8_t *)(rows+i*10u));
   uint32_t first_length=*(volatile uint8_t *)(link+448u);
   uint32_t second=*(volatile uint8_t *)(link+481u);
   uint32_t first=*(volatile uint8_t *)(link+480u);
   uint32_t second_length=*(volatile uint8_t *)(link+444u);
   total+=opencfw_em9305_config_link_time_3185e8(first,second,first_length,second_length);
  }
 }
 return total;
}
static inline uint32_t opencfw_em9305_config_round_mpyw(uint32_t a,uint32_t b)
{return (uint32_t)((int32_t)(int16_t)a*(int32_t)(int16_t)b);}
static inline uint32_t opencfw_em9305_config_round_mpyuw(uint32_t a,uint32_t b)
{return (a&65535u)*(b&65535u);}
/* Native317efc..317f2c: byte-wrapped numerator/divisor and ceiling quotient. */
uint32_t opencfw_em9305_config_basic_rounding_317efc(uint32_t first,uint32_t second,uint32_t third)
{
 uint32_t product=opencfw_em9305_config_round_mpyw(third-1u,first);
 uint32_t numerator=opencfw_em9305_config_round_mpyuw(first,second+1u)&255u;
 uint32_t divisor=(product&255u)+1u;
 uint32_t raw_divisor=divisor;
 if((divisor&255u)!=divisor)divisor=1u;
 divisor&=255u;
 uint32_t quotient=numerator/divisor;
 uint32_t reproduced=quotient;
 if(raw_divisor==divisor)reproduced=opencfw_em9305_config_update_mpywhl(quotient,raw_divisor);
 reproduced&=255u;
 return (quotient+(numerator!=reproduced))&255u;
}
static inline uint32_t opencfw_em9305_config_update_macwhl(uint32_t prior,uint32_t a,uint32_t b)
{return prior+(uint32_t)((int64_t)(int32_t)a*(int16_t)b);}
/* Native326b00..326d0c: full attachment/timing, two-slot schedule, limits and fixed-point retry. */
uint32_t opencfw_em9305_config_channel_update_326b00(uintptr_t channel,uintptr_t input)
{
 uint32_t count,offset=0u,index=0u;
 for(;;){count=*(volatile uint8_t *)(input+20u);if(index>=count)break;
  uintptr_t rows=*(volatile uint32_t *)(input+24u);uint32_t id=*(volatile uint8_t *)input;
  uintptr_t link=opencfw_em9305_config_link_find_31abc0(id,*(volatile uint8_t *)(rows+offset));
  (void)opencfw_em9305_config_attach_link_318670(channel,link);
  if(*(volatile uint8_t *)(input+13u)==1u){
   *(volatile uint32_t *)(link+508u)=opencfw_em9305_config_basic_link_sum_3185a8(input);
   uint32_t second_length=*(volatile uint8_t *)(link+444u),second=*(volatile uint8_t *)(link+481u);
   uint32_t first_length=*(volatile uint8_t *)(link+448u),first=*(volatile uint8_t *)(link+480u);
   *(volatile uint32_t *)(link+408u)=opencfw_em9305_config_link_time_3185e8(first,second,first_length,second_length);
  }else{uint32_t second_length=*(volatile uint8_t *)(link+444u),second=*(volatile uint8_t *)(link+481u);
   uint32_t first_length=*(volatile uint8_t *)(link+448u),first=*(volatile uint8_t *)(link+480u);
   uint32_t time=opencfw_em9305_config_link_time_3185e8(first,second,first_length,second_length);
   *(volatile uint32_t *)(link+508u)=time;*(volatile uint32_t *)(link+408u)=time;
  }
  offset+=10u;++index;
 }
 for(;;){uint32_t changed=0u;uintptr_t first_link=*(volatile uint32_t *)(channel+88u);
  if(*(volatile uint8_t *)(input+13u)==1u){
   uint32_t t=*(volatile uint32_t *)(first_link+508u),multiplier=*(volatile uint8_t *)(first_link+504u);
   uint32_t interval=*(volatile uint16_t *)(first_link+500u);
   uint32_t baseline=opencfw_em9305_config_update_mpywhl(t,multiplier);
   *(volatile uint16_t *)(channel+20u)=(uint16_t)interval;
   *(volatile uint32_t *)(first_link+20u)=baseline;*(volatile uint32_t *)(first_link+16u)=baseline;
   *(volatile uint32_t *)(channel+12u)=baseline;
   for(uint32_t i=1u;i<count;++i){uintptr_t rows=*(volatile uint32_t *)(input+24u);uint32_t id=*(volatile uint8_t *)input;
    uintptr_t link=opencfw_em9305_config_link_find_31abc0(id,*(volatile uint8_t *)(rows+opencfw_em9305_config_basic_stride(i)));
    uint32_t sum=0u,pos=0u;
    for(uint32_t j=0u;j<i;++j){rows=*(volatile uint32_t *)(input+24u);id=*(volatile uint8_t *)input;
     uintptr_t other=opencfw_em9305_config_link_find_31abc0(id,*(volatile uint8_t *)(rows+pos));
     uint32_t first_length=*(volatile uint8_t *)(other+448u),second=*(volatile uint8_t *)(other+481u);
     uint32_t first=*(volatile uint8_t *)(other+480u),second_length=*(volatile uint8_t *)(other+444u);
     sum+=opencfw_em9305_config_link_time_3185e8(first,second,first_length,second_length);pos+=10u;
    }
    uint32_t baseline_now=*(volatile uint32_t *)(first_link+16u);count=*(volatile uint8_t *)(input+20u);
    *(volatile uint32_t *)(link+16u)=baseline_now-sum;
    *(volatile uint32_t *)(link+20u)=*(volatile uint32_t *)(first_link+16u);
   }
  }else{uint32_t sum=0u;uintptr_t link=first_link;
   for(;;){uint32_t time=*(volatile uint32_t *)(link+508u),multiplier=*(volatile uint8_t *)(link+504u);
    sum=opencfw_em9305_config_update_macwhl(sum,time,multiplier);
    if(link!=first_link)break;
    link=*(volatile uint32_t *)(channel+92u);if(!link)break;
   }
   link=first_link;
   for(;;){*(volatile uint32_t *)(link+16u)=sum;
    uint32_t baseline=*(volatile uint32_t *)(first_link+16u);*(volatile uint32_t *)(link+20u)=baseline;
    if(link!=first_link)break;
    link=*(volatile uint32_t *)(channel+92u);if(!link)break;
   }
   uint32_t baseline=*(volatile uint32_t *)(first_link+16u),interval=*(volatile uint16_t *)(first_link+500u);
   *(volatile uint32_t *)(channel+12u)=baseline;*(volatile uint16_t *)(channel+20u)=(uint16_t)interval;
  }
  if(!count)break;
  uint32_t i=0u,pos=0u;
  do{uintptr_t rows=*(volatile uint32_t *)(input+24u);uint32_t id=*(volatile uint8_t *)input;
   uintptr_t link=opencfw_em9305_config_link_find_31abc0(id,*(volatile uint8_t *)(rows+pos));
   uint32_t a=*(volatile uint8_t *)(link+502u);
   uint32_t first_limit=opencfw_em9305_config_basic_limit_31855c(link,input,1u);
   uint32_t b=*(volatile uint8_t *)(link+503u);if(a>first_limit)a=first_limit;
   /* Exact native R7 captures first limit return, and becomes second call R0. */
   uint32_t second_limit=opencfw_em9305_config_basic_limit_31855c((uintptr_t)first_limit,input,0u);
   *(volatile uint8_t *)(link+502u)=(uint8_t)a;
   if(b>second_limit)b=second_limit;*(volatile uint8_t *)(link+503u)=(uint8_t)b;
   if(a==0u||b==0u)goto finish;
   count=*(volatile uint8_t *)(input+20u);++i;pos+=10u;
  }while(i<count);
  if(!count)break;
  uintptr_t rows=*(volatile uint32_t *)(input+24u);i=0u;
  do{uint32_t offset_now=opencfw_em9305_config_basic_stride(i),id=*(volatile uint8_t *)input;
   uintptr_t link=opencfw_em9305_config_link_find_31abc0(id,*(volatile uint8_t *)(rows+offset_now));
   rows=*(volatile uint32_t *)(input+24u);uintptr_t row=rows+offset_now;
   uint32_t a=*(volatile uint8_t *)(link+512u),b=*(volatile uint8_t *)(link+513u);
   uint32_t limit_b=*(volatile uint8_t *)(link+503u),limit_a=*(volatile uint8_t *)(link+502u);
   uint32_t row_b=*(volatile uint8_t *)(row+9u),row_a=*(volatile uint8_t *)(row+8u);
   uint32_t rounded=opencfw_em9305_config_basic_rounding_317efc(a>b?a:b,row_a>row_b?row_a:row_b,limit_a<limit_b?limit_a:limit_b);
   if(*(volatile uint8_t *)(link+504u)!=rounded){changed=1u;*(volatile uint8_t *)(link+504u)=(uint8_t)rounded;}
   count=*(volatile uint8_t *)(input+20u);++i;
  }while(i<count);
  if(!changed)break;
 }
finish:
 *(volatile uint8_t *)(channel+2u)=*(volatile uint8_t *)(input+13u);
 uint32_t ready=opencfw_em9305_config_channel_ready_3186a0(channel);
 *(volatile uint8_t *)(channel+22u)=(uint8_t)ready;
 return ready;
}

static unsigned char exp_link[16][656],exp_ch[140];
static void w32(unsigned char *p,unsigned off,uint32_t v){memcpy(p+off,&v,4);}
int main(void){if(mmap((void*)0x800000,0x60000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;unsigned cases=0;
for(unsigned count=1;count<=16;++count)for(unsigned mode=0;mode<256;++mode)for(unsigned seed=0;seed<4;++seed){memset((void*)0x810000,0,0x40000);*(uint8_t*)0x810000=7;*(uint8_t*)0x810014=count;*(uint8_t*)0x81000d=mode;*(uint32_t*)0x810018=0x811000;*(uint32_t*)0x805cac=0x814000;*(uint16_t*)0x814036=seed*3971;*(uint8_t*)0x805a86=seed&1?16:0;limit_calls=0;
memset((void*)0x813000,0xa5,140);*(uint32_t*)0x813058=0;*(uint32_t*)0x81305c=0;memcpy(exp_ch,(void*)0x813000,140);uint32_t times[16],total=0;
for(unsigned i=0;i<16;++i){*(uint8_t*)(uintptr_t)(0x811000+i*10)=i;unsigned char *p=(void*)(uintptr_t)(0x820000+i*656);memset(p,0x5a,656);p[480]=1;p[481]=2;p[448]=seed*37+i;p[444]=seed*19+i;p[504]=seed+1;p[502]=31;p[503]=31;p[512]=1;p[513]=1;*(uint16_t*)(p+500)=seed*4000+i;memcpy(exp_link[i],p,656);times[i]=112+p[448]*8+60+p[444]*4+300+seed*3971;if(i<count)total+=times[i];}
w32(exp_ch,88,0x820000);if(count>1)w32(exp_ch,92,0x820000+656);
for(unsigned i=0;i<count;++i){w32(exp_link[i],408,times[i]);w32(exp_link[i],508,mode==1?total:times[i]);exp_link[i][502]=exp_link[i][503]=exp_link[i][504]=1;}
uint32_t baseline;if(mode==1){baseline=total;uint32_t prefix=0;for(unsigned i=0;i<count;++i){w32(exp_link[i],16,baseline-prefix);w32(exp_link[i],20,baseline);prefix+=times[i];}}
else{baseline=times[0]+(count>1?times[1]:0);for(unsigned i=0;i<(count>1?2:1);++i){w32(exp_link[i],16,baseline);w32(exp_link[i],20,baseline);}}
w32(exp_ch,12,baseline);memcpy(exp_ch+20,exp_link[0]+500,2);exp_ch[2]=mode;exp_ch[22]=0x23;
if(opencfw_em9305_config_channel_update_326b00(0x813000,0x810000)!=0x123)return 6;
if(memcmp(exp_ch,(void*)0x813000,140))return 3;for(unsigned i=0;i<16;++i)if(memcmp(exp_link[i],(void*)(uintptr_t)(0x820000+i*656),656))return 4;if(limit_calls!=2*count*(seed?2:1))return 5;++cases;}
printf("PASS %u\n",cases);}
