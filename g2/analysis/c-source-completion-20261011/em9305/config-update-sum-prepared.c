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
