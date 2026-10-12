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
