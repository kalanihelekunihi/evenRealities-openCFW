/* SPDX-License-Identifier: MIT
 * Stock B stage1 flash reader 0x10000fdc. Control flow is attributable to
 * NationalChip GX8002 arch/soc/grus/spl/spl_spinor.c:sflash_readdata,
 * pinned commit 8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5.
 * Native 0x10000fec enables module 13, 0x10000ff0 conditionally initializes
 * the controller, 0x10000ffe polls command 5 until status bit 0 clears,
 * 0x10001014 handles zero length, 0x10001052 chunks to 0x10000 bytes, and
 * 0x100010c6 disables module 13. The inlined controller descendants retain
 * genuine contracts.
 */
#include <stdint.h>
extern volatile uint32_t gx8002_stage1_flash_jedec;

extern void gx8002_image_b_stage1_clock_gate_100001f8(
    uint32_t module, uint32_t enabled);
extern void gx8002_image_b_stage1_flash_initialize_100010e2(void);
extern uint32_t gx8002_image_b_stage1_flash_transaction_10000edc(
    uint32_t command, uint8_t *destination, uint32_t bytes);
extern void gx8002_image_b_stage1_flash_read_chunk_1000105a(
    uint32_t source_offset, uint8_t *destination, uint32_t bytes);

uint32_t gx8002_image_b_stage1_flash_read_10000fdc(
    uint32_t source_offset, void *destination, uint32_t bytes)
{
    uint8_t *cursor = destination;
    gx8002_image_b_stage1_clock_gate_100001f8(13u, 1u);
    if (gx8002_stage1_flash_jedec !=
        UINT32_C(0x00ffffff))
        gx8002_image_b_stage1_flash_initialize_100010e2();
    uint8_t status;
    do {
        (void)gx8002_image_b_stage1_flash_transaction_10000edc(
            5u, &status, 1u);
    } while ((status & 1u) != 0u);
    while (bytes != 0u) {
        uint32_t take = bytes < UINT32_C(0x10000) ? bytes : UINT32_C(0x10000);
        gx8002_image_b_stage1_flash_read_chunk_1000105a(source_offset,
                                                           cursor, take);
        source_offset += take;
        cursor += take;
        bytes -= take;
    }
    gx8002_image_b_stage1_clock_gate_100001f8(13u, 0u);
    return 0u;
}
