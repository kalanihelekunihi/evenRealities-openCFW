#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x31e84c..0x31e8fa: decode a received PAwR response PDU. The
 * header (native 0x32db0c) must have length 6..37 and an accepted PDU type
 * (0, 1, 2, 4, 6 -> kinds 0, 1, 3, 4, 2); the report gets kind (+10), data
 * length (+8, 0 for type 1), data pointer (+4 = event +8) and channel (+9 =
 * event +39). After the address check (native 0x303404 with policy
 * (uintptr_t)&em9305_ram_8050ec) the report gets the address type (+11, bit 1 when resolved) and
 * address (+12), and *flag the check's flag byte. Returns the check result,
 * or 0 when rejected. */
extern uint32_t opencfw_em9305_dispatch_child_32db0c(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_radio_packet_check_303404(uintptr_t,uintptr_t,uint32_t,uintptr_t);
extern uintptr_t opencfw_em9305_radio_address_write_3045e8(uintptr_t,uint32_t,uint32_t);

struct pawr_header {
    uint8_t type;
    uint8_t reserved;
    uint16_t value;
    uint8_t length;
} __attribute__((aligned(4)));

struct pawr_check {
    uint32_t resolved[2];
    uint32_t address[2];
    uint8_t reserved[2];
    uint8_t type;
    uint8_t resolved_type;
    uint8_t reserved2;
    uint8_t flag;
} __attribute__((aligned(4)));

uint32_t opencfw_em9305_pawr_decode_31e84c(uintptr_t event, uintptr_t report, uintptr_t flag)
{
    struct pawr_check check;
    struct pawr_header header;
    uint32_t kind, data_length;
    (void)opencfw_em9305_dispatch_child_32db0c((uintptr_t)&header, event);
    uint32_t length = header.length;
    if ((uint8_t)(length - 0x26u) < 224u) return 0u;
    data_length = length - 6u;
    switch (header.type) {
    case 0u: kind = 0u; break;
    case 1u: kind = 1u; data_length = 0u; break;
    case 2u: kind = 3u; break;
    case 4u: kind = 4u; break;
    case 6u: kind = 2u; break;
    default: return 0u;
    }
    volatile uint8_t *out = (volatile uint8_t *)report;
    out[10] = (uint8_t)kind;
    out[8] = (uint8_t)data_length;
    *(volatile uint32_t *)(report + 4u) = (uint32_t)(event + 8u);
    out[9] = *(volatile uint8_t *)(event + 39u);
    uint32_t result = opencfw_em9305_radio_packet_check_303404(event, (uintptr_t)&em9305_ram_8050ec, 1u, (uintptr_t)&check);
    if (result == 0u) return 0u;
    uint32_t address_type = check.resolved_type;
    if (address_type != check.type ||
        ((check.resolved[0] ^ check.address[0]) | (check.resolved[1] ^ check.address[1])) != 0u)
        address_type |= 2u;
    out[11] = (uint8_t)address_type;
    (void)opencfw_em9305_radio_address_write_3045e8(report + 12u, check.address[0], check.address[1]);
    *(volatile uint8_t *)flag = check.flag;
    return result;
}
