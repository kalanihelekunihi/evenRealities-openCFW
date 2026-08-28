/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded Cordio application-database accessors matched to the stock
 * AppDbGetKey-style routine and adjacent peer-address helpers at
 * 0x0047AE78, 0x0047AEC0, and 0x0047AEC8.
 */

#define OPEN_CFW_MRAM_ACCESSOR_ADDRESS_TYPE_OFFSET 0x06U
#define OPEN_CFW_MRAM_ACCESSOR_IRK_OFFSET 0x07U
#define OPEN_CFW_MRAM_ACCESSOR_CSRK_OFFSET 0x1EU
#define OPEN_CFW_MRAM_ACCESSOR_KEY_MASK_OFFSET 0x2EU
#define OPEN_CFW_MRAM_ACCESSOR_LOCAL_LTK_OFFSET 0x34U
#define OPEN_CFW_MRAM_ACCESSOR_LOCAL_LEVEL_OFFSET 0x4EU
#define OPEN_CFW_MRAM_ACCESSOR_PEER_LTK_OFFSET 0x50U
#define OPEN_CFW_MRAM_ACCESSOR_PEER_LEVEL_OFFSET 0x6AU

#define OPEN_CFW_MRAM_ACCESSOR_LOCAL_LTK 0x01U
#define OPEN_CFW_MRAM_ACCESSOR_PEER_LTK 0x02U
#define OPEN_CFW_MRAM_ACCESSOR_IRK 0x04U
#define OPEN_CFW_MRAM_ACCESSOR_CSRK 0x08U

__attribute__((used, noinline))
unsigned char *open_cfw_mram_get_key(
    volatile unsigned char *record,
    unsigned int requested_type,
    volatile unsigned char *security_level
)
{
    unsigned int key_type = (unsigned char)requested_type;

    if (
        (record[OPEN_CFW_MRAM_ACCESSOR_KEY_MASK_OFFSET]
            & key_type) == 0U
    ) {
        return (unsigned char *)0;
    }

    switch (key_type) {
    case OPEN_CFW_MRAM_ACCESSOR_LOCAL_LTK:
        *security_level =
            record[OPEN_CFW_MRAM_ACCESSOR_LOCAL_LEVEL_OFFSET];
        return (unsigned char *)(
            record + OPEN_CFW_MRAM_ACCESSOR_LOCAL_LTK_OFFSET
        );
    case OPEN_CFW_MRAM_ACCESSOR_PEER_LTK:
        *security_level =
            record[OPEN_CFW_MRAM_ACCESSOR_PEER_LEVEL_OFFSET];
        return (unsigned char *)(
            record + OPEN_CFW_MRAM_ACCESSOR_PEER_LTK_OFFSET
        );
    case OPEN_CFW_MRAM_ACCESSOR_IRK:
        return (unsigned char *)(
            record + OPEN_CFW_MRAM_ACCESSOR_IRK_OFFSET
        );
    case OPEN_CFW_MRAM_ACCESSOR_CSRK:
        return (unsigned char *)(
            record + OPEN_CFW_MRAM_ACCESSOR_CSRK_OFFSET
        );
    default:
        return (unsigned char *)0;
    }
}

__attribute__((used, noinline))
unsigned char *open_cfw_mram_get_peer_address(
    volatile unsigned char *record
)
{
    if (record == (volatile unsigned char *)0) {
        return (unsigned char *)0;
    }
    return (unsigned char *)record;
}

__attribute__((used, noinline))
unsigned int open_cfw_mram_get_peer_address_type(
    volatile unsigned char *record
)
{
    if (record == (volatile unsigned char *)0) {
        return 0xFFU;
    }
    return record[OPEN_CFW_MRAM_ACCESSOR_ADDRESS_TYPE_OFFSET];
}
