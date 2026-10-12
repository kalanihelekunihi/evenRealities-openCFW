static inline uint32_t opencfw_em9305_config_limit_mpyuw(uint32_t a,uint32_t factor)
{uint32_t r;if(factor==1000u)__asm__ volatile("mpyuw %0,%1,1000":"=r"(r):"r"(a));else __asm__ volatile("mpyuw %0,%1,1250":"=r"(r):"r"(a));return r;}
static inline uint32_t opencfw_em9305_config_limit_divu(uint32_t a,uint32_t b)
{uint32_t r=1u;__asm__ volatile("divu %0,%1,%2":"+r"(r):"r"(a),"r"(b));return r;}
/* Native31855c..3185a8: full limit computation, full-width selector, unsigned quotient and low-byte return. */
uint32_t opencfw_em9305_config_basic_limit_31855c(uintptr_t link,uintptr_t input,uint32_t selector)
{
 uint32_t policy=*(volatile uint16_t *)(input+(selector?16u:18u));
 uint32_t interval=*(volatile uint16_t *)(link+500u);
 uint32_t budget=opencfw_em9305_config_limit_mpyuw(policy,1000u);
 uint32_t mode=*(volatile uint8_t *)(link+484u);
 uint32_t baseline=*(volatile uint32_t *)(link+20u);
 uint32_t period=opencfw_em9305_config_limit_mpyuw(interval,1250u);
 uint32_t time=*(volatile uint32_t *)(link+(selector?492u:496u));
 uint32_t value=budget-baseline;
 if(mode==1u)value-=time;else value+=time;
 uint32_t result=1u;
 if(value>=period)result=opencfw_em9305_config_limit_divu(value,period);
 return result&255u;
}
