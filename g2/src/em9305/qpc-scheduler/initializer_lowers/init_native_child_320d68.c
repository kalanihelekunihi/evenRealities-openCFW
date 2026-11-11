#include <stdint.h>

/* Native 0x320d68..0x320dda: handle a received control PDU for the link
 * (+0x24): parse its header (native 0x32db0c) and payload (native 0x32df24
 * into link +152), then schedule the response (native 0x30301c) with the
 * link's four timing words (+156..+168), the parsed type and length and the
 * channel byte +154, mark the link busy (+1) and signal the auxiliary task.
 * Always returns 0. */
extern uint32_t opencfw_em9305_dispatch_child_32db0c(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_dispatch_child_32df24(uintptr_t,uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_child_30301c(uintptr_t,uintptr_t,uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_auxiliary_signal_304394(void);

struct pdu_header {
    uint8_t type;
    uint8_t reserved;
    uint16_t length;
};

struct pdu_response {
    uint32_t timing[4];
    uint8_t type;
    uint8_t channel;
    uint16_t length;
};

uint32_t opencfw_em9305_child_320d68(uintptr_t context, uintptr_t pdu)
{
    struct pdu_header header;
    struct pdu_response response;
    uint8_t status;
    if (pdu == 0u) return 0u;
    uintptr_t link = *(volatile uint32_t *)(context + 0x24u);
    uintptr_t session = *(volatile uint32_t *)(context + 44u);
    uint32_t used = opencfw_em9305_dispatch_child_32db0c((uintptr_t)&header, pdu);
    (void)opencfw_em9305_dispatch_child_32df24(link + 152u, (uintptr_t)&status, pdu + used);
    volatile uint32_t *timing = (volatile uint32_t *)(link + 156u);
    response.type = header.type;
    response.length = header.length;
    response.timing[1] = timing[1];
    response.timing[3] = timing[3];
    response.timing[0] = timing[0];
    response.timing[2] = timing[2];
    response.channel = *(volatile uint8_t *)(link + 154u);
    (void)opencfw_em9305_child_30301c((uintptr_t)&response,
                                      *(volatile uint32_t *)(context + 44u) + 76u, 1u,
                                      session + 144u);
    *(volatile uint8_t *)(link + 1u) = 1u;
    (void)opencfw_em9305_auxiliary_signal_304394();
    return 0u;
}
