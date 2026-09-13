/* SPDX-License-Identifier: MIT */
/* Initial active KWS state agrees with pinned upstream max_decoder.c. */
#include <decoder.h>
int open_cfw_gx8002_max_decoder_state
    __attribute__((section(".data.decoder_state"))) = VUI_KWS_ACTIVE_STATE;
_Static_assert(sizeof(int) == 4, "decoder state ABI");
