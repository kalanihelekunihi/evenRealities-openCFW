#ifndef OPENCFW_CLOCK_GENERATORS_H
#define OPENCFW_CLOCK_GENERATORS_H
#include <stdint.h>
/* Explicit stock small-enum ABI; ordinary SDK enum layout is not this ABI. */
typedef struct {
 uint8_t reference, vco, fraction_mode, reference_divider, post1, post2;
 uint16_t feedback_integer;
 uint32_t feedback_fraction;
} opencfw_pll_config;
_Static_assert(sizeof(opencfw_pll_config)==12,"stock PLL descriptor size");
uint32_t opencfw_boot_startup_hf2_generate(uint32_t,uint32_t,uint32_t,uint32_t *);
uint32_t opencfw_boot_startup_pll_generate(uint8_t *,uint32_t,uint32_t);
uint32_t opencfw_boot_pll_min_generate(opencfw_pll_config *,uint32_t,uint32_t,uint32_t);
#endif
