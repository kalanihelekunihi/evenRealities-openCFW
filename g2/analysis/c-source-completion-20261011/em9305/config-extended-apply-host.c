#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned n_existing,n_free,n_alloc,n_update,n_clear,busy,allocfail,haschannel,shrink,updated_channel;
static unsigned initial_count;
uintptr_t opencfw_em9305_config_link_find_31abc0(uint32_t id,uint32_t slot){if(id!=7)__builtin_trap();return slot<n_existing?(0x820000u+slot*656u):0u;}
uintptr_t opencfw_em9305_ll_test_channel_find_31ab50(uint32_t id){if(id!=7)__builtin_trap();return haschannel?0x813000u:0u;}
uint32_t opencfw_em9305_command_config_clear_30ca18(uint32_t id){if(id!=7)__builtin_trap();++n_clear;return 99;}
uintptr_t opencfw_em9305_config_channel_allocate_316b5c(uint32_t id){if(id!=7)__builtin_trap();return allocfail?0u:0x813000u;}
uint32_t opencfw_em9305_config_free_links_31b278(void){return n_free;}
uintptr_t opencfw_em9305_config_link_allocate_316bbc(uintptr_t ch){if(ch!=0x813000)__builtin_trap();uintptr_t link=0x820000u+(n_existing+n_alloc)*656u;++n_alloc;*(uint16_t*)(link+8u)=400+n_existing+n_alloc-1;*(uint8_t*)(link+10u)=99;return link;}
static uint32_t opencfw_em9305_config_extended_stride(uint32_t i){return i*14u;}
void opencfw_em9305_config_extended_link_update_3272d8(uintptr_t link,uintptr_t input,uintptr_t row){if(input!=0x810000||row!=0x811000u+n_update*14u)__builtin_trap();unsigned index=*(uint8_t*)row;if(index>=n_existing&&*(uint8_t*)(link+10u)!=0)__builtin_trap();++n_update;if(shrink)*(uint8_t*)0x810013=1;}
void opencfw_em9305_config_extended_channel_update_326d0c(uintptr_t ch,uintptr_t in){if(ch!=0x813000||in!=0x810000)__builtin_trap();++updated_channel;}
extern uint32_t opencfw_em9305_config_extended_existing_31b2d0(uintptr_t);
extern void opencfw_em9305_config_extended_link_update_3272d8(uintptr_t,uintptr_t,uintptr_t);
extern void opencfw_em9305_config_extended_channel_update_326d0c(uintptr_t,uintptr_t);
/* Native31b2d0..31b2f8: captured count, input ID and 14-byte row lookup. */
uint32_t opencfw_em9305_config_extended_existing_31b2d0(uintptr_t input)
{
 uint32_t count=*(volatile uint8_t *)(input+19u),found=0u;
 if(count){uintptr_t rows=*(volatile uint32_t *)(input+20u);uint32_t id=*(volatile uint8_t *)input;
  for(uint32_t i=0u;i<count;++i)found+=opencfw_em9305_config_link_find_31abc0(id,*(volatile uint8_t *)(rows+i*14u))!=0u;
 }
 return found&255u;
}
/* Native308a3c..308b14: complete extended apply. Native ignores clear status and preserves mutations on failure. */
uint32_t opencfw_em9305_config_extended_apply_308a3c(uintptr_t input,uintptr_t output)
{
 uintptr_t channel=opencfw_em9305_ll_test_channel_find_31ab50(*(volatile uint8_t *)input);
 if(channel){if(*(volatile uint8_t *)(channel+23u))return 12u;
  (void)opencfw_em9305_command_config_clear_30ca18(*(volatile uint8_t *)input);
 }
 channel=opencfw_em9305_config_channel_allocate_316b5c(*(volatile uint8_t *)input);
 if(!channel)return 7u;
 uint32_t existing=opencfw_em9305_config_extended_existing_31b2d0(input);
 uint32_t count=*(volatile uint8_t *)(input+19u);
 if(existing){uint32_t free=opencfw_em9305_config_free_links_31b278();
  if((int32_t)free<(int32_t)(count-existing))return 7u;
  for(uint32_t i=0u;i<*(volatile uint8_t *)(input+19u);++i){uint32_t offset=opencfw_em9305_config_extended_stride(i);
   uintptr_t rows=*(volatile uint32_t *)(input+20u);
   uintptr_t link=opencfw_em9305_config_link_find_31abc0(*(volatile uint8_t *)input,*(volatile uint8_t *)(rows+offset));
   if(!link){link=opencfw_em9305_config_link_allocate_316bbc(channel);rows=*(volatile uint32_t *)(input+20u);*(volatile uint8_t *)(link+10u)=0u;}
   else rows=*(volatile uint32_t *)(input+20u);
   opencfw_em9305_config_extended_link_update_3272d8(link,input,rows+offset);
   *(volatile uint16_t *)(output+i*2u)=*(volatile uint16_t *)(link+8u);
  }
 }else{if(opencfw_em9305_config_free_links_31b278()<count)return 9u;
  if(*(volatile uint8_t *)(input+19u)){uint32_t i=0u,offset=0u;
   do{uintptr_t link=opencfw_em9305_config_link_allocate_316bbc(channel);uintptr_t rows=*(volatile uint32_t *)(input+20u);
    *(volatile uint8_t *)(link+10u)=0u;
    opencfw_em9305_config_extended_link_update_3272d8(link,input,rows+offset);
    uint32_t id=*(volatile uint16_t *)(link+8u);count=*(volatile uint8_t *)(input+19u);++i;offset+=14u;
    *(volatile uint16_t *)output=(uint16_t)id;output+=2u;
   }while(i<count);
  }
 }
 opencfw_em9305_config_extended_channel_update_326d0c(channel,input);
 *(volatile uint8_t *)(channel+112u)=*(volatile uint8_t *)(input+19u);
 return 0u;
}

