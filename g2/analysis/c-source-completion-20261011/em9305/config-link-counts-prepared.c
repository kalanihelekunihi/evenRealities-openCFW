/* Native31abc0..31ac08: active channel/slot match over656-byte rows. */
uintptr_t opencfw_em9305_config_link_find_31abc0(uint32_t channel,uint32_t slot)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t count=*(volatile uint8_t *)(config+53u);
 if(!count)return 0u;
 uintptr_t row=*(volatile uint32_t *)(uintptr_t)0x805c68u;
 for(uint32_t i=0u;i<count;++i,row+=656u){
  if(*(volatile uint8_t *)row==0u)continue;
  if(*(volatile uint8_t *)(row+11u)!=channel)continue;
  if(*(volatile uint8_t *)(row+12u)==slot)return row;
 }
 return 0u;
}
/* Native31b278..31b2a8: byte-sized inactive link count. */
uint32_t opencfw_em9305_config_free_links_31b278(void)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t count=*(volatile uint8_t *)(config+53u),free=0u;
 if(count){uintptr_t row=*(volatile uint32_t *)(uintptr_t)0x805c68u;
  for(uint32_t i=0u;i<count;++i,row+=656u)if(*(volatile uint8_t *)row==0u)++free;
 }
 return free&255u;
}
/* Native31b2a8..31b2d0: captured input count/rows/id, lookup each compact row. */
uint32_t opencfw_em9305_config_existing_count_31b2a8(uintptr_t input)
{
 uint32_t count=*(volatile uint8_t *)(input+20u),found=0u;
 if(count){uintptr_t rows=*(volatile uint32_t *)(input+24u);
  uint32_t channel=*(volatile uint8_t *)input;
  for(uint32_t i=0u;i<count;++i){uint32_t slot=*(volatile uint8_t *)(rows+i*10u);
   found+=opencfw_em9305_config_link_find_31abc0(channel,slot)!=0u;
  }
 }
 return found&255u;
}
