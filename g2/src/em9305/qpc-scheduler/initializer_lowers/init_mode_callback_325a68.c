#include <stdint.h>

/* Native 0x325a68..0x325b12. This callback composes already selected
 * queue-count, capacity, timing, allocator, and sender providers. Native
 * MPYWHUL/MPYW are 32 x 16 / 16 x 16 products written in C. */
extern uint32_t opencfw_em9305_phy_packet_alloc_32d2f0(uint32_t);
extern uint32_t opencfw_em9305_phy_queue_count_314114(uintptr_t);
extern uint32_t opencfw_em9305_ll_event_mode_32d4b0(uintptr_t);
extern uint32_t opencfw_em9305_radio_record_timing_30c40c(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_phy_packet_send_32d32c(uintptr_t,uintptr_t);
static uint32_t multiply_whul(uint32_t a,uint32_t b)
{
    return (uint32_t)a*(uint16_t)b;
}
static uint32_t multiply_w(uint32_t a,uint32_t b)
{
    return (uint32_t)((int32_t)(int16_t)a*(int16_t)b);
}
uint32_t opencfw_em9305_mode_callback_325a68(uintptr_t context,
                                               uintptr_t callback_identity)
{
    (void)callback_identity;
    uintptr_t packet=opencfw_em9305_phy_packet_alloc_32d2f0(8u);
    if (packet==0u) return 0u;
    uint32_t anchor=*(volatile uint16_t *)(context+262u);
    uintptr_t queue=context+360u;
    uint32_t count=opencfw_em9305_phy_queue_count_314114(queue);
    uintptr_t root=*(volatile uint32_t *)(uintptr_t)0x805cacu;
    uint32_t unit=*(volatile uint16_t *)(root+38u);
    uint32_t scaled=multiply_whul(count,unit);
    uint32_t capacity=opencfw_em9305_ll_event_mode_32d4b0(context);
    uint32_t timing=opencfw_em9305_radio_record_timing_30c40c(scaled,capacity);
    if (timing<6u) timing=6u;
    else {
        count=opencfw_em9305_phy_queue_count_314114(queue);
        root=*(volatile uint32_t *)(uintptr_t)0x805cacu;
        unit=*(volatile uint16_t *)(root+38u);
        scaled=multiply_whul(count,unit);
        capacity=opencfw_em9305_ll_event_mode_32d4b0(context);
        timing=opencfw_em9305_radio_record_timing_30c40c(scaled,capacity);
    }
    uint32_t latency=*(volatile uint16_t *)(context+260u);
    uint32_t interval=*(volatile uint16_t *)(context+846u);
    uint32_t product=multiply_w(interval,(latency+1u)*timing);
    *(volatile uint16_t *)(context+716u)=(uint16_t)(product+anchor);
    *(volatile uint8_t *)packet=1u;
    *(volatile uint8_t *)(packet+1u)=*(volatile uint8_t *)(context+708u);
    *(volatile uint8_t *)(packet+2u)=*(volatile uint8_t *)(context+709u);
    *(volatile uint8_t *)(packet+3u)=*(volatile uint8_t *)(context+710u);
    *(volatile uint8_t *)(packet+4u)=*(volatile uint8_t *)(context+711u);
    *(volatile uint8_t *)(packet+5u)=*(volatile uint8_t *)(context+712u);
    *(volatile uint8_t *)(packet+6u)=*(volatile uint8_t *)(context+716u);
    *(volatile uint8_t *)(packet+7u)=*(volatile uint8_t *)(context+717u);
    return opencfw_em9305_phy_packet_send_32d32c(context,packet);
}
