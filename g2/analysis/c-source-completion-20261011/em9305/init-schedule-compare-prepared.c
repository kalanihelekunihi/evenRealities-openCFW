/* Complete318b78..318c18: connection arbitration with wrapped MPYWHL,
 * native unsigned comparisons and fresh queue/period reads. */
uint32_t opencfw_em9305_init_schedule_compare_318b78(uintptr_t first,uintptr_t second)
{
 if(*(volatile uint8_t *)(second+26u)!=1u)return (uint32_t)first;
 uintptr_t kind=*(volatile uint32_t *)(second+44u);
 if((*(volatile uint8_t *)kind&254u)!=4u)return (uint32_t)first;
 uintptr_t a=*(volatile uint32_t *)(first+36u);
 if(*(volatile uint8_t *)(a+1u)==0u)return (uint32_t)second;
 uintptr_t b=*(volatile uint32_t *)(second+36u);
 uint32_t priority_a=*(volatile uint8_t *)(a+401u);
 uint32_t priority_b=*(volatile uint8_t *)(b+401u);
 if(priority_a<priority_b)return (uint32_t)second;
 uint32_t period=*(volatile uint16_t *)(b+266u);
 uint32_t elapsed=*(volatile uint32_t *)(b+392u);
 uint32_t threshold=(uint32_t)(uint16_t)period*2500u;
 uint32_t product=opencfw_em9305_native_mpywhl(elapsed,10000u);
 if(product<threshold)return (uint32_t)second;
 if(priority_a!=0u)return (uint32_t)first;
 period=*(volatile uint16_t *)(a+266u);
 elapsed=*(volatile uint32_t *)(a+392u);
 threshold=(uint32_t)(uint16_t)period*2500u;
 product=opencfw_em9305_native_mpywhl(elapsed,10000u);
 if(product<threshold)return (uint32_t)first;
 if(*(volatile uint8_t *)(b+635u)!=255u)return (uint32_t)second;
 if(*(volatile uint8_t *)(a+635u)!=255u)return (uint32_t)first;
 if(opencfw_em9305_wsf_queue_empty(b+360u)==0u)return (uint32_t)second;
 if(opencfw_em9305_wsf_queue_empty(a+360u)==0u)return (uint32_t)first;
 uint32_t period_b=*(volatile uint16_t *)(b+266u);
 uint32_t period_a=*(volatile uint16_t *)(a+266u);
 if(period_a<(period_b>>2u))return (uint32_t)second;
 if(period_b>=(period_a>>2u))return (uint32_t)second;
 return (uint32_t)first;
}
