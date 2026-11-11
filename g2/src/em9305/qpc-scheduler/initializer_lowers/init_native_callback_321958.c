#include <stdint.h>

/* Native 0x321958..0x321c30: periodic-sync receive callback (owner, pdu,
 * status). Records the status (+44) and the channel index in the report
 * buffer. Decodes the extended header (32df24) into 0x803b68: data
 * pointer (+4), data length (+8) and header flags (+10). An AUX_SYNC
 * report (type 7) on a listening, mapped channel consumes it from the
 * pending channel map, copies the AD data, runs the 0x805c9c report hook
 * and computes the anchor offset; a first sync arms the record (+5,
 * 325d50/326108) or reports a filtered-out sync (reason 2). It then
 * stores the first AUX pointer (0x803d70), forwards a pending sync-lost
 * event (+408, task 0x805b18), and for a header with an AuxPtr computes
 * the next window (+108) and returns its offset. Type 5 goes to 321830. */
#define U8(a) (*(volatile uint8_t *)(uintptr_t)(a))
#define U16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define U32(a) (*(volatile uint32_t *)(uintptr_t)(a))

extern uint32_t opencfw_em9305_dispatch_child_32df24(uintptr_t out, uintptr_t flags_out,
                                                     uintptr_t in);
extern void opencfw_em9305_child_321830(uintptr_t context, uintptr_t pdu);
extern void *opencfw_em9305_memcpy(void *destination, const void *source, uint32_t bytes);
extern void opencfw_em9305_child_31c530(uintptr_t record);
extern uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t length);
extern uint32_t opencfw_em9305_wsf_task_message_send(uint32_t task, uintptr_t message);
extern void opencfw_em9305_child_32db74(uintptr_t out, uintptr_t packed);
extern uint32_t opencfw_em9305_init_secondary_current_303f5c(void);
extern uint32_t opencfw_em9305_init_secondary_time_317ebc(uint32_t, uint32_t);
extern uint32_t opencfw_em9305_init_secondary_message_325d50(uintptr_t record, uint32_t reason);
extern uint32_t opencfw_em9305_child_326108(uintptr_t record, uint32_t value);

#define EXT_HEADER 0x803b68u /* +4 data, +8 data length, +10 header flags */
#define AUX_POINTER 0x803d70u
#define SCAN_FILTER 0x8051a4u

