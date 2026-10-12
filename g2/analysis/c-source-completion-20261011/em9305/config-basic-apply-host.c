#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned absent,alloc_fail,existing,free_links,find_existing,update_calls,channel_calls,alloc_calls,invalid,retry;
uintptr_t opencfw_em9305_ll_test_channel_find_31ab50(uint32_t id){if(id!=7)__builtin_trap();return absent?0:0x814000;}
uintptr_t opencfw_em9305_config_channel_allocate_316b5c(uint32_t id){if(id!=7)__builtin_trap();return alloc_fail?0:0x814000;}
uint32_t opencfw_em9305_config_existing_count_31b2a8(uintptr_t p){if(p!=0x810000)__builtin_trap();return existing;}
uint32_t opencfw_em9305_config_free_links_31b278(void){return free_links;}
uintptr_t opencfw_em9305_config_link_find_31abc0(uint32_t id,uint32_t slot){if(id!=7||slot!=3)__builtin_trap();return (find_existing||alloc_calls)?0x815000:0;}
uintptr_t opencfw_em9305_config_link_allocate_316bbc(uintptr_t ch){if(ch!=0x814000)__builtin_trap();++alloc_calls;return 0x815000;}
uintptr_t opencfw_em9305_ll_link_find_31ab88(uint32_t id){if(id!=23)__builtin_trap();return 0x815000;}
uint32_t opencfw_em9305_config_link_update_326ed8(uintptr_t link,uintptr_t p,uintptr_t row){if(link!=0x815000||p!=0x810000||row!=0x811000)__builtin_trap();++update_calls;return 0xbad;}
uint32_t opencfw_em9305_config_channel_update_326b00(uintptr_t ch,uintptr_t p){if(ch!=0x814000||p!=0x810000)__builtin_trap();++channel_calls;*(uint8_t*)0x814016=(!invalid)&&(!retry||(*(uint8_t*)0x811008==0&&*(uint8_t*)0x811009==0));return 0xff;}
extern uintptr_t opencfw_em9305_config_channel_allocate_316b5c(uint32_t);
extern uint32_t opencfw_em9305_config_existing_count_31b2a8(uintptr_t);
extern uint32_t opencfw_em9305_config_free_links_31b278(void);
extern uintptr_t opencfw_em9305_config_link_find_31abc0(uint32_t,uint32_t);
extern uintptr_t opencfw_em9305_config_link_allocate_316bbc(uintptr_t);
extern uint32_t opencfw_em9305_config_link_update_326ed8(uintptr_t,uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_config_channel_update_326b00(uintptr_t,uintptr_t);
static inline uint32_t opencfw_em9305_config_apply_stride(uint32_t i){return i*10u;}
/* Native3087ec..308a3c: full basic apply, existing/new link paths and bounded decrement passes. */
uint32_t opencfw_em9305_config_basic_apply_3087ec(uintptr_t input,uintptr_t output)
{
 uintptr_t channel=opencfw_em9305_ll_test_channel_find_31ab50(*(volatile uint8_t *)input);
 if(!channel){channel=opencfw_em9305_config_channel_allocate_316b5c(*(volatile uint8_t *)input);if(!channel)return 7u;}
 uint32_t latch=*(volatile uint8_t *)(uintptr_t)0x805ab1u;
 uint32_t busy=*(volatile uint8_t *)(channel+23u);
 if((busy|latch)!=0u)return 12u;
 if(*(volatile uint8_t *)(channel+1u)!=0u)return 12u;
 uint32_t existing=opencfw_em9305_config_existing_count_31b2a8(input);
 uint32_t count=*(volatile uint8_t *)(input+20u);
 if(count){uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
  uintptr_t rows=*(volatile uint32_t *)(input+24u);
  uint32_t max=*(volatile uint8_t *)(config+48u);
  for(uint32_t i=0u;i<count;++i){uintptr_t p=rows+8u+i*10u;
   uint32_t a=*(volatile uint8_t *)p;*(volatile uint8_t *)p=(uint8_t)(a<max?a:max);
   uint32_t b=*(volatile uint8_t *)(p+1u);*(volatile uint8_t *)(p+1u)=(uint8_t)(b<max?b:max);
  }
 }
 uint32_t free=opencfw_em9305_config_free_links_31b278();
 if(existing){if((int32_t)(count-existing)>(int32_t)free)return 7u;
  for(uint32_t i=0u;i<*(volatile uint8_t *)(input+20u);++i){
   uintptr_t rows=*(volatile uint32_t *)(input+24u);
   uint32_t offset=opencfw_em9305_config_apply_stride(i);
   uint32_t id=*(volatile uint8_t *)input,slot=*(volatile uint8_t *)(rows+offset);
   uintptr_t link=opencfw_em9305_config_link_find_31abc0(id,slot);
   if(link){uint32_t first=*(volatile uint8_t *)(link+528u);
    rows=*(volatile uint32_t *)(input+24u);uintptr_t row=rows+offset;
    if(first!=255u&&*(volatile uint16_t *)(row+2u)==0u)return 12u;
    if(*(volatile uint8_t *)(link+532u)!=255u&&*(volatile uint16_t *)(row+4u)==0u)return 12u;
    (void)opencfw_em9305_config_link_update_326ed8(link,input,row);
   }else{link=opencfw_em9305_config_link_allocate_316bbc(channel);
    rows=*(volatile uint32_t *)(input+24u);
    *(volatile uint8_t *)(link+10u)=0u;
    (void)opencfw_em9305_config_link_update_326ed8(link,input,rows+offset);
   }
   uint32_t link_id=*(volatile uint16_t *)(link+8u);
   *(volatile uint16_t *)(output+i*2u)=(uint16_t)link_id;
  }
 }else{if(count>free)return 9u;
  uint32_t i=0u;uint32_t live_count=*(volatile uint8_t *)(input+20u);
  if(live_count)do{uintptr_t link=opencfw_em9305_config_link_allocate_316bbc(channel);
   uintptr_t rows=*(volatile uint32_t *)(input+24u);
   *(volatile uint8_t *)(link+10u)=0u;
   (void)opencfw_em9305_config_link_update_326ed8(link,input,rows+i*10u);
   uint32_t link_id=*(volatile uint16_t *)(link+8u);
   live_count=*(volatile uint8_t *)(input+20u);
   ++i;*(volatile uint16_t *)(output+(i-1u)*2u)=(uint16_t)link_id;
  }while(i<live_count);
 }
 (void)opencfw_em9305_config_channel_update_326b00(channel,input);
 uint32_t changed=1u,complete=*(volatile uint8_t *)(channel+22u)==0u;
 while(changed&&complete){changed=0u;uint32_t i=0u,live_count;
  for(;;){live_count=*(volatile uint8_t *)(input+20u);if(i>=live_count)break;
   uintptr_t link=opencfw_em9305_ll_link_find_31ab88(*(volatile uint16_t *)(output+i*2u));
   uintptr_t rows=*(volatile uint32_t *)(input+24u),row=rows+opencfw_em9305_config_apply_stride(i);
   uint32_t a=*(volatile uint8_t *)(row+8u);if(a){*(volatile uint8_t *)(row+8u)=(uint8_t)(a-1u);changed=1u;}
   uint32_t bv=*(volatile uint8_t *)(row+9u);if(bv){*(volatile uint8_t *)(row+9u)=(uint8_t)(bv-1u);changed=1u;}
   (void)opencfw_em9305_config_link_update_326ed8(link,input,row);
   (void)opencfw_em9305_config_channel_update_326b00(channel,input);
   if(*(volatile uint8_t *)(channel+22u)!=0u)break;
   ++i;
  }
  complete=i>=live_count;
 }
 uint32_t all=1u,i=0u,count_final;
 for(;;){count_final=*(volatile uint8_t *)(input+20u);if(i>=count_final)break;
  uintptr_t rows=*(volatile uint32_t *)(input+24u);
  uintptr_t link=opencfw_em9305_config_link_find_31abc0(*(volatile uint8_t *)input,*(volatile uint8_t *)(rows+i*10u));
  if(*(volatile uint8_t *)(link+502u)==0u)all=0u;
  else if(*(volatile uint8_t *)(link+503u)==0u)all=0u;
  ++i;
 }
 if(!all)return 17u;
 if(*(volatile uint8_t *)(channel+22u)==0u)return 17u;
 *(volatile uint8_t *)(channel+112u)=(uint8_t)count_final;
 return 0u;
}

static void reset(void){memset((void*)0x810000,0,64);memset((void*)0x811000,0,32);memset((void*)0x814000,0,140);memset((void*)0x815000,0,656);memset((void*)0x812000,0xa5,8);*(uint8_t*)0x810000=7;*(uint8_t*)0x810014=1;*(uint32_t*)0x810018=0x811000;*(uint8_t*)0x811000=3;*(uint16_t*)0x811002=1;*(uint16_t*)0x811004=1;*(uint16_t*)0x815008=23;*(uint8_t*)0x8151f6=1;*(uint8_t*)0x8151f7=1;*(uint8_t*)0x815210=255;*(uint8_t*)0x815214=255;*(uint32_t*)0x805cac=0x813000;*(uint8_t*)0x813030=255;*(uint8_t*)0x805ab1=0;absent=alloc_fail=existing=find_existing=invalid=retry=0;free_links=8;update_calls=channel_calls=alloc_calls=0;}
static unsigned run(unsigned expect){unsigned r=opencfw_em9305_config_basic_apply_3087ec(0x810000,0x812000);if(r!=expect){printf("bad %u %u\n",r,expect);return 1;}return 0;}
int main(void){if(mmap((void*)0x800000,0x20000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;unsigned cases=0;
 for(unsigned e=0;e<2;++e)for(unsigned find=0;find<2;++find)for(unsigned a=0;a<256;++a)for(unsigned bv=0;bv<256;++bv){reset();existing=e;find_existing=find;retry=1;*(uint8_t*)0x811008=a;*(uint8_t*)0x811009=bv;if(run(0)||*(uint16_t*)0x812000!=23||*(uint8_t*)0x814070!=1||*(uint8_t*)0x811008||*(uint8_t*)0x811009)return 3;unsigned rounds=a>bv?a:bv;if(channel_calls!=1+rounds||update_calls!=1+rounds)return 4;++cases;}
 for(unsigned mode=0;mode<10;++mode){reset();unsigned expected=0;switch(mode){case 0:absent=alloc_fail=1;expected=7;break;case 1:*(uint8_t*)0x805ab1=1;expected=12;break;case 2:*(uint8_t*)0x814017=1;expected=12;break;case 3:*(uint8_t*)0x814001=1;expected=12;break;case 4:free_links=0;expected=9;break;case 5:existing=1;*(uint8_t*)0x810014=2;free_links=0;expected=7;break;case 6:existing=find_existing=1;*(uint8_t*)0x815210=0;*(uint16_t*)0x811002=0;expected=12;break;case 7:existing=find_existing=1;*(uint8_t*)0x815214=0;*(uint16_t*)0x811004=0;expected=12;break;case 8:invalid=1;expected=17;break;case 9:*(uint8_t*)0x8151f6=0;expected=17;break;}
 if(run(expected))return 5;
 ++cases;
 }
 printf("PASS %u\n",cases);return 0;}
