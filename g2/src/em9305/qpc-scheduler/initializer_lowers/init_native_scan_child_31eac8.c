#include <stdint.h>

/* Native 0x31eac8..0x31ec3e: start the scanner. Clear the 240-byte scan
 * radio block (0x805070) and set up its descriptor (completion callback
 * 0x31ec40, owner 0x804fd8, kind 3/2, length 257, first advertising channel
 * from the channel mask 0x805b00, access address 0x8e89bed6, CRC init
 * 0x555555, TX power 0x805a9c); size the scan PDU buffers (0x57, 0x20 by PHY
 * mask 0x80501a), install the scan callbacks and allocate the receive (and
 * for active scanning the response) buffer. Pick the own address (random
 * 0x805a8c when 0x805019 bit 0, else public 0x805b40), set the address
 * flags (bit 0, 0x51 with privacy 0x805a9d) and for active scanning prepare
 * the SCAN_REQ (native 0x3243c0). Finally schedule the first window (now +
 * 1228, interval 0x805016 * 625 us) via native 0x313220; returns the
 * resulting anchor stored at 0x805010. */
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
    const uintptr_t node = 0x805070u;
    (void)opencfw_em9305_memset((void *)node, 0u, 0xf0u);
    uint32_t channels = SCAN_U8(0x805b00u);
    uint32_t complete = (uint32_t)(uintptr_t)opencfw_em9305_scan_callback_31ec40;
    SCAN_U32(0x805090u) = complete;
    SCAN_U32(0x80508cu) = complete;
    SCAN_U32(0x80509cu) = 0x8050a0u;
    SCAN_U8(0x805088u) = 3u;
    SCAN_U32(0x805094u) = 0x804fd8u;
    SCAN_U8(0x8050a0u) = 2u;
    SCAN_U16(0x80508au) = 257u;
    uint32_t channel = opencfw_em9305_init_channel_first_325708(channels);
    uint32_t phys = SCAN_U8(0x80501au);
    SCAN_U32(0x8050a8u) = 0x555555u;
    uint32_t power = SCAN_U8(0x805a9cu);
    SCAN_U8(0x8050a1u) = (uint8_t)channel;
    SCAN_U16(0x8050acu) = 257u;
    SCAN_U16(0x8050ecu) = 0x57u;
    SCAN_U32(0x8050a4u) = 0x8e89bed6u;
    SCAN_U8(0x8050a2u) = (uint8_t)power;
    if ((phys & 1u) != 0u) SCAN_U16(0x8050eeu) = 0x57u;
    if ((phys & 2u) != 0u) SCAN_U32(0x8050f0u) = 0x20u;
    SCAN_U8(0x805136u) = 0x2du;
    SCAN_U32(0x805120u) = (uint32_t)(uintptr_t)opencfw_em9305_scan_callback_322910;
    SCAN_U32(0x80511cu) = (uint32_t)(uintptr_t)opencfw_em9305_scan_callback_3228e4;
    SCAN_U32(0x805118u) = (uint32_t)(uintptr_t)opencfw_em9305_scan_callback_31e9f8;
    SCAN_U32(0x805114u) = (uint32_t)(uintptr_t)opencfw_em9305_scan_callback_31e940;
    SCAN_U8(0x805137u) = (uint8_t)channels;
    uintptr_t receive = opencfw_em9305_wsf_event_allocate(0x2du);
    uint32_t active = SCAN_U8(0x805018u);
    SCAN_U32(0x805104u) = (uint32_t)receive;
    if (active == 1u) SCAN_U32(0x80510cu) = (uint32_t)opencfw_em9305_wsf_event_allocate(0x2du);
    uint32_t low, high, flags;
    if ((SCAN_U8(0x805019u) & 1u) != 0u) {
        high = SCAN_U32(0x805a90u);
        low = SCAN_U32(0x805a8cu);
        flags = SCAN_U32(0x8050f0u);
        SCAN_U32(0x8050f8u) = high;
        SCAN_U32(0x8050f4u) = low;
        flags |= 2u;
    } else {
        high = SCAN_U32(0x805b44u);
        low = SCAN_U32(0x805b40u);
        flags = SCAN_U32(0x8050f0u);
        SCAN_U32(0x8050f8u) = high;
        SCAN_U32(0x8050f4u) = low;
    }
    uint32_t privacy = SCAN_U8(0x805a9du);
    uint32_t value = flags | 1u;
    SCAN_U32(0x8050f0u) = value;
    if (privacy != 0u) {
        value = flags | 81u;
        SCAN_U32(0x8050f0u) = value;
    }
    if (SCAN_U8(0x805018u) == 1u) {
        SCAN_U8(0x805162u) = (uint8_t)((value >> 1) & 1u);
        SCAN_U8(0x805164u) = 12u;
        SCAN_U8(0x805160u) = 3u;
        request[3] = 0u;
        request[2] = 0u;
        request[0] = low;
        request[1] = high;
        (void)opencfw_em9305_scan_prepare_3243c0(0x804fdau, (uintptr_t)request);
        SCAN_U8(0x805135u) = 14u;
        SCAN_U32(0x805108u) = 0x804fd8u;
    } else {
        SCAN_U32(0x805108u) = 0u;
    }
    SCAN_U8(0x805161u) = 0u;
    uint32_t now = opencfw_em9305_scan_current_303f80();
    uint32_t interval = SCAN_U16(0x805016u);
    SCAN_U32(0x80507cu) = now + 1228u;
    SCAN_U16(0x80506cu) = 0u;
    SCAN_U32(0x805080u) = interval * 625u;
    (void)opencfw_em9305_auxiliary_insert_313220(node);
    uint32_t anchor = SCAN_U32(0x805078u);
    SCAN_U32(0x805010u) = anchor;
    return anchor;
}