uint32_t opencfw_em9305_callback_321958(uintptr_t owner, uintptr_t pdu, uint32_t status)
{
    uintptr_t link = U32(owner + 36u);
    uint32_t listening = U8(link + 777u);
    uintptr_t session = U32(owner + 44u);
    U8(link + 44u) = (uint8_t)status;
    if (listening != 0u)
        U8(U32(link + 780u) + 21u) = U8(session + 13u);
    if (pdu == 0u)
        return 0u;

    uint32_t type = U8(pdu) & 0xfu;
    uint32_t length = U8(pdu + 1u);
    U8(session + 136u) = 0u;
    uint32_t used = opencfw_em9305_dispatch_child_32df24(link + 736u, EXT_HEADER + 10u, pdu + 2u);
    U32(EXT_HEADER + 4u) = used + pdu + 2u;
    U8(EXT_HEADER + 8u) = (uint8_t)(length - U8(link + 736u) - 1u);
    if (type == 5u) {
        opencfw_em9305_child_321830(owner, pdu);
        return 0u;
    }
    if (type != 7u)
        return 0u;

    link = U32(owner + 36u);
    session = U32(owner + 44u);
    uintptr_t sync = link + 616u;
    if (U8(link + 777u) != 0u) {
        uintptr_t report = U32(link + 780u);
        uint32_t event_counter = U16(link + 248u);
        U8(session + 150u) = 1u;
        uint32_t channel = U8(report + 18u);
        U16(report + 16u) = (uint16_t)event_counter;
        U8(report + 19u) = (uint8_t)channel;
        U8(report + 20u) = U8(U32(owner + 44u) + 1u);
    }
    if (U8(link + 5u) == 0u) {
        U8(AUX_POINTER) = 1u;
        uint32_t filter = U8(SCAN_FILTER + 16u);
        if (filter != 0u &&
            ((U8(sync + 122u) & 4u) != 0u ? ((filter >> (U8(sync + 141u) & 31u)) & 1u) != 0u
                                          : (filter & 0x10u) != 0u)) {
            U8(U32(SCAN_FILTER + 20u) + 603u) = 1u;
            (void)opencfw_em9305_init_secondary_message_325d50(link, 2u);
            return 0u;
        }
        U8(link + 5u) = 1u;
        (void)opencfw_em9305_init_secondary_message_325d50(link, 4u);
        (void)opencfw_em9305_child_326108(link, 1u);
        if (U8(0x8051c0u) == 1u)
            U32(link + 260u) = U32(link + 252u) * U16(sync);
    }

    uintptr_t window = session + 128u;
    if (U8(link + 777u) != 0u && U8(link + 5u) != 0u) {
        uintptr_t report = U32(link + 780u);
        uint64_t bit = (uint64_t)1u << (U8(report + 18u) & 63u);
        uint32_t map_low = U32(report), map_high = U32(report + 4u);
        if (((uint32_t)bit & map_low) == 0u && ((uint32_t)(bit >> 32) & map_high) == 0u) {
            U32(session + 112u) = 0u;
        } else {
            uint32_t size = U8(report + 109u);
            uintptr_t data = U32(report + 92u);
            U32(report) = map_low & ~(uint32_t)bit;
            U32(report + 4u) = map_high & ~(uint32_t)(bit >> 32);
            U16(report + 98u) = 0u;
            U16(report + 88u) = (uint16_t)size;
            (void)opencfw_em9305_memcpy((void *)data, (const void *)(report + 112u), size);
            report = U32(link + 780u);
            uintptr_t hook = U32(0x805c9cu);
            U32(session + 124u) = report + 22u;
            U16(session + 120u) = (uint16_t)((uint32_t (*)(uint32_t, uintptr_t, uintptr_t, uint32_t))hook)(
                U16(report + 366u), report + 22u, report + 88u, 0u);
            report = U32(link + 780u);
            uint32_t offset = U8(report + 18u);
            uint32_t pointer = U32(report + 92u);
            U32(window + 4u) = pointer;
            U16(window) = U16(report + 98u);
            uint32_t sca = U8(report + offset + 368u);
            U32(session + 112u) = U8(sync - 101u) * sca * 125u + U8(sync - 102u) * 1250u;
        }
    }

    if (U8(AUX_POINTER + 1u) == 0u && status == 0u && U8(window + 20u) != 0u) {
        uint32_t anchor = U32(window + 16u);
        U8(AUX_POINTER + 1u) = 1u;
        U32(AUX_POINTER + 4u) = anchor;
    }
    opencfw_em9305_child_31c530(link);
    uintptr_t lost = link + 408u;
    if (U8(lost) == 1u) {
        uint32_t unit = U8(sync - 196u) == 0u ? 30u : 300u;
        U32(link + 412u) = unit * U16(link + 418u) + U32(window + 16u);
        U8(link + 416u) = U8(link + 256u);
        uintptr_t message = opencfw_em9305_wsf_event_allocate(0x64u);
        if (message != 0u) {
            U32(message) = 0x3110000u;
            (void)opencfw_em9305_memcpy((void *)(message + 4u), (const void *)lost, 0x60u);
            (void)opencfw_em9305_wsf_task_message_send(U8(0x805b18u), message);
        }
    }

    uint32_t flags = U8(EXT_HEADER + 10u);
    if (U8(link + 7u) != 0u && (flags & 8u) != 0u) {
        uint32_t expected = U16(sync + 142u);
        uint32_t index = U8(sync + 161u) != 0u ? U8(U32(link + 780u) + 18u) & 0x7fu : 0u;
        if (expected == U16(link + index * 2u + 280u))
            return 0u;
    }
    if ((flags & 0x10u) == 0u)
        return 0u;

    uint8_t aux[8] __attribute__((aligned(4)));
    opencfw_em9305_child_32db74((uintptr_t)aux, U32(link + 768u));
    uint32_t offset = (uint32_t)*(volatile uint16_t *)(aux + 4) *
                      (((volatile uint8_t *)aux)[2] == 0u ? 30u : 300u);
    U8(session + 1u) = ((volatile uint8_t *)aux)[0];
    uint32_t now = opencfw_em9305_init_secondary_current_303f5c();
    uint32_t unit = ((volatile uint8_t *)aux)[2] == 0u ? 30u : 300u;
    uint32_t accuracy = ((volatile uint8_t *)aux)[1] == 1u ? 50u : 500u;
    uint32_t widening = opencfw_em9305_init_secondary_time_317ebc(unit + offset, now + accuracy);
    unit = ((volatile uint8_t *)aux)[2] == 0u ? 30u : 300u;
    U32(session + 108u) = unit + (widening << 1);
    return offset - widening;
}
