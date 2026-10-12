/* Native3304f0..33052c. Prepared while selected snapshot runs. Native32f0a0 saves r0 and reads packet+2; native3304f0 forwards packet and returns its r0. */
extern uint32_t opencfw_em9305_dispatch_32f0a0(uintptr_t);
uint32_t opencfw_em9305_dispatch_3304f0(uintptr_t packet)
{
 if(*(volatile uint8_t *)(packet+2u)!=8u)
  return opencfw_em9305_dispatch_32f0a0(packet);
 uintptr_t event=opencfw_em9305_ll_event_allocate(14u,4u);
 if(event==0u)return 0u;
 *(volatile uint8_t *)(event+1u)=14u;
 *(volatile uint8_t *)(event+2u)=32u;
 /* Native STB.AB stores before subtracting2 from r0. */
 *(volatile uint8_t *)event=1u;
 uint32_t status=*(volatile uint8_t *)(packet+4u);
 *(volatile uint8_t *)(event+3u)=(uint8_t)status;
 (void)opencfw_em9305_ll_event_send(event-2u);
 return 1u;
}
