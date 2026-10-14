/* Apollo MAIN s200 v2.2.6.10 ALS state storage.
 * The authenticated startup data record initializes 0x20000060..0x2000006b
 * to three 0x400 words. Its zero initializer covers 0x20004558..0x20075047,
 * including the six other cells below. Final address placement is a linker
 * contract and is not established by this relocatable source file. */
#include <stdint.h>

uint32_t audio_als_scale_clamped = 0x400u;
uint32_t audio_als_scale_active = 0x400u;
uint32_t audio_als_scale_shadow = 0x400u;

uint32_t audio_als_active_previous;
uint32_t audio_als_default_previous;
uint32_t audio_als_recompute_pending;
uint32_t audio_als_curve_index;
uint32_t audio_als_curve_nominal;
uint32_t audio_als_curve_adjusted;
