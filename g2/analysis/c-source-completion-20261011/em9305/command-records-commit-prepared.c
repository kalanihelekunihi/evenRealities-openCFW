/* Native3096a8..309874: complete validation, timing, free-slot allocation,
 * partial writes and fresh post-child base loads. */
uint32_t opencfw_em9305_command_records_commit_3096a8(uint32_t id,uint32_t count,uintptr_t rows)
{
 if(id>239u)return 18u;
 uintptr_t record=opencfw_em9305_radio_record_find_31aa64(id);
 if(record==0u)return 66u;
 uintptr_t row_state=record+796u;
 if(*(volatile uint8_t *)(record+718u)==0u)return 12u;
 if(count-1u>=15u)return 18u;
 for(uint32_t i=0u;i<count;++i){uintptr_t row=rows+i*8u;
  if(*(volatile uint8_t *)(row+3u)>251u)return 18u;
  uint32_t value=*(volatile uint8_t *)(row+1u),maximum=*(volatile uint8_t *)(row_state+2u);
  if(maximum<value)return 18u;
  uint32_t index=*(volatile uint8_t *)row;
  if(index>=15u)return 18u;
  uintptr_t configuration=*(volatile uint32_t *)(record+0xafcu);
  uint32_t start=*(volatile uint8_t *)(configuration+78u),span=*(volatile uint8_t *)(configuration+79u);
  if(start+span<=index||index<start)return 12u;
  uint32_t current=*(volatile uint8_t *)(row_state+3u);
  if(index<current)return 70u;
  if(index==current&&*(volatile uint8_t *)(row_state-107u)!=0u)return 70u;
 }
 for(uint32_t i=0u;i<count;++i){
  uintptr_t configuration=*(volatile uint32_t *)(uintptr_t)0x805cacu;
  uint32_t spacing=*(volatile uint16_t *)(configuration+20u),live_spacing=*(volatile uint32_t *)(record+72u);
  if(live_spacing>spacing)spacing=live_spacing;
  uint32_t budget;
  if(*(volatile uint8_t *)(row_state+2u)!=0u)budget=opencfw_em9305_config_limit_mpyuw(*(volatile uint8_t *)row_state,1250u);
  else budget=*(volatile uint32_t *)(record+792u);
  uint32_t timing=0u;
  if(*(volatile uint8_t *)(row_state+8u)!=0u){uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x801a14u;if(callback)timing=((uint32_t(*)(uint32_t))callback)(*(volatile uint8_t *)(row_state+8u));}
  uint32_t size=*(volatile uint8_t *)(rows+i*8u+3u),phy=*(volatile uint8_t *)(record+63u);
  uint32_t needed=opencfw_em9305_radio_duration_312be4(phy,0u,timing,(uint16_t)spacing,size,0u,2u,5u);
  if(budget-150u<needed)return 69u;
 }
 uintptr_t base=*(volatile uint32_t *)(row_state+364u);
 for(uint32_t i=0u;i<count;++i){
  uint32_t high=*(volatile uint32_t *)(base+0xf08u),low=*(volatile uint32_t *)(base+0xf04u);
  uintptr_t mask_pointer=base+0xf04u;
  uint32_t free_index=255u;
  for(uint32_t bit=0u;bit<15u;++bit)if((low&(1u<<bit))!=0u){free_index=bit;break;}
  if(free_index==255u)return 7u;
  uintptr_t row=rows+i*8u;
  uint32_t index=*(volatile uint8_t *)row;
  uintptr_t mapping=base+index+0xf0cu;
  if(*(volatile uint8_t *)mapping!=255u)return 18u;
  *(volatile uint8_t *)mapping=(uint8_t)free_index;
  base=*(volatile uint32_t *)(row_state+364u);
  uint32_t size=*(volatile uint8_t *)(row+3u);
  low&=~(1u<<free_index);
  uintptr_t slot=base+(free_index<<8);
  uintptr_t source=*(volatile uint32_t *)(row+4u);
  *(volatile uint32_t *)(mask_pointer+4u)=high;
  *(volatile uint32_t *)mask_pointer=low;
  *(volatile uint8_t *)(slot+1u)=(uint8_t)size;
  (void)opencfw_em9305_memcpy((void *)(slot+4u),(const void *)source,size);
  source=*(volatile uint32_t *)(row+4u);size=*(volatile uint8_t *)(row+3u);
  uint32_t seed=opencfw_em9305_pal_random_step();
  uint32_t checksum=opencfw_em9305_crc_update_304678(seed,size,source);
  base=*(volatile uint32_t *)(row_state+364u);
  uint32_t first=*(volatile uint8_t *)(row+1u),second=*(volatile uint8_t *)(row+2u);
  slot=base+(free_index<<8);
  *(volatile uint16_t *)(slot+2u)=(uint16_t)checksum;
  *(volatile uint8_t *)slot=1u;
  *(volatile uint8_t *)(base+0xf00u)=(uint8_t)first;
  *(volatile uint8_t *)(base+0xf01u)=(uint8_t)second;
 }
 *(volatile uint8_t *)(record+1156u)=1u;
 return 0u;
}
