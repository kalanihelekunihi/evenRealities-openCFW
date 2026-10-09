#ifndef AUDIO_CLOCK_PUBLIC_DISPATCH_H
#define AUDIO_CLOCK_PUBLIC_DISPATCH_H
#include <stdint.h>
/* Public entry points narrow both arguments to stock one-byte enums.
 * Validate full-width app input before passing it here; wrapping is stock ABI.
 * LFRC/XTAL-LS children assume a validated user, like other manager children. */
uint32_t audio_lfrc_request(uint32_t user);
uint32_t audio_lfrc_release(uint32_t user);
uint32_t audio_xtal_ls_request(uint32_t user);
uint32_t audio_xtal_ls_release(uint32_t user);
uint32_t audio_clock_request(uint32_t clock, uint32_t user);
uint32_t audio_clock_release(uint32_t clock, uint32_t user);
#endif
