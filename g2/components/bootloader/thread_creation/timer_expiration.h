/* SPDX-License-Identifier: MIT. Bootloader timer expiration ABI. */
#ifndef OPENCFW_BOOT_TIMER_EXPIRATION_H
#define OPENCFW_BOOT_TIMER_EXPIRATION_H
#include <stdint.h>

/* 0x419406: base is the selected timer deadline in the normal due path,
 * and the list-head deadline during rollover. now is the sampled tick or
 * UINT32_MAX during rollover. */
void opencfw_bl_timer_expire(uint32_t base, uint32_t now);

/* 0x41965c: drain the current timer list and exchange current/overflow lists. */
void opencfw_bl_timer_rollover(void);

#endif
