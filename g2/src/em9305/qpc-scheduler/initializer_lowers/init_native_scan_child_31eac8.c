#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x31eac8..0x31ec3e: start the scanner. Clear the 240-byte scan
 * radio block (((uintptr_t)&em9305_ram_80505c + 0x14u)) and set up its descriptor (completion callback
 * 0x31ec40, owner ((uintptr_t)&em9305_ram_803d58 + 0x1280u), kind 3/2, length 257, first advertising channel
 * from the channel mask ((uintptr_t)&em9305_ram_805af0 + 0x10u), access address 0x8e89bed6, CRC init
 * 0x555555, TX power ((uintptr_t)&em9305_ram_805a6c + 0x30u)); size the scan PDU buffers (0x57, 0x20 by PHY
 * mask ((uintptr_t)&em9305_ram_805010 + 0xau)), install the scan callbacks and allocate the receive (and
 * for active scanning the response) buffer. Pick the own address (random
 * ((uintptr_t)&em9305_ram_805a6c + 0x20u) when ((uintptr_t)&em9305_ram_805010 + 0x9u) bit 0, else public ((uintptr_t)&em9305_ram_805af0 + 0x50u)), set the address
 * flags (bit 0, 0x51 with privacy ((uintptr_t)&em9305_ram_805a6c + 0x31u)) and for active scanning prepare
 * the SCAN_REQ (native 0x3243c0). Finally schedule the first window (now +
 * 1228, interval ((uintptr_t)&em9305_ram_805010 + 0x6u) * 625 us) via native 0x313220; returns the
 * resulting anchor stored at (uintptr_t)&em9305_ram_805010. */
