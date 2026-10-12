/* SPDX-License-Identifier: MIT
 * Source initializer 0x100269a4..0x10026a94. Native XIP audio input/output
 * consumers read and write the 60-word runtime alias through byte +0xec.
 * Unnamed word meanings remain unattributed; nonzero values are exact stock.
 */
#include "resident_board_product_state.h"

struct gx8002_board_product_state gx8002_board_state_269a4
    __attribute__((section(".gx8002.board_state.269a4"), used,
                   aligned(4))) = {
    .words = {
        [0] = 2u, [1] = 0x498u, [4] = 1u, [8] = 0xc98u,
        [11] = 1u, [15] = 0x498u, [18] = 1u, [22] = 6u,
        [23] = 1u, [25] = 2u, [28] = 1u, [30] = 1u,
        [36] = 2u, [42] = 1u, [47] = 1u, [48] = 2u,
        [51] = 1u, [53] = 1u, [54] = 2u, [59] = 1u,
    },
};
