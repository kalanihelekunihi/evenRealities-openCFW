#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned calls,ready;
uintptr_t opencfw_em9305_config_link_find_31abc0(uint32_t id,uint32_t slot){if(id!=7||slot>=16)__builtin_trap();++calls;return 0x820000u+slot*656u;}
uint32_t opencfw_em9305_config_channel_ready_3186a0(uintptr_t channel){if(channel!=0x813000)__builtin_trap();return ready;}
static uint32_t opencfw_em9305_config_extended_stride(uint32_t i){return i*14u;}
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
extern uint32_t opencfw_em9305_config_channel_ready_3186a0(uintptr_t);
static inline uint32_t opencfw_em9305_config_update_mpywhl(uint32_t a,uint32_t b)
{return (uint32_t)((int64_t)(int32_t)a*(int16_t)b);}
static uint32_t opencfw_em9305_config_update_link_time(uintptr_t link)
{
 uint32_t second=*(volatile uint8_t *)(link+481u);
 uint32_t first_length=*(volatile uint8_t *)(link+448u);
 uint32_t first=*(volatile uint8_t *)(link+480u);
 uint32_t second_length=*(volatile uint8_t *)(link+444u);
 return opencfw_em9305_config_link_time_3185e8(first,second,first_length,second_length);
}
/* Native326d0c..326ed8: complete extended channel timing, attachment and suffix schedule update. */
void opencfw_em9305_config_extended_channel_update_326d0c(uintptr_t channel,uintptr_t input)
{
 uint32_t outer=0u,count,id;uintptr_t rows;
 for(;;){count=*(volatile uint8_t *)(input+19u);rows=*(volatile uint32_t *)(input+20u);id=*(volatile uint8_t *)input;
  if(outer>=count)break;
  uint32_t offset=opencfw_em9305_config_extended_stride(outer);
  uintptr_t link=opencfw_em9305_config_link_find_31abc0(id,*(volatile uint8_t *)(rows+offset));
  (void)opencfw_em9305_config_attach_link_318670(channel,link);
  uint32_t mode=*(volatile uint8_t *)(input+17u),total=0u;
  if(mode==1u){count=*(volatile uint8_t *)(input+19u);
   if(count){uint32_t i=0u,pos=0u;
    do{rows=*(volatile uint32_t *)(input+20u);id=*(volatile uint8_t *)input;
     uintptr_t other=opencfw_em9305_config_link_find_31abc0(id,*(volatile uint8_t *)(rows+pos));
     uint32_t t=opencfw_em9305_config_update_link_time(other);
     count=*(volatile uint8_t *)(input+19u);++i;total+=t;pos+=14u;
    }while(i<count);
   }
   *(volatile uint32_t *)(link+508u)=total;
   uint32_t t=opencfw_em9305_config_update_link_time(link);
   *(volatile uint32_t *)(link+408u)=t;
  }else{uint32_t t=opencfw_em9305_config_update_link_time(link);
   *(volatile uint32_t *)(link+508u)=t;
   *(volatile uint32_t *)(link+408u)=t;
  }
  ++outer;
 }
 uint32_t first_slot=*(volatile uint8_t *)rows;
 uint32_t mode=*(volatile uint8_t *)(input+17u);
 uintptr_t first_link=opencfw_em9305_config_link_find_31abc0(id,first_slot);
 if(mode==1u){uint32_t t=*(volatile uint32_t *)(first_link+508u);
  uint32_t multiplier=*(volatile uint8_t *)(first_link+504u);
  uint32_t interval=*(volatile uint16_t *)(first_link+500u);
  uint32_t baseline=opencfw_em9305_config_update_mpywhl(t,multiplier);
  *(volatile uint16_t *)(channel+20u)=(uint16_t)interval;
  *(volatile uint32_t *)(first_link+20u)=baseline;
  *(volatile uint32_t *)(first_link+16u)=baseline;
  *(volatile uint32_t *)(channel+12u)=baseline;
  for(uint32_t index=1u;index<*(volatile uint8_t *)(input+19u);++index){
   rows=*(volatile uint32_t *)(input+20u);id=*(volatile uint8_t *)input;
   uintptr_t link=opencfw_em9305_config_link_find_31abc0(id,*(volatile uint8_t *)(rows+opencfw_em9305_config_extended_stride(index)));
   uint32_t sum=0u,pos=0u;
   for(uint32_t j=0u;j<index;++j){rows=*(volatile uint32_t *)(input+20u);id=*(volatile uint8_t *)input;
    uintptr_t other=opencfw_em9305_config_link_find_31abc0(id,*(volatile uint8_t *)(rows+pos));
    sum+=opencfw_em9305_config_update_link_time(other);pos+=14u;
   }
   *(volatile uint32_t *)(link+16u)=*(volatile uint32_t *)(first_link+16u)-sum;
   *(volatile uint32_t *)(link+20u)=*(volatile uint32_t *)(first_link+16u);
  }
 }else{uint32_t index=0u,pos=0u;
  count=*(volatile uint8_t *)(input+19u);
  while(index<count){rows=*(volatile uint32_t *)(input+20u);id=*(volatile uint8_t *)input;
   uintptr_t link=opencfw_em9305_config_link_find_31abc0(id,*(volatile uint8_t *)(rows+opencfw_em9305_config_extended_stride(index)));
   count=*(volatile uint8_t *)(input+19u);
   if(index<count){uint32_t j=index,offset=pos;
    do{rows=*(volatile uint32_t *)(input+20u);id=*(volatile uint8_t *)input;
     uintptr_t other=opencfw_em9305_config_link_find_31abc0(id,*(volatile uint8_t *)(rows+offset));
     uint32_t t=*(volatile uint32_t *)(other+508u);
     uint32_t multiplier=*(volatile uint8_t *)(other+504u);
     uint32_t previous=*(volatile uint32_t *)(link+16u);
     count=*(volatile uint8_t *)(input+19u);
     uint32_t value=opencfw_em9305_config_update_mpywhl(t,multiplier)+previous;
     ++j;offset+=14u;*(volatile uint32_t *)(link+16u)=value;
    }while(j<count);
   }
   uint32_t baseline=*(volatile uint32_t *)(first_link+16u);pos+=14u;++index;
   *(volatile uint32_t *)(link+20u)=baseline;
  }
  uint32_t baseline=*(volatile uint32_t *)(first_link+16u);
  uint32_t interval=*(volatile uint16_t *)(first_link+500u);
  *(volatile uint32_t *)(channel+12u)=baseline;
  *(volatile uint16_t *)(channel+20u)=(uint16_t)interval;
 }
 *(volatile uint8_t *)(channel+2u)=*(volatile uint8_t *)(input+17u);
 *(volatile uint8_t *)(channel+22u)=(uint8_t)opencfw_em9305_config_channel_ready_3186a0(channel);
}

