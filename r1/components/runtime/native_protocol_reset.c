#include <stdint.h>
extern uint32_t r1_proto_port_init(void);
extern volatile uint16_t r1_protocol_sequence;
extern void __aeabi_memclr(void *,uint32_t);
extern void r1_native_delayed_schedule(void (*)(uint32_t),uint32_t,uint32_t);
extern uint32_t r1_event_publish(uint32_t,const void *,uint32_t);
volatile uint8_t r1_protocol_reset_workspace[640]
 __attribute__((section(".r1.protocol.reset.workspace"),aligned(4)))={0};
/* Supplemental callback recovered from native instructions, absent from the
 * locked function ledger. Only its one-byte payload has a public contract. */
__attribute__((noinline,section(".r1.protocol.reset.callback")))
void r1_protocol_reaper_tick(uint32_t argument)
{
 (void)argument;uint8_t value=1;
 (void)r1_event_publish(0x10,&value,1);
 r1_native_delayed_schedule(r1_protocol_reaper_tick,0,0x384000);
}
void r1_ack_reaper_arm(void)
{r1_native_delayed_schedule(r1_protocol_reaper_tick,0,0x384000);}
uint32_t r1_native_proto_port_reset(void)
{
 (void)r1_proto_port_init();
 __aeabi_memclr((void *)(uintptr_t)r1_protocol_reset_workspace,640);
 r1_ack_reaper_arm();r1_protocol_sequence=0;return 0;
}
