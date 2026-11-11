/* SPDX-License-Identifier: MIT
 * BINH A stage-1 NOR loader at stock 0x10000a2c..0x10000aa8.
 * Locked stage-1 load SHA-256:
 * 65775a0feea148f5e1582693160c06204d5183fee717ba75706ce1cb4d40f605
 * The two read offsets, destinations, lengths, and entries below follow the
 * authenticated C-SKY disassembly and the recovered GX8002 scatter layout.
 */
#include <stdint.h>

extern uint32_t gx8002_image_a_stage1_flash_read_10000c40(
    uint32_t flash_offset, void *destination, uint32_t bytes);

struct gx8002_image_a_stage1_transfer {
    uint32_t flash_offset;
    uint32_t destination;
    uint32_t bytes;
    uint32_t entry;
};

static struct gx8002_image_a_stage1_transfer
gx8002_image_a_stage1_transfer_for(uint32_t package, uint32_t marker,
                                   uint32_t xip_bytes)
{
    if (marker == UINT32_C(0xaabbccdd)) {
        /* The second image's offset is absolute after the XIP-length read;
         * stock does not add the package boot address to this second read. */
        return (struct gx8002_image_a_stage1_transfer) {
            UINT32_C(0x323b4) + xip_bytes,
            UINT32_C(0x20003000), UINT32_C(0x1408c), UINT32_C(0x10003100)
        };
    }
    return (struct gx8002_image_a_stage1_transfer) {
        package + UINT32_C(0x3004) + xip_bytes,
        UINT32_C(0x10023400), UINT32_C(0x397c), UINT32_C(0x10023500)
    };
}

__attribute__((used, section(".spl_a.text")))
int32_t gx8002_image_a_stage1_loader_10000a2c(void)
{
    volatile uint32_t *const package_word =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x20001284);
    volatile uint32_t *const marker_word =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x20033ffc);
    volatile uint32_t *const entry_word =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002e938);
    uint32_t package = *package_word;
    uint32_t marker = *marker_word;
    uint32_t xip_bytes = 0;
    uint32_t length_word = package + (marker == UINT32_C(0xaabbccdd)
        ? UINT32_C(0x323b0) : UINT32_C(0x3000));

    (void)gx8002_image_a_stage1_flash_read_10000c40(
        length_word, &xip_bytes, 4u);
    struct gx8002_image_a_stage1_transfer transfer =
        gx8002_image_a_stage1_transfer_for(package, marker, xip_bytes);
    (void)gx8002_image_a_stage1_flash_read_10000c40(
        transfer.flash_offset,
        (void *)(uintptr_t)transfer.destination,
        transfer.bytes);
    *entry_word = transfer.entry;
    ((void (*)(void))(uintptr_t)transfer.entry)();
    return 0;
}