static unsigned char expected[16][656],ch[140];
static void w32(unsigned char *p,unsigned off,uint32_t v){memcpy(p+off,&v,4);}
static uint32_t r32(unsigned char *p,unsigned off){uint32_t v;memcpy(&v,p+off,4);return v;}
static uint32_t time_value(unsigned char *p,unsigned feature,unsigned overhead){unsigned a=p[480],b=p[481],x=p[448],y=p[444];uint32_t t=300+overhead;t+=a==1?x*8+112:a==2?x*4+60:a==3?feature?(x+4)*16+462:(x+4)*64+720:0;t+=b==1?y*8+112:b==2?y*4+60:b==3?feature?(y+4)*16+462:(y+4)*64+720:0;return t;}
int main(void){if(mmap((void*)0x800000,0x60000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;unsigned cases=0;
for(unsigned seed=0;seed<16;++seed)for(unsigned count=0;count<=16;++count)for(unsigned mode=0;mode<256;++mode){memset((void*)0x810000,0,0x40000);*(uint8_t*)0x810000=7;*(uint8_t*)0x810013=count;*(uint8_t*)0x810011=mode;*(uint32_t*)0x810014=0x811000;*(uint32_t*)0x805cac=0x814000;*(uint16_t*)0x814036=seed*3971;*(uint8_t*)0x805a86=seed&1?16:0;ready=seed+256;calls=0;
memset((void*)0x813000,0xa5,140);*(uint32_t*)0x813058=0;*(uint32_t*)0x81305c=0;memcpy(ch,(void*)0x813000,140);
uint32_t times[16],total=0;for(unsigned i=0;i<16;++i){*(uint8_t*)(uintptr_t)(0x811000+i*14)=i;unsigned char *p=(void*)(uintptr_t)(0x820000+i*656);memset(p,0x5a,656);p[480]=(seed+i)&7;p[481]=(seed+i*3)&7;p[448]=(seed+i*19)&255;p[444]=(seed+i*23)&255;p[504]=(seed+i*13)&255;*(uint16_t*)(p+500)=seed*4000+i;*(uint32_t*)(p+16)=seed*0x10000000u+i*17;memcpy(expected[i],p,656);times[i]=time_value(p,seed&1,seed*3971);if(i<count)total+=times[i];}
if(count)w32(ch,88,0x820000);if(count>1)w32(ch,92,0x820000+656);
for(unsigned i=0;i<count;++i){w32(expected[i],408,times[i]);w32(expected[i],508,mode==1?total:times[i]);}
if(mode==1){uint32_t base=r32(expected[0],508)*expected[0][504];memcpy(ch+20,expected[0]+500,2);w32(expected[0],20,base);w32(expected[0],16,base);w32(ch,12,base);uint32_t prefix=0;for(unsigned i=1;i<count;++i){prefix+=times[i-1];w32(expected[i],16,base-prefix);w32(expected[i],20,base);}}
else{for(unsigned i=0;i<count;++i){uint32_t acc=r32(expected[i],16);for(unsigned j=i;j<count;++j)acc+=times[j]*expected[j][504];w32(expected[i],16,acc);w32(expected[i],20,r32(expected[0],16));}w32(ch,12,r32(expected[0],16));memcpy(ch+20,expected[0]+500,2);}
ch[2]=mode;ch[22]=seed;
opencfw_em9305_config_extended_channel_update_326d0c(0x813000,0x810000);
if(memcmp(ch,(void*)0x813000,140))return 3;for(unsigned i=0;i<16;++i)if(memcmp(expected[i],(void*)(uintptr_t)(0x820000+i*656),656))return 4;
unsigned wanted=mode==1?count*(1+count)+1+(count?count-1:0)+(count*(count-1))/2:count+1+count+count*(count+1)/2;if(calls!=wanted)return 5;++cases;}
printf("PASS %u\n",cases);}
