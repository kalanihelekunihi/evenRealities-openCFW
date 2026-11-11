#include <stdint.h>

/* Native 0x31bbb0..0x31bc28: drain the six-entry received-test-packet
 * ring at 0x8028d0 (tail +0, head +4, 20-byte entries from +8). Each
 * entry becomes a type-258 report (id +8, length +0x18, timestamp +0x10,
 * status +0xc) for the message 12 bytes before the stored buffer (+0x14);
 * the buffer slot is cleared and the test timer restarted. */
extern uint32_t opencfw_em9305_dispatch_child_31b9ac(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_ll_received_event_active(uintptr_t);
extern uint32_t opencfw_em9305_ll_test_timer_31c490(uint32_t,uint32_t);

struct init_test_report_31bbb0 {
    uint16_t id;
    uint16_t type;
    uint16_t length;
    uint16_t reserved0;
    uint32_t timestamp;
    uint16_t status;
    uint16_t length_copy;
    uint8_t flag;
    uint8_t reserved1[3];
    uint32_t extra;
};

void opencfw_em9305_callback_31bbb0(void)
{
    volatile uint32_t *ring=(volatile uint32_t *)(uintptr_t)0x8028d0u;
    uint32_t head=ring[1];
    if(head==ring[0]) return;
    struct init_test_report_31bbb0 report;
    do {
        uintptr_t entry=(uintptr_t)0x8028d0u+head*20u;
        report.extra=0u;
        report.flag=0u;
        report.id=*(volatile uint16_t *)(entry+8u);
        report.type=258u;
        uintptr_t message=*(volatile uint32_t *)(entry+0x14u)-12u;
        report.timestamp=*(volatile uint32_t *)(entry+0x10u);
        uint32_t length=*(volatile uint16_t *)(entry+0x18u);
        report.length=(uint16_t)length;
        report.length_copy=(uint16_t)length;
        report.status=(uint16_t)*(volatile uint32_t *)(entry+0xcu);
        (void)opencfw_em9305_dispatch_child_31b9ac(message,(uintptr_t)&report);
        (void)opencfw_em9305_ll_received_event_active(message);
        *(volatile uint32_t *)((uintptr_t)0x8028d0u+ring[1]*20u+0x14u)=0u;
        (void)opencfw_em9305_ll_test_timer_31c490(report.id,report.timestamp);
        head=(ring[1]+1u)%6u;
        ring[1]=head;
    } while(head!=ring[0]);
}
