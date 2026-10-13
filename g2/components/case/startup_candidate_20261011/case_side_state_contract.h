/* SPDX-License-Identifier: MIT
 * Two source names for the authenticated CASE0x08003a00 state reset.
 * Nonzero selects left state, zero selects right; all fields are RAM-only.
 * Both entry names keep void-return ABI and distinct callable addresses.
 */
#ifndef CASE_SIDE_STATE_CONTRACT_H
#define CASE_SIDE_STATE_CONTRACT_H
#include <stdint.h>
void case_boot_button_mode_reset(uint32_t active);
void case_policy_fake_standby_set(uint32_t side);
#endif
