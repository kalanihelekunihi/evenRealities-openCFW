extern uintptr_t opencfw_em9305_config_channel_allocate_316b5c(uint32_t);
extern uint32_t opencfw_em9305_config_existing_count_31b2a8(uintptr_t);
extern uint32_t opencfw_em9305_config_free_links_31b278(void);
extern uintptr_t opencfw_em9305_config_link_find_31abc0(uint32_t,uint32_t);
extern uintptr_t opencfw_em9305_config_link_allocate_316bbc(uintptr_t);
extern uint32_t opencfw_em9305_config_link_update_326ed8(uintptr_t,uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_config_channel_update_326b00(uintptr_t,uintptr_t);
static inline uint32_t opencfw_em9305_config_apply_stride(uint32_t i)
{uint32_t r;__asm__ volatile("mpy %0,%1,10":"=r"(r):"r"(i));return r;}
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
