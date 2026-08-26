/*
 * SPDX-License-Identifier: Apache-2.0
 *
 * Production-routed ABI for the two linked G2 Cordio WSF string helpers.
 */

#ifndef OPEN_CFW_RUNTIME_CORDIO_WSTR_CANDIDATE_H
#define OPEN_CFW_RUNTIME_CORDIO_WSTR_CANDIDATE_H

#include <stdint.h>

void open_cfw_cordio_wstr_reverse_copy_candidate(
    uint8_t *destination,
    const uint8_t *source,
    uint16_t length
);
void open_cfw_cordio_wstr_reverse_candidate(uint8_t *buffer, uint8_t length);

#endif /* OPEN_CFW_RUNTIME_CORDIO_WSTR_CANDIDATE_H */
