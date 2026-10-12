static inline uint32_t opencfw_em9305_config_round_mpyw(uint32_t a,uint32_t b)
{uint32_t r;__asm__ volatile("mpyw %0,%1,%2":"=r"(r):"r"(a),"r"(b));return r;}
static inline uint32_t opencfw_em9305_config_round_mpyuw(uint32_t a,uint32_t b)
{uint32_t r;__asm__ volatile("mpyuw %0,%1,%2":"=r"(r):"r"(a),"r"(b));return r;}
/* Native317efc..317f2c: byte-wrapped numerator/divisor and ceiling quotient. */
uint32_t opencfw_em9305_config_basic_rounding_317efc(uint32_t first,uint32_t second,uint32_t third)
{
 uint32_t product=opencfw_em9305_config_round_mpyw(third-1u,first);
 uint32_t numerator=opencfw_em9305_config_round_mpyuw(first,second+1u)&255u;
 uint32_t divisor=(product&255u)+1u;
 uint32_t raw_divisor=divisor;
 if((divisor&255u)!=divisor)divisor=1u;
 divisor&=255u;
 uint32_t quotient=opencfw_em9305_config_limit_divu(numerator,divisor);
 uint32_t reproduced=quotient;
 if(raw_divisor==divisor)reproduced=opencfw_em9305_config_update_mpywhl(quotient,raw_divisor);
 reproduced&=255u;
 return (quotient+(numerator!=reproduced))&255u;
}
