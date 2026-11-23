#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x324e3c..0x324ea2: queue a 24-byte message 0x206 {u8 a, u8 b,
 * u32 c, u32 d, u32 context, u32 value} to the task at ((uintptr_t)&em9305_ram_805af0 + 0x28u) while
 * fewer than four are outstanding (count at ((uintptr_t)&em9305_ram_805af0 + 0x6cu), read and bumped
 * inside critical sections). */
extern void opencfw_em9305_wsf_critical_enter(void);
extern void opencfw_em9305_wsf_critical_exit(void);
extern uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t length);
extern uint32_t opencfw_em9305_wsf_task_message_send(uint32_t task, uintptr_t message);

void opencfw_em9305_callback_324e3c(uint32_t context, uint32_t value, uint32_t a,
                                    uint32_t b, uint32_t c, uint32_t d)
{
    volatile uint8_t *outstanding=&em9305_ram_805af0.u8_805b5c;
    opencfw_em9305_wsf_critical_enter();
    uint32_t count=*outstanding;
    opencfw_em9305_wsf_critical_exit();
    if(count>=4u)return;
    uintptr_t message=opencfw_em9305_wsf_event_allocate(24u);
    if(message==0u)return;
    uint32_t task=em9305_ram_805af0.u8_805b18;
    *(volatile uint16_t *)(message+2u)=0x206u;
    *(volatile uint32_t *)(message+16u)=context;
    *(volatile uint32_t *)(message+8u)=c;
    *(volatile uint8_t *)(message+5u)=(uint8_t)b;
    *(volatile uint8_t *)(message+4u)=(uint8_t)a;
    *(volatile uint32_t *)(message+20u)=value;
    *(volatile uint32_t *)(message+12u)=d;
    (void)opencfw_em9305_wsf_task_message_send(task,message);
    opencfw_em9305_wsf_critical_enter();
    *outstanding=(uint8_t)(*outstanding+1u);
    opencfw_em9305_wsf_critical_exit();
}
