#include <stdint.h>

/* Native 0x32bdfc..0x32be78: decode the received PDU header into
 * 0x8019fc; for LLID 3 with control opcode 12 parse the payload into
 * 0x801a04 (32e144), then build the 20-byte request {four parsed words,
 * LLID, 3, header halfword} and hand it to 30301c with the context's
 * +76 and the link's +184. Returns 1 only when that succeeds and the
 * link byte +204 is set. */
extern uint32_t opencfw_em9305_child_32db0c(uintptr_t out, uintptr_t in);
extern uint32_t opencfw_em9305_child_32e144(uintptr_t out, uintptr_t payload);
extern uint32_t opencfw_em9305_child_30301c(uintptr_t request, uintptr_t context,
                                            uint32_t flags, uintptr_t link);

struct opencfw_em9305_request_32bdfc {
    uint32_t words[4];
    uint8_t llid;
    uint8_t kind;
    uint16_t header;
};

uint32_t opencfw_em9305_child_32bdfc(uintptr_t record, uintptr_t pdu)
{
    struct opencfw_em9305_request_32bdfc request;
    uintptr_t link=*(volatile uint32_t *)(record+44u);
    (void)opencfw_em9305_child_32db0c(0x8019fcu,pdu);
    if(*(volatile uint8_t *)(uintptr_t)0x8019fcu!=3u)return 0u;
    if(*(volatile uint8_t *)(uintptr_t)0x801a00u!=12u)return 0u;
    (void)opencfw_em9305_child_32e144(0x801a04u,pdu+2u);
    volatile const uint32_t *parsed=(volatile const uint32_t *)(uintptr_t)0x801a04u;
    request.words[2]=parsed[2];
    request.llid=*(volatile uint8_t *)(uintptr_t)0x8019fcu;
    request.header=*(volatile uint16_t *)(uintptr_t)0x8019feu;
    uintptr_t context=*(volatile uint32_t *)(record+44u);
    request.words[1]=parsed[1];
    request.words[0]=parsed[0];
    request.words[3]=parsed[3];
    request.kind=3u;
    if(opencfw_em9305_child_30301c((uintptr_t)&request,context+76u,0u,link+184u)==0u)
        return 0u;
    return *(volatile uint8_t *)(link+204u)!=0u;
}
