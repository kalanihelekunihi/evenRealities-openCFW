/* SPDX-License-Identifier: MIT
 * Native board configuration and mutable PCM fields: 0x100269a4..0x10026a94
 * source initializer, 0x200269a4 runtime alias after the stage copy.
 */
#ifndef GX8002_RESIDENT_BOARD_PRODUCT_STATE_H
#define GX8002_RESIDENT_BOARD_PRODUCT_STATE_H
#include <stdint.h>

struct gx8002_board_product_state {
    uint32_t words[60];
};
_Static_assert(sizeof(struct gx8002_board_product_state) == 240,
               "native board configuration extent");
extern struct gx8002_board_product_state gx8002_board_state_269a4;

#endif
