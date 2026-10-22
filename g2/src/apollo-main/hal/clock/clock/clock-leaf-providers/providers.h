#ifndef AUDIO_CLOCK_LEAF_PROVIDERS_H
#define AUDIO_CLOCK_LEAF_PROVIDERS_H
#include <stdint.h>
uint32_t audio_ext_request(uint32_t user),audio_ext_release(uint32_t user);
/* The HFRC/HFRC2 leaves below are AmbiqSuite 5.1.0 am_hal_clkgen functions;
 * these names are payload defsym aliases of the upstream definitions. */
uint32_t audio_hfrc_force(uint32_t enabled),audio_hfrc_apply(uint32_t config),audio_hfrc_disable(void);
uint32_t audio_hfrc2_force(uint32_t enabled),audio_hfrc2_apply(const void *config),audio_hfrc2_disable(void);
/* DIV_0_TRP=0 model for malformed denominators; supported generation uses div0..3. */
uint32_t audio_hfrc2_ratio(uint32_t reference_hz,uint32_t target_hz,uint32_t divider,uint32_t *ratio);
uint32_t audio_hfrc_target(uint32_t reference_hz,uint32_t target_hz,uint32_t *target);
#endif
