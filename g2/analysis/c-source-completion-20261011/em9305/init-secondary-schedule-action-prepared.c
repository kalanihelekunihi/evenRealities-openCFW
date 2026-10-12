/* Complete native325d50..325d72: delayed reason capture precedes allocation. */
uint32_t opencfw_em9305_init_secondary_message_325d50(uintptr_t record,uint32_t reason)
{
 uintptr_t message=opencfw_em9305_wsf_event_allocate(4u);
 if(message==0u)return 0u;
 uint32_t event=*(volatile uint8_t *)(record+9u);
 uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 *(volatile uint8_t *)(message+3u)=(uint8_t)reason;
 *(volatile uint8_t *)(message+2u)=(uint8_t)event;
 return opencfw_em9305_wsf_task_message_send(handler,message);
}
/* Complete native318fc0..318fe6, callback incoming regs unused. */
uint32_t opencfw_em9305_init_secondary_action_318fc0(uintptr_t incoming,uint32_t offset,uint32_t state)
{
 (void)incoming;(void)offset;(void)state;
 uintptr_t root=0x8051a4u;
 uintptr_t record=*(volatile uint32_t *)(root+20u);
 uint32_t marked=*(volatile uint8_t *)(record+603u);
 if(marked==0u)*(volatile uint8_t *)(record+4u)=1u;
 uint32_t notify=*(volatile uint8_t *)(root+1u);
 if(notify!=0u){*(volatile uint8_t *)(record+3u)=1u;return opencfw_em9305_ll_schedule_notify_313354(record+48u);}
 return opencfw_em9305_init_secondary_message_325d50(record,5u);
}
