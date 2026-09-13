/* SPDX-License-Identifier: MIT */
/* Recovered standby state and countdown, following the TWS task buffer. */
#include <stdint.h>
struct tws_standby_words { uint32_t state, countdown; };
_Static_assert(sizeof(struct tws_standby_words)==8,"standby state ABI");
struct tws_standby_words open_cfw_gx8002_tws_standby_words
    __attribute__((section(".bss.tws_standby_words")));