static void reset(unsigned count,unsigned ex,unsigned free){memset((void*)0x810000,0,0x40000);*(uint8_t*)0x810000=7;*(uint8_t*)0x810013=count;*(uint32_t*)0x810014=0x811000;for(unsigned i=0;i<count;++i){*(uint8_t*)(uintptr_t)(0x811000+i*14)=i;*(uint16_t*)(uintptr_t)(0x820008+i*656)=400+i;}n_existing=ex;n_free=free;n_alloc=n_update=n_clear=busy=allocfail=haschannel=shrink=updated_channel=0;initial_count=count;}
int main(void){if(mmap((void*)0x800000,0x60000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;unsigned cases=0;
for(unsigned count=0;count<256;++count)for(unsigned mode=0;mode<3;++mode)for(unsigned free=0;free<256;++free){unsigned ex=mode==0?0:mode==1?count:count/2;reset(count,ex,free);unsigned expected=free<count-ex?(ex?7:9):0;unsigned result=opencfw_em9305_config_extended_apply_308a3c(0x810000,0x812000);if(result!=expected)return 3;if(expected){if(n_update||n_alloc||updated_channel)return 4;}else{if(n_update!=count||n_alloc!=count-ex||updated_channel!=1||*(uint8_t*)0x813070!=count)return 5;for(unsigned i=0;i<count;++i)if(*(uint16_t*)(uintptr_t)(0x812000+i*2)!=400+i)return 6;}++cases;}
for(unsigned ex=0;ex<=2;++ex){reset(4,ex,255);shrink=1;if(opencfw_em9305_config_extended_apply_308a3c(0x810000,0x812000)!=0||n_update!=1||*(uint8_t*)0x813070!=1)return 7;++cases;}
reset(2,0,255);haschannel=1;*(uint8_t*)0x813017=1;if(opencfw_em9305_config_extended_apply_308a3c(0x810000,0x812000)!=12||n_clear||n_alloc)return 8;++cases;
reset(2,0,255);allocfail=1;if(opencfw_em9305_config_extended_apply_308a3c(0x810000,0x812000)!=7||n_update)return 9;++cases;
reset(2,0,255);haschannel=1;if(opencfw_em9305_config_extended_apply_308a3c(0x810000,0x812000)!=0||n_clear!=1)return 10;++cases;
printf("PASS %u\n",cases);}