extern void *opencfw_em9305_memset(void *,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_init_channel_first_325708(uint32_t);
extern uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t);
extern uint32_t opencfw_em9305_scan_prepare_3243c0(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_scan_current_303f80(void);
extern uint32_t opencfw_em9305_auxiliary_insert_313220(uintptr_t);
extern uint32_t opencfw_em9305_scan_callback_31ec40(uintptr_t);
extern uint32_t opencfw_em9305_scan_callback_322910(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_scan_callback_3228e4(uint32_t);
extern uint32_t opencfw_em9305_scan_callback_31e9f8(void);
extern uint32_t opencfw_em9305_scan_callback_31e940(void);

#define SCAN_U8(a) (*(volatile uint8_t *)(uintptr_t)(a))
#define SCAN_U16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define SCAN_U32(a) (*(volatile uint32_t *)(uintptr_t)(a))

uint32_t opencfw_em9305_scan_start_31eac8(void)
{
    uint32_t request[4];
    const uintptr_t node = ((uintptr_t)&em9305_ram_80505c + 0x14u);
    (void)opencfw_em9305_memset((void *)node, 0u, 0xf0u);
    uint32_t channels = SCAN_U8(((uintptr_t)&em9305_ram_805af0 + 0x10u));
    uint32_t complete = (uint32_t)(uintptr_t)opencfw_em9305_scan_callback_31ec40;
    SCAN_U32(((uintptr_t)&em9305_ram_80505c + 0x34u)) = complete;
    SCAN_U32(((uintptr_t)&em9305_ram_80505c + 0x30u)) = complete;
    SCAN_U32(((uintptr_t)&em9305_ram_80505c + 0x40u)) = ((uintptr_t)&em9305_ram_80505c + 0x44u);
    SCAN_U8(((uintptr_t)&em9305_ram_80505c + 0x2cu)) = 3u;
    SCAN_U32(((uintptr_t)&em9305_ram_80505c + 0x38u)) = ((uintptr_t)&em9305_ram_803d58 + 0x1280u);
    SCAN_U8(((uintptr_t)&em9305_ram_80505c + 0x44u)) = 2u;
    SCAN_U16(((uintptr_t)&em9305_ram_80505c + 0x2eu)) = 257u;
    uint32_t channel = opencfw_em9305_init_channel_first_325708(channels);
    uint32_t phys = SCAN_U8(((uintptr_t)&em9305_ram_805010 + 0xau));
    SCAN_U32(((uintptr_t)&em9305_ram_80505c + 0x4cu)) = 0x555555u;
    uint32_t power = SCAN_U8(((uintptr_t)&em9305_ram_805a6c + 0x30u));
    SCAN_U8(((uintptr_t)&em9305_ram_80505c + 0x45u)) = (uint8_t)channel;
    SCAN_U16(((uintptr_t)&em9305_ram_80505c + 0x50u)) = 257u;
    SCAN_U16((uintptr_t)&em9305_ram_8050ec) = 0x57u;
    SCAN_U32(((uintptr_t)&em9305_ram_80505c + 0x48u)) = 0x8e89bed6u;
    SCAN_U8(((uintptr_t)&em9305_ram_80505c + 0x46u)) = (uint8_t)power;
    if ((phys & 1u) != 0u) SCAN_U16(((uintptr_t)&em9305_ram_8050ec + 0x2u)) = 0x57u;
    if ((phys & 2u) != 0u) SCAN_U32(((uintptr_t)&em9305_ram_8050ec + 0x4u)) = 0x20u;
    SCAN_U8(((uintptr_t)&em9305_ram_805134 + 0x2u)) = 0x2du;
    SCAN_U32(((uintptr_t)&em9305_ram_8050ec + 0x34u)) = (uint32_t)(uintptr_t)opencfw_em9305_scan_callback_322910;
    SCAN_U32(((uintptr_t)&em9305_ram_8050ec + 0x30u)) = (uint32_t)(uintptr_t)opencfw_em9305_scan_callback_3228e4;
    SCAN_U32(((uintptr_t)&em9305_ram_8050ec + 0x2cu)) = (uint32_t)(uintptr_t)opencfw_em9305_scan_callback_31e9f8;
    SCAN_U32(((uintptr_t)&em9305_ram_8050ec + 0x28u)) = (uint32_t)(uintptr_t)opencfw_em9305_scan_callback_31e940;
    SCAN_U8(((uintptr_t)&em9305_ram_805134 + 0x3u)) = (uint8_t)channels;
    uintptr_t receive = opencfw_em9305_wsf_event_allocate(0x2du);
    uint32_t active = SCAN_U8(((uintptr_t)&em9305_ram_805010 + 0x8u));
    SCAN_U32(((uintptr_t)&em9305_ram_8050ec + 0x18u)) = (uint32_t)receive;
    if (active == 1u) SCAN_U32(((uintptr_t)&em9305_ram_8050ec + 0x20u)) = (uint32_t)opencfw_em9305_wsf_event_allocate(0x2du);
    uint32_t low, high, flags;
    if ((SCAN_U8(((uintptr_t)&em9305_ram_805010 + 0x9u)) & 1u) != 0u) {
        high = SCAN_U32(((uintptr_t)&em9305_ram_805a6c + 0x24u));
        low = SCAN_U32(((uintptr_t)&em9305_ram_805a6c + 0x20u));
        flags = SCAN_U32(((uintptr_t)&em9305_ram_8050ec + 0x4u));
        SCAN_U32(((uintptr_t)&em9305_ram_8050ec + 0xcu)) = high;
        SCAN_U32(((uintptr_t)&em9305_ram_8050ec + 0x8u)) = low;
        flags |= 2u;
    } else {
        high = SCAN_U32(((uintptr_t)&em9305_ram_805af0 + 0x54u));
        low = SCAN_U32(((uintptr_t)&em9305_ram_805af0 + 0x50u));
        flags = SCAN_U32(((uintptr_t)&em9305_ram_8050ec + 0x4u));
        SCAN_U32(((uintptr_t)&em9305_ram_8050ec + 0xcu)) = high;
        SCAN_U32(((uintptr_t)&em9305_ram_8050ec + 0x8u)) = low;
    }
    uint32_t privacy = SCAN_U8(((uintptr_t)&em9305_ram_805a6c + 0x31u));
    uint32_t value = flags | 1u;
    SCAN_U32(((uintptr_t)&em9305_ram_8050ec + 0x4u)) = value;
    if (privacy != 0u) {
        value = flags | 81u;
        SCAN_U32(((uintptr_t)&em9305_ram_8050ec + 0x4u)) = value;
    }
    if (SCAN_U8(((uintptr_t)&em9305_ram_805010 + 0x8u)) == 1u) {
        SCAN_U8(((uintptr_t)&em9305_ram_805160 + 0x2u)) = (uint8_t)((value >> 1) & 1u);
        SCAN_U8(((uintptr_t)&em9305_ram_805160 + 0x4u)) = 12u;
        SCAN_U8((uintptr_t)&em9305_ram_805160) = 3u;
        request[3] = 0u;
        request[2] = 0u;
        request[0] = low;
        request[1] = high;
        (void)opencfw_em9305_scan_prepare_3243c0(((uintptr_t)&em9305_ram_803d58 + 0x1282u), (uintptr_t)request);
        SCAN_U8(((uintptr_t)&em9305_ram_805134 + 0x1u)) = 14u;
        SCAN_U32(((uintptr_t)&em9305_ram_8050ec + 0x1cu)) = ((uintptr_t)&em9305_ram_803d58 + 0x1280u);
    } else {
        SCAN_U32(((uintptr_t)&em9305_ram_8050ec + 0x1cu)) = 0u;
    }
    SCAN_U8(((uintptr_t)&em9305_ram_805160 + 0x1u)) = 0u;
    uint32_t now = opencfw_em9305_scan_current_303f80();
    uint32_t interval = SCAN_U16(((uintptr_t)&em9305_ram_805010 + 0x6u));
    SCAN_U32(((uintptr_t)&em9305_ram_80505c + 0x20u)) = now + 1228u;
    SCAN_U16(((uintptr_t)&em9305_ram_80505c + 0x10u)) = 0u;
    SCAN_U32(((uintptr_t)&em9305_ram_80505c + 0x24u)) = interval * 625u;
    (void)opencfw_em9305_auxiliary_insert_313220(node);
    uint32_t anchor = SCAN_U32(((uintptr_t)&em9305_ram_80505c + 0x1cu));
    SCAN_U32((uintptr_t)&em9305_ram_805010) = anchor;
    return anchor;
}
