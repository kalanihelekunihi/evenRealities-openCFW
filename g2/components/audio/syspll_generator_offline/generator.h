#ifndef AUDIO_SYSPLL_GENERATOR_H
#define AUDIO_SYSPLL_GENERATOR_H
#include "../clock_driver_config_offline/driver.h"
/* Reconstructed stock helpers. Float inputs are MHz; integer inputs are Hz.
 * Postdiv output must be nonNULL if a valid candidate is found.
 * No configuration reference byte is written by any generator.
 * Malformed integer divisions use the explicit DIV_0_TRP=0 offline profile. */
float audio_pll_gcd(float a,float b);
uint32_t audio_pll_integer(float reference_mhz,float vco_mhz,uint8_t *refdiv,uint16_t *fbdiv);
uint32_t audio_pll_fraction(float reference_mhz,float vco_mhz,uint8_t *refdiv,uint16_t *fbdiv,uint32_t *fraction);
uint32_t audio_pll_generate(audio_pll_config *config,float reference_mhz,float vco_mhz);
uint32_t audio_pll_min_vco(audio_pll_config *config,uint32_t reference_hz,uint32_t output_hz,uint32_t minimum_vco_hz);
uint32_t audio_pll_postdiv(audio_pll_config *config,uint32_t reference_hz,uint32_t output_hz);
#endif
