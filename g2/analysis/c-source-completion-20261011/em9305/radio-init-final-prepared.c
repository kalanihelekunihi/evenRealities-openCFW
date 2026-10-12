extern uint32_t opencfw_em9305_init_features_3099cc(uint32_t);
extern uint32_t opencfw_em9305_init_features_308ff8(uint32_t);
extern uint32_t opencfw_em9305_init_event_state_30e0e8(uint32_t);
/* Native30bf6c..30bfea: preserve all writes before the genuine reset
 * state provider, including pending capabilities later overwritten by reset. */
uint32_t opencfw_em9305_init_final_30bf6c(uint32_t incoming)
{
 *(volatile uint8_t *)(uintptr_t)0x805b18u=(uint8_t)incoming;
 uint32_t value=opencfw_em9305_init_features_3099cc(incoming);
 value=opencfw_em9305_init_features_308ff8(value);
 (void)value;
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t previous=*(volatile uint32_t *)(uintptr_t)0x805b30u;
 uint32_t a=*(volatile uint8_t *)(config+62u),b=*(volatile uint8_t *)(config+63u),c=*(volatile uint8_t *)(config+64u);
 *(volatile uint8_t *)(uintptr_t)0x805aa8u=0u;
 *(volatile uint8_t *)(uintptr_t)0x805a78u=0u;
 *(volatile uint8_t *)(uintptr_t)0x805a76u=0u;
 *(volatile uint32_t *)(uintptr_t)0x805a70u=0u;
 *(volatile uint8_t *)(uintptr_t)0x805a74u=0u;
 uint32_t d=*(volatile uint8_t *)(config+65u);
 *(volatile uint32_t *)(uintptr_t)0x805b44u=0u;
 *(volatile uint32_t *)(uintptr_t)0x805b40u=0u;
 uint32_t bits=previous|(a<<8u)|(b<<11u)|(c<<9u)|(d<<10u);
 *(volatile uint32_t *)(uintptr_t)0x805b30u=bits;
 uint8_t lower,upper;
 (void)opencfw_em9305_ll_signed_bounds_31026c((uintptr_t)&lower,(uintptr_t)&upper);
 int32_t bound=(int8_t)upper;
 bits=*(volatile uint32_t *)(uintptr_t)0x805b30u;
 if(bound>19)bits|=1u<<15u;
 *(volatile uint32_t *)(uintptr_t)0x805b30u=bits;
 value=opencfw_em9305_init_state_30e9a4((uint32_t)bound);
 return opencfw_em9305_init_event_state_30e0e8(value);
}
