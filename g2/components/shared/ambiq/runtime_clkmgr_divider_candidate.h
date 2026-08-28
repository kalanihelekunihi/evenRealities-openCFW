/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_RUNTIME_CLKMGR_DIVIDER_CANDIDATE_H
#define OPEN_CFW_RUNTIME_CLKMGR_DIVIDER_CANDIDATE_H

#include <stdint.h>

enum open_cfw_clkmgr_divider_status {
    OPEN_CFW_CLKMGR_DIVIDER_OK = 0,
    OPEN_CFW_CLKMGR_DIVIDER_INVALID_ARGUMENT = 6,
};

/*
 * Generate the HFRC2 UQ17.15 divider coefficient used by the Apollo510 clock
 * manager.  source_divider_exponent selects source_hz / 2^exponent.
 */
uint32_t open_cfw_clkmgr_hfrc2_uq15_divider(
    uint32_t source_hz,
    uint32_t requested_hz,
    uint32_t source_divider_exponent,
    uint32_t *divider_uq15);

/* Generate the integer HFRC divider used by the Apollo510 clock manager. */
uint32_t open_cfw_clkmgr_hfrc_integer_divider(
    uint32_t source_hz,
    uint32_t requested_hz,
    uint32_t *divider);

#endif
