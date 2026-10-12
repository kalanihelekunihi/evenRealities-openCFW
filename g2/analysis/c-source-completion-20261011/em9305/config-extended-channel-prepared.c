extern uint32_t opencfw_em9305_config_channel_ready_3186a0(uintptr_t);
static inline uint32_t opencfw_em9305_config_update_mpywhl(uint32_t a,uint32_t b)
{uint32_t result;__asm__ volatile("mpywhl %0,%1,%2":"=r"(result):"r"(a),"r"(b));return result;}
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
