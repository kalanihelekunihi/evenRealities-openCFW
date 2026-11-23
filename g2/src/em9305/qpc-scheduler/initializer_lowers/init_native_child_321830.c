#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x321830..0x32195a: handle a periodic-sync AUX_SYNC/legacy report
 * for a sync record (+0x24, session +0x2c). Clears session +150; needs the
 * sync to be listening (+777) on a channel enabled in its map (native
 * 0x3027f4 over the map at *(+780)). Builds an 88-byte sync-established
 * message: record index (784-byte records from ((uintptr_t)&em9305_ram_803d58 + 0x20u)), parsed header
 * (native 0x32db0c) and copied advertiser data (native 0x32dd54). Only a
 * report from the expected advertiser (((uintptr_t)&em9305_ram_805af0 + 0x50u)/((uintptr_t)&em9305_ram_805af0 + 0x54u)) whose address is
 * not already synced (native 0x318200) is kept: the addresses are stored in
 * the record (+740..+752) and message, timing/PHY fields are filled from the
 * session and ((uintptr_t)&em9305_ram_805af0 + 0x14u), the message goes to the handler at ((uintptr_t)&em9305_ram_805af0 + 0x28u) and the
 * session's receive window is armed (native 0x323b10). */
extern uint64_t opencfw_em9305_child_3027f4(uint32_t,uint32_t,uint32_t);
extern uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t);
extern uint32_t opencfw_em9305_child_32db0c(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_init_transition_packet_copy_32dd54(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_ll_stream_address_busy_318200(uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_wsf_event_release(uintptr_t);
extern uint32_t opencfw_em9305_radio_duration_piece_312b88(uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_wsf_task_message_send(uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_child_323b10(uintptr_t,uintptr_t,uint32_t);

struct sync_header {
    uint8_t type;
    uint8_t reserved;
    uint8_t address_type;
    uint8_t random_type;
} __attribute__((aligned(4)));

void opencfw_em9305_child_321830(uintptr_t context, uintptr_t pdu)
{
    struct sync_header header;
    uintptr_t record = *(volatile uint32_t *)(context + 0x24u);
    uintptr_t session = *(volatile uint32_t *)(context + 0x2cu);
    uint32_t listening = *(volatile uint8_t *)(record + 777u);
    *(volatile uint8_t *)(session + 150u) = 0u;
    if (listening == 0u) return;
    uintptr_t map = *(volatile uint32_t *)(record + 780u);
    uint64_t used = opencfw_em9305_child_3027f4(*(volatile uint32_t *)(map + 8u),
                                                *(volatile uint32_t *)(map + 12u),
                                                *(volatile uint8_t *)(map + 0x12u));
    if (((uint32_t)used & 1u) == 0u) return;
    uintptr_t message = opencfw_em9305_wsf_event_allocate(0x58u);
    if (message == 0u) return;
    uint8_t index = (uint8_t)((int32_t)(record - ((uintptr_t)&em9305_ram_803d58 + 0x20u)) / 784);
    *(volatile uint8_t *)(message + 2u) = 0u;
    *(volatile uint16_t *)message = index;
    uint32_t used_bytes = opencfw_em9305_child_32db0c((uintptr_t)&header, pdu);
    (void)opencfw_em9305_init_transition_packet_copy_32dd54(message + 4u, pdu + used_bytes);
    uint32_t high = *(volatile uint32_t *)(message + 0x10u);
    uint32_t low = *(volatile uint32_t *)(message + 0xcu);
    if (em9305_ram_805af0.u32_805b44 != high ||
        em9305_ram_805af0.u32_805b40 != low) {
        (void)opencfw_em9305_wsf_event_release(message);
        return;
    }
    uint32_t address_type = header.random_type;
    uint32_t random_type = header.address_type;
    uint32_t random_high = *(volatile uint32_t *)(message + 8u);
    uint32_t random_low = *(volatile uint32_t *)(message + 4u);
    *(volatile uint32_t *)(record + 740u) = low;
    *(volatile uint32_t *)(record + 744u) = (address_type << 16) | high;
    *(volatile uint32_t *)(message + 0x48u) = 0u;
    *(volatile uint32_t *)(message + 0x44u) = 0u;
    *(volatile uint8_t *)(message + 52u) = (uint8_t)random_type;
    *(volatile uint32_t *)(record + 748u) = random_low;
    *(volatile uint32_t *)(message + 0x40u) = random_high;
    *(volatile uint32_t *)(message + 0x3cu) = random_low;
    *(volatile uint32_t *)(record + 752u) = (random_type << 16) | random_high;
    if (opencfw_em9305_ll_stream_address_busy_318200(random_type, random_low, random_high) != 0u) {
        (void)opencfw_em9305_wsf_event_release(message);
        return;
    }
    uintptr_t channel_map = *(volatile uint32_t *)(record + 780u);
    uint32_t phy_options = *(volatile uint8_t *)(session + 139u);
    uint32_t offset = *(volatile uint32_t *)(session + 144u);
    *(volatile uint8_t *)(message + 54u) = *(volatile uint8_t *)(channel_map + 0x15u);
    offset += opencfw_em9305_radio_duration_piece_312b88(*(volatile uint8_t *)(session + 13u),
                                                         phy_options, 0x24u);
    uint32_t interval_low = em9305_ram_805af0.u32_805b04;
    *(volatile uint16_t *)(message + 0x38u) = 256u;
    uint32_t interval_high = em9305_ram_805af0.u32_805b08;
    *(volatile uint32_t *)(message + 0x4cu) = interval_low;
    uint32_t handler = em9305_ram_805af0.u8_805b18;
    *(volatile uint16_t *)(message + 86u) = index;
    *(volatile uint8_t *)(message + 84u) = 0xffu;
    *(volatile uint32_t *)(message + 0x30u) = offset;
    *(volatile uint32_t *)(message + 0x50u) = interval_high;
    *(volatile uint8_t *)(message + 55u) = 0u;
    *(volatile uint8_t *)(message + 53u) = 1u;
    (void)opencfw_em9305_wsf_task_message_send(handler, message);
    uintptr_t window = *(volatile uint32_t *)(record + 780u) + 0x16u;
    *(volatile uint8_t *)(session + 136u) = 1u;
    *(volatile uint32_t *)(session + 0x7cu) = (uint32_t)window;
    *(volatile uint16_t *)(session + 120u) = (uint16_t)opencfw_em9305_child_323b10(0u, window, 0u);
}
