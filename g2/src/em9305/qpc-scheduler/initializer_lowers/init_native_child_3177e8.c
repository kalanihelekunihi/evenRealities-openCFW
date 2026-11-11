#include <stdint.h>

/* Native 0x3177e8..0x31788e: spend a byte budget of radio time on the
 * queued packets of a context (queue at +8). Each packet's progress byte +11
 * advances by its record timing (native 0x30c40c over length +8 and rate
 * +10) or by the remaining budget; a packet whose progress covers its length
 * is removed, released and completed (up to max packets, counted under
 * the critical section at 0x805adc). Without the busy flags +36/+108 every
 * finished packet bumps the idle count +16. Stops when the budget or the
 * queue runs out. */
extern uintptr_t opencfw_em9305_wsf_event_at(uintptr_t,uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_radio_record_timing_30c40c(uint32_t,uint32_t);
extern uintptr_t opencfw_em9305_wsf_event_remove(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_wsf_event_release(uintptr_t);
extern void opencfw_em9305_radio_packet_complete_31ae74(uintptr_t);
extern uint32_t opencfw_em9305_wsf_critical_enter(void);
extern uint32_t opencfw_em9305_wsf_critical_exit(void);

void opencfw_em9305_child_3177e8(uintptr_t context, uint32_t budget, uint32_t max)
{
    uint8_t handler;
    uintptr_t queue = context + 8u;
    uint32_t index = 0u, removed = 0u;
    for (;;) {
        uint32_t position = index - removed;
        uintptr_t packet;
        for (;;) {
            uint32_t room = budget & 0xffu;
            if (room == 0u) return;
            packet = opencfw_em9305_wsf_event_at(queue, position & 0xffu, (uintptr_t)&handler);
            if (packet == 0u) return;
            uint32_t time = opencfw_em9305_radio_record_timing_30c40c(
                *(volatile uint16_t *)(packet + 8u), *(volatile uint8_t *)(packet + 10u));
            uint32_t progress = *(volatile uint8_t *)(packet + 11u);
            if (time <= room) {
                progress += time;
                budget -= time;
            } else {
                progress += budget;
                budget = 0u;
            }
            uint32_t rate = *(volatile uint8_t *)(packet + 10u);
            *(volatile uint8_t *)(packet + 11u) = (uint8_t)progress;
            if (rate * (progress & 0xffu) >= *(volatile uint16_t *)(packet + 8u)) break;
        }
        if ((index & 0xffu) < max) {
            (void)opencfw_em9305_wsf_event_remove(queue, (uintptr_t)&handler);
            (void)opencfw_em9305_wsf_event_release(*(volatile uint32_t *)packet);
            opencfw_em9305_radio_packet_complete_31ae74(packet);
            (void)opencfw_em9305_wsf_critical_enter();
            volatile uint8_t *completed = (volatile uint8_t *)(uintptr_t)0x805adcu;
            *completed = (uint8_t)(*completed + 1u);
            (void)opencfw_em9305_wsf_critical_exit();
            ++removed;
        }
        ++index;
        if (*(volatile uint8_t *)(context + 36u) == 0u && *(volatile uint8_t *)(context + 108u) == 0u) {
            volatile uint8_t *idle = (volatile uint8_t *)(context + 16u);
            *idle = (uint8_t)(*idle + 1u);
        }
    }
}
