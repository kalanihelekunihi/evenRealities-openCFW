#include <stdint.h>

/* Native 0x31a5bc..0x31a6f8: create a connection for an initiator/advertiser
 * link. Take a free connection entry (native 0x316c58, status 9 when none)
 * and reserve its anchor slot (native 0x3133b4 between the link's minimum
 * and maximum interval +24/+26, units of 1250 us, with CE length +592 of the
 * entry; status 13 and release on failure). Bind the link to the entry
 * index (+88), store the slot anchor in 625 us units (+90), role/PHY bytes
 * (+98/+99) and the peer address/type in the 912-byte entry, then start the
 * connection (natives 0x320088, 0x31c88c). On success count the role up
 * (PHY 1, 3 or 4 also counts the secondary init state) and return 0;
 * otherwise report the status (native 0x3257a4), post event 2 and return
 * the status. */
extern uintptr_t opencfw_em9305_init_connection_allocate_316c58(void);
extern uint32_t opencfw_em9305_associated_slot_allocate_3133b4(uint32_t id, uint32_t direction,
                                                               uint32_t minimum, uint32_t maximum,
                                                               uint32_t extent, uintptr_t output,
                                                               uintptr_t query);
extern uint32_t opencfw_em9305_init_connection_query_31b21c(uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_init_connection_release_31ad90(uintptr_t);
extern uint32_t opencfw_em9305_common_request_30455c(uint32_t);
extern uint32_t opencfw_em9305_common_release_304588(uint32_t);
extern uint32_t opencfw_em9305_child_320088(uintptr_t,uintptr_t,uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_child_31c88c(uintptr_t,uintptr_t,uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_init_state_status_send_3257a4(uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_child_325e84(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_init_secondary_count_up_30e4cc(void);
extern uint32_t opencfw_em9305_command_count_30e4bc(void);

uint32_t opencfw_em9305_child_31a5bc(uintptr_t link, uint32_t peer_type, uint32_t peer_low,
                                     uint32_t peer_high, uint32_t role, uint32_t phy)
{
    uint32_t status;
    uint32_t anchor;
    uintptr_t entry = opencfw_em9305_init_connection_allocate_316c58();
    if (entry == 0u) {
        status = 9u;
    } else {
        uintptr_t interval = link + 0x18u;
        uint32_t index = (uint8_t)((int32_t)(entry - *(volatile uint32_t *)(uintptr_t)0x805c70u) / 912);
        uint32_t minimum = *(volatile uint16_t *)interval * 1250u;
        uint32_t maximum = *(volatile uint16_t *)(interval + 2u) * 1250u;
        if (opencfw_em9305_associated_slot_allocate_3133b4(
                index, 0u, minimum, maximum, *(volatile uint16_t *)(entry + 592u), (uintptr_t)&anchor,
                (uintptr_t)opencfw_em9305_init_connection_query_31b21c) == 0u) {
            (void)opencfw_em9305_init_connection_release_31ad90(entry);
            status = 13u;
        } else {
            uintptr_t base = *(volatile uint32_t *)(uintptr_t)0x805c70u;
            index = (uint8_t)((int32_t)(entry - base) / 912);
            *(volatile uint8_t *)(link + 242u) = 0u;
            *(volatile uint8_t *)(link + 241u) = 0u;
            uint64_t scaled = (uint64_t)anchor * 0x1a36e3u;
            *(volatile uint8_t *)(link + 2u) = 0u;
            *(volatile uint8_t *)(link + 1u) = 0u;
            *(volatile uint16_t *)(link + 88u) = (uint16_t)index;
            uintptr_t connection = index * 912u + base;
            *(volatile uint8_t *)(link + 99u) = (uint8_t)phy;
            *(volatile uint8_t *)(link + 98u) = (uint8_t)role;
            *(volatile uint16_t *)(link + 90u) = (uint16_t)(scaled >> 31);
            *(volatile uint32_t *)(connection + 520u) = peer_high;
            *(volatile uint32_t *)(connection + 516u) = peer_low;
            *(volatile uint8_t *)(connection + 524u) = (uint8_t)peer_type;
            *(volatile uint8_t *)(connection + 890u) = 0xffu;
            *(volatile uint16_t *)(connection + 892u) = 0xffffu;
            (void)opencfw_em9305_common_request_30455c(1u);
            status = opencfw_em9305_child_320088(link, interval, peer_low, peer_high, peer_type);
            if (status == 0u)
                status = opencfw_em9305_child_31c88c(link, interval, peer_low, peer_high, peer_type);
            if (status == 0u) {
                uint32_t kind = *(volatile uint8_t *)(link + 98u);
                if (kind < 5u && ((0x1au >> kind) & 1u) != 0u)
                    (void)opencfw_em9305_init_secondary_count_up_30e4cc();
                volatile uint8_t *links = (volatile uint8_t *)(uintptr_t)0x805a74u;
                *links = (uint8_t)(*links + 1u);
                (void)opencfw_em9305_command_count_30e4bc();
                return 0u;
            }
            (void)opencfw_em9305_common_release_304588(1u);
        }
    }
    (void)opencfw_em9305_init_state_status_send_3257a4(status, peer_type, peer_low, peer_high);
    (void)opencfw_em9305_child_325e84(link, 2u);
    return status;
}
