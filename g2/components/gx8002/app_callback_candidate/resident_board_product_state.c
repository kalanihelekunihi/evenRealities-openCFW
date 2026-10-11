/* SPDX-License-Identifier: MIT
 * Source initializer 0x100269a4..0x100269cc. XIP board accessor 0x10203004
 * returns the 0x200269a4 runtime alias; board log code reads halfword +0x20.
 * Field meanings beyond these consumers remain unattributed.
 */
#include <stdint.h>

struct gx8002_board_product_state {
    uint32_t field_00;
    uint32_t field_04;
    uint32_t field_08_0c[2];
    uint32_t field_10;
    uint32_t field_14_1c[3];
    uint32_t field_20;
    uint32_t field_24;
};
_Static_assert(sizeof(struct gx8002_board_product_state) == 40,
               "native board state extent");

const struct gx8002_board_product_state gx8002_board_state_269a4
    __attribute__((section(".gx8002.board_state.269a4"), used,
                   aligned(4))) = {
    .field_00 = 2u,
    .field_04 = UINT32_C(0x498),
    .field_10 = 1u,
    .field_20 = UINT32_C(0xc98),
};
