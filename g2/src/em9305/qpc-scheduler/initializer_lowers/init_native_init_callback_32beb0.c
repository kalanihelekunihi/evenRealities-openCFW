#include <stdint.h>

/* Native 0x32beb0..0x32bfc2: handle a received sync-related control PDU.
 * Without an established sync (session +260 clear) the PDU payload is parsed
 * into the receive state at 0x8056cc (native 0x32df24) and the remaining
 * counter (+8) derived from the PDU byte 1 and the expected count. With a
 * sync, a missing PDU reports status 0x3e; otherwise the PDU header and the
 * two addresses are parsed (natives 0x32db0c, 0x32db54): a matching
 * 12-byte address pair produces a 20-byte message 787 to the handler at
 * 0x805b18, a mismatch reports status 0x42. Reports go through native
 * 0x316908 and finish with native 0x325eb4; both PDU paths then call the
 * session's completion hook (+172) on its node (+208). Returns 1, or 0 for
 * an unsynced call without a PDU. */
extern uint32_t opencfw_em9305_dispatch_child_32db0c(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_dispatch_child_32db54(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_dispatch_child_32df24(uintptr_t,uintptr_t,uintptr_t);
extern uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t);
extern uint32_t opencfw_em9305_wsf_task_message_send(uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_init_transition_report_316908(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_init_transition_finish_325eb4(uintptr_t,uint32_t);

struct sync_pdu_header {
    uint8_t type;
    uint8_t reserved;
    uint16_t length;
};

static void opencfw_em9305_init_callback_32beb0_report(uintptr_t record, uint32_t status)
{
    uintptr_t sync = *(volatile uint32_t *)(record + 0xafcu);
    uint32_t peer_high = *(volatile uint32_t *)(sync + 72u);
    uint32_t peer_low = *(volatile uint32_t *)(sync + 0x44u);
    uint32_t peer_type = *(volatile uint8_t *)(sync + 66u);
    (void)opencfw_em9305_init_transition_report_316908(*(volatile uint8_t *)(record + 1u), status,
                                                       peer_type, peer_low, peer_high);
    (void)opencfw_em9305_init_transition_finish_325eb4(record, 2u);
}

uint32_t opencfw_em9305_init_callback_32beb0(uintptr_t context, uintptr_t pdu)
{
    uintptr_t session = *(volatile uint32_t *)(context + 0x2cu);
    uintptr_t record = *(volatile uint32_t *)(context + 0x24u);
    if (*(volatile uint8_t *)(session + 260u) == 0u) {
        if (pdu == 0u) return 0u;
        volatile uint32_t *slot = (volatile uint32_t *)(record + 0xafcu);
        uint32_t count = *(volatile uint8_t *)(pdu + 1u);
        uint32_t used = opencfw_em9305_dispatch_child_32df24(*slot + 4u, 0x8056ccu, pdu + 2u);
        uintptr_t sync = *slot;
        *(volatile uint32_t *)(uintptr_t)0x8056d0u = (uint32_t)(used + pdu + 2u);
        *(volatile uint8_t *)(uintptr_t)0x8056d4u =
            (uint8_t)(count + ~(uint32_t)*(volatile uint8_t *)(sync + 4u));
        return 1u;
    }
    if (pdu == 0u) {
        opencfw_em9305_init_callback_32beb0_report(record, 0x3eu);
        return 1u;
    }
    struct sync_pdu_header header;
    uint32_t address[4];
    uint32_t used = opencfw_em9305_dispatch_child_32db0c((uintptr_t)&header, pdu);
    uint32_t length = opencfw_em9305_dispatch_child_32db54((uintptr_t)address, pdu + used + 2u);
    uintptr_t sync = *(volatile uint32_t *)(record + 0xafcu);
    if (length == 12u && *(volatile uint32_t *)(sync + 0x70u) == address[1] &&
        *(volatile uint32_t *)(sync + 0x6cu) == address[0]) {
        uintptr_t message = opencfw_em9305_wsf_event_allocate(0x14u);
        if (message != 0u) {
            *(volatile uint16_t *)(message + 2u) = 787u;
            *(volatile uint32_t *)(message + 0xcu) = address[1];
            *(volatile uint32_t *)(message + 8u) = address[0];
            *(volatile uint16_t *)message = *(volatile uint8_t *)(record + 1u);
            sync = *(volatile uint32_t *)(record + 0xafcu);
            *(volatile uint8_t *)(message + 5u) = *(volatile uint8_t *)(sync + 65u);
            *(volatile uint8_t *)(message + 6u) = *(volatile uint8_t *)(sync + 66u);
            (void)opencfw_em9305_wsf_task_message_send(*(volatile uint8_t *)(uintptr_t)0x805b18u, message);
        }
    } else {
        opencfw_em9305_init_callback_32beb0_report(record, 0x42u);
    }
    uintptr_t hook = *(volatile uint32_t *)(session + 172u);
    ((void (*)(uintptr_t, uintptr_t))hook)(session + 208u, hook);
    return 1u;
}
