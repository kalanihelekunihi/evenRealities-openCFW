#include <stdint.h>

/* Native 0x31f904..0x31f9aa: handle a received encryption PDU for the
 * link at +36. No PDU: run 325688. Otherwise decode its header and, while
 * the context (+44) is in key state 4 with the link's 64-bit key id
 * (+104) matching +168, validate it with 319ee8 (flags = +187, plus bit 1
 * when +186 differs or the id at +176 changed); on success clear +34 and
 * run the 31a1b0/31a1fc session-key steps on +20/+56. Every PDU path ends
 * with 3256c8. Returns 0. */
extern uint32_t opencfw_em9305_child_325688(uintptr_t link);
extern uint32_t opencfw_em9305_child_32db0c(uintptr_t out, uintptr_t in);
extern uint32_t opencfw_em9305_child_319ee8(uintptr_t link, uint32_t mode, uintptr_t header,
                                            uint32_t id_low, uint32_t id_high,
                                            uint32_t flags, int32_t key_state,
                                            uintptr_t pdu, uintptr_t session);
extern uint32_t opencfw_em9305_child_31a1b0(uintptr_t link, uintptr_t session, uintptr_t key);
extern uint32_t opencfw_em9305_child_31a1fc(uintptr_t link, uintptr_t session, uintptr_t key);
extern uint32_t opencfw_em9305_child_3256c8(uintptr_t link);

uint32_t opencfw_em9305_child_31f904(uintptr_t owner, uintptr_t pdu)
{
    uint8_t header[8];
    uintptr_t link=*(volatile uint32_t *)(owner+36u);
    if(pdu==0u){
        (void)opencfw_em9305_child_325688(link);
        return 0u;
    }
    uintptr_t context=*(volatile uint32_t *)(owner+44u);
    uintptr_t key=context+152u;
    (void)opencfw_em9305_child_32db0c((uintptr_t)header,pdu);
    if(*(volatile uint8_t *)(key+32u)==4u){
        uint32_t id_low=*(volatile uint32_t *)(link+104u);
        uint32_t id_high=*(volatile uint32_t *)(link+108u);
        if(*(volatile uint32_t *)(key+16u)==id_low&&*(volatile uint32_t *)(key+20u)==id_high){
            uint32_t flags=*(volatile uint8_t *)(context+187u);
            uint32_t previous=*(volatile uint8_t *)(context+186u);
            uint32_t next_high=*(volatile uint32_t *)(key+28u);
            uint32_t next_low=*(volatile uint32_t *)(key+24u);
            if(flags!=previous||next_low!=id_low||next_high!=id_high)flags|=2u;
            uintptr_t session=link+20u;
            if(opencfw_em9305_child_319ee8(link,0u,(uintptr_t)header,next_low,next_high,flags,
                                           *(volatile int8_t *)key,pdu,session)!=0u){
                uintptr_t session_key=link+56u;
                *(volatile uint8_t *)(link+34u)=0u;
                if(opencfw_em9305_child_31a1b0(link,session,session_key)!=0u)
                    (void)opencfw_em9305_child_31a1fc(link,session,session_key);
            }
        }
    }
    (void)opencfw_em9305_child_3256c8(link);
    return 0u;
}
