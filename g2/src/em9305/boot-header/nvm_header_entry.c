/* SPDX-License-Identifier: MIT
 * G2 EM9305 user-application header and first NVM instruction sequence.
 *
 * The EM9305 SDK firmwareHeaderV0_t layout (v4.6) matches the authenticated
 * 2.2.6.10 header at 0x302000. Its 40-byte header is followed by a 10-byte
 * NVM_Entry at 0x302028 and six erased bytes. The vendor's external image
 * step fills firmwareSize, firmwareCRC and headerCRC after the final link.
 *
 * ARC has no C operation for replacing SP before entering a C function, so
 * the two entry instructions are expressed as inline assembly in this C
 * translation unit. They set the stock stack top and branch to the existing
 * source-owned NVM boot loop. No stock machine-code bytes are embedded.
 */
#include <stddef.h>
#include <stdint.h>

extern void opencfw_em9305_stock_30ed80(void);
extern void NVM_Entry(void);

/* This is the exact two-instruction control-flow shape of the stock entry.
 * Defining the symbol at file scope prevents a compiler epilogue/NOP from
 * entering the ten-byte NVM record. */
__asm__(
    ".section .nvm_entry,\"ax\",@progbits\n"
    ".global NVM_Entry\n"
    ".type NVM_Entry,@function\n"
    "NVM_Entry:\n"
    "mov_s sp, 0x80f978\n"
    "b opencfw_em9305_stock_30ed80\n"
    ".size NVM_Entry, .-NVM_Entry\n"
    ".previous\n");

struct __attribute__((packed, aligned(4))) g2_em_firmware_header {
    uint32_t magic;
    uint8_t version;
    uint8_t length;
    uint8_t section_code;
    uint8_t reserved;
    uint32_t firmware_start;
    uint32_t firmware_size;
    uint32_t firmware_crc;
    uint32_t emcore_crc;
    uint32_t options;
    uint16_t firmware_version;
    void (*execution)(void);
    uint32_t header_crc;
    uint16_t alignment;
};

_Static_assert(sizeof(struct g2_em_firmware_header) == 40, "EM9305 header length");
_Static_assert(offsetof(struct g2_em_firmware_header, firmware_crc) == 16, "firmware CRC field");
_Static_assert(offsetof(struct g2_em_firmware_header, execution) == 30, "execution field");
_Static_assert(offsetof(struct g2_em_firmware_header, header_crc) == 34, "header CRC field");

const struct g2_em_firmware_header __attribute__((used, section(".programHeader")))
g2_em_program_header = {
    .magic = UINT32_C(0x52444846), /* 'FHDR' in little-endian flash */
    .version = 0,
    .length = 40,
    .section_code = 3, /* user application */
    .firmware_start = UINT32_C(0x00302028),
    .firmware_size = UINT32_MAX,
    .firmware_crc = UINT32_MAX,
    .emcore_crc = UINT32_MAX,
    .options = 0,
    .firmware_version = 0,
    .execution = NVM_Entry,
    .header_crc = UINT32_MAX,
};
