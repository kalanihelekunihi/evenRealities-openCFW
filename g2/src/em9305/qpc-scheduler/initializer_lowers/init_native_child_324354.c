#include <stdint.h>

/* Native 0x324354..0x3243ba: write an advertising PDU into the output buffer:
 * encoded header (type 4, length = data length +1717 plus 6, flag set for
 * mode 1/3, or mode 2 with address bits 15:14 == 01), the 6-byte address from
 * +0x10/+0x14, then up to 31 data bytes from +1718. Returns length + 2. */
extern uint32_t opencfw_em9305_radio_encode_3239d4(uintptr_t output,uintptr_t input);
extern uintptr_t opencfw_em9305_radio_address_write_3045e8(uintptr_t,uint32_t,uint32_t);
extern void *opencfw_em9305_memcpy(void *destination, const void *source, uint32_t bytes);

struct adv_header {
    uint8_t type;
    uint8_t reserved;
    uint8_t flag;
    uint8_t reserved2;
    uint8_t length;
} __attribute__((aligned(4)));

uint32_t opencfw_em9305_child_324354(uintptr_t record, uintptr_t output)
{
    struct adv_header header;
    uint32_t mode = *(volatile uint8_t *)(record + 57u);
    *(volatile uint32_t *)&header = 4u;
    if (mode == 3u || mode == 1u ||
        (mode == 2u && (*(volatile uint32_t *)(record + 0x14u) & 0xc000u) == 0x4000u))
        header.flag = 1u;
    header.length = (uint8_t)(*(volatile uint8_t *)(record + 1717u) + 6u);
    uintptr_t cursor = output + opencfw_em9305_radio_encode_3239d4(output, (uintptr_t)&header);
    (void)opencfw_em9305_radio_address_write_3045e8(cursor, *(volatile uint32_t *)(record + 0x10u),
                                                    *(volatile uint32_t *)(record + 0x14u));
    uint32_t length = *(volatile uint8_t *)(record + 1717u);
    if (length != 0u)
        (void)opencfw_em9305_memcpy((void *)(cursor + 6u), (const void *)(record + 1718u),
                                    length < 31u ? length : 31u);
    return (uint8_t)(header.length + 2u);
}
