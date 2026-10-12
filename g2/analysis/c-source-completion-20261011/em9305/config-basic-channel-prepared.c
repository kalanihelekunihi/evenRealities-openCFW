static inline uint32_t opencfw_em9305_config_update_macwhl(uint32_t prior,uint32_t a,uint32_t b)
{uint32_t result;__asm__ volatile("mov r58,%1\n\tmacwhl %0,%2,%3":"=r"(result):"r"(prior),"r"(a),"r"(b));return result;}
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
   if(b>second_limit)b=second_limit;
   *(volatile uint8_t *)(link+503u)=(uint8_t)b;
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
