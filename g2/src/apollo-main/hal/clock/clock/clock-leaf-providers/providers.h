#ifndef AUDIO_CLOCK_LEAF_PROVIDERS_H
#define AUDIO_CLOCK_LEAF_PROVIDERS_H
#include <stdint.h>
uint32_t audio_ext_request(uint32_t user),audio_ext_release(uint32_t user);
uint32_t audio_pll_power_enable(void),audio_pll_power_disable(void),audio_pll_power_enabled(uint8_t *enabled);
uint32_t audio_hfrc_force(uint32_t enabled),audio_hfrc_apply(uint32_t config),audio_hfrc_disable(void);
uint32_t audio_hfrc2_force(uint32_t enabled),audio_hfrc2_apply(const void *config),audio_hfrc2_disable(void);
/* DIV_0_TRP=0 model for malformed denominators; supported generation uses div0..3. */
uint32_t audio_hfrc2_ratio(uint32_t reference_hz,uint32_t target_hz,uint32_t divider,uint32_t *ratio);
uint32_t audio_hfrc_target(uint32_t reference_hz,uint32_t target_hz,uint32_t *target);
#endif
