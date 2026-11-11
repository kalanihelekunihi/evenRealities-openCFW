#include <stdint.h>

/* Native 0x32c4fc..0x32c5a4: prepare the next periodic-advertising train
 * PDU for the link (+0x24). Without a pending anchor (+2780) only a restart
 * (more == 0) proceeds. The sync-info byte +2784 is copied to +2517; a
 * restart resets the offset (+1430), refills the train (native 0x325854) and
 * encodes the first PDU (native 0x3239fc) into the slot at +2616, otherwise
 * the train is refilled once it has been consumed (offset below the length
 * +2250) and the continuation PDU (native 0x323ac8) goes to the slot at
 * +2652 with the remaining data. Returns the anchor plus the configured
 * advance (config +22), or 0. */
extern uint32_t opencfw_em9305_child_325854(uintptr_t record);
extern uint32_t opencfw_em9305_associated_packet_continue_323ac8(uintptr_t,uintptr_t,uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_child_3239fc(uintptr_t,uintptr_t,uintptr_t,uint32_t);

uint32_t opencfw_em9305_child_32c4fc(uintptr_t context, uint32_t more)
{
    uintptr_t train = *(volatile uint32_t *)(context + 0x24u);
    uint32_t anchor = *(volatile uint32_t *)(train + 0xadcu);
    if (anchor == 0u && more != 0u) return 0u;
    uintptr_t config = *(volatile uint32_t *)(uintptr_t)0x805cacu;
    uint32_t info = *(volatile uint8_t *)(train + 0xae0u);
    uint32_t next = anchor + *(volatile uint16_t *)(config + 0x16u);
    volatile uint32_t *data = (volatile uint32_t *)(train + 1424u);
    volatile uint16_t *offset = (volatile uint16_t *)(train + 1430u);
    *(volatile uint8_t *)(train + 0x9d5u) = (uint8_t)info;
    if (more == 0u) {
        *offset = 0u;
        (void)opencfw_em9305_child_325854(train);
        uint32_t header = opencfw_em9305_child_3239fc(train, train + 945u, train + 1420u, 0u);
        uint32_t source = *data;
        uint32_t length = *offset;
        *(volatile uint16_t *)(train + 2616u) = (uint16_t)header;
        *(volatile uint32_t *)(train + 2628u) = source;
        *(volatile uint16_t *)(train + 2624u) = (uint16_t)length;
        return next;
    }
    uint32_t sent = *offset;
    if (sent < *(volatile uint16_t *)(train + 0x8cau))
        (void)opencfw_em9305_child_325854(train);
    uint32_t header = opencfw_em9305_associated_packet_continue_323ac8(train, train + 945u,
                                                                      train + 1420u, 0u);
    uint32_t source = *data;
    uint32_t length = *offset;
    *(volatile uint16_t *)(train + 2652u) = (uint16_t)header;
    *(volatile uint32_t *)(train + 2664u) = source + sent;
    *(volatile uint16_t *)(train + 2660u) = (uint16_t)(length - sent);
    return next;
}
