#include <stdint.h>

/* Native 0x31a258..0x31a328: post the 88-byte connection-established message
 * (code 0x3f01) for a link to the handler at 0x805b18: handle (+88, also
 * clearing byte 2 of its 912-byte connection entry), the 44 connection bytes
 * from +0x24, the peer address (+460 block when +96 is set, else +676) with
 * its type (bit 1 set and the resolved address kept when it differs from the
 * identity), the local words +0x50/+0x54, role +97 and accuracy +100. Then
 * run native 0x31ff2c and select the link's PHY bit (1 << +16) at 0x802a5d,
 * which is returned. */
extern uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t);
extern void *opencfw_em9305_memcpy(void *destination, const void *source, uint32_t bytes);
extern uint32_t opencfw_em9305_wsf_task_message_send(uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_child_31ff2c(uintptr_t);

uint32_t opencfw_em9305_child_31a258(uintptr_t link)
{
    uintptr_t message = opencfw_em9305_wsf_event_allocate(0x58u);
    if (message != 0u) {
        uint32_t handle = *(volatile uint16_t *)(link + 88u);
        *(volatile uint16_t *)(message + 2u) = 0x3f01u;
        uintptr_t entry = handle * 912u + *(volatile uint32_t *)(uintptr_t)0x805c70u;
        *(volatile uint16_t *)message = (uint8_t)handle;
        *(volatile uint8_t *)(entry + 2u) = 0u;
        (void)opencfw_em9305_memcpy((void *)(message + 4u), (const void *)(link + 0x24u), 0x2cu);
        uint32_t identity_high, identity_low;
        uintptr_t peer;
        if (*(volatile uint8_t *)(link + 96u) != 0u) {
            identity_high = *(volatile uint32_t *)(link + 472u);
            identity_low = *(volatile uint32_t *)(link + 468u);
            peer = link + 460u;
        } else {
            identity_high = *(volatile uint32_t *)(link + 688u);
            identity_low = *(volatile uint32_t *)(link + 684u);
            peer = link + 676u;
        }
        uint32_t type = *(volatile uint8_t *)(peer + 19u);
        uint32_t identity_type = *(volatile uint8_t *)(peer + 18u);
        uint32_t resolved_high = *(volatile uint32_t *)(peer + 4u);
        uint32_t resolved_low = *(volatile uint32_t *)peer;
        if (type == identity_type && identity_high == resolved_high && identity_low == resolved_low) {
            resolved_low = 0u;
            resolved_high = 0u;
        } else {
            type |= 2u;
        }
        *(volatile uint32_t *)(message + 0x44u) = resolved_low;
        *(volatile uint32_t *)(message + 0x3cu) = identity_low;
        *(volatile uint8_t *)(message + 52u) = (uint8_t)type;
        *(volatile uint32_t *)(message + 0x48u) = resolved_high;
        *(volatile uint32_t *)(message + 0x40u) = identity_high;
        uint32_t local_high = *(volatile uint32_t *)(link + 0x54u);
        uint32_t local_low = *(volatile uint32_t *)(link + 0x50u);
        *(volatile uint32_t *)(message + 0x50u) = local_high;
        *(volatile uint32_t *)(message + 0x4cu) = local_low;
        *(volatile uint8_t *)(message + 53u) = *(volatile uint8_t *)(link + 97u);
        uint32_t accuracy = *(volatile uint8_t *)(link + 100u);
        uint32_t handler = *(volatile uint8_t *)(uintptr_t)0x805b18u;
        *(volatile uint16_t *)(message + 86u) = 0xffffu;
        *(volatile uint8_t *)(message + 54u) = (uint8_t)accuracy;
        *(volatile uint8_t *)(message + 84u) = 0xffu;
        (void)opencfw_em9305_wsf_task_message_send(handler, message);
    }
    (void)opencfw_em9305_child_31ff2c(link);
    uint32_t phy = 1u << (*(volatile uint8_t *)(link + 16u) & 31u);
    *(volatile uint8_t *)(uintptr_t)0x802a5du = (uint8_t)phy;
    return phy;
}
