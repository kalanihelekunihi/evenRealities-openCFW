/* Native3252b8..3252da: drain connection+368, count modulo256. */
uint32_t opencfw_em9305_init_connection_drain_3252b8(uintptr_t connection)
{
 uintptr_t queue=connection+368u;uint32_t count=0u;uint8_t handler;
 for(;;){uintptr_t event=opencfw_em9305_wsf_event_remove(queue,(uintptr_t)&handler);if(event==0u)return (uint8_t)count;(void)opencfw_em9305_wsf_event_release(event);count+=1u;}
}
/* Native31ae64..31ae6e: return event's eight-byte header to recycle queue. */
uint32_t opencfw_em9305_init_connection_recycle_31ae64(uintptr_t event)
{return opencfw_em9305_wsf_queue_append(0x8056dcu,event-8u);}
/* Native32d5f4..32d648: handler255 events have no nested payload/recycle. */
uint32_t opencfw_em9305_init_connection_drain_32d5f4(uintptr_t connection)
{
 uintptr_t queue=connection+360u;uint32_t count=0u;uint8_t handler;
 for(;;){
  uintptr_t event=opencfw_em9305_wsf_event_remove(queue,(uintptr_t)&handler);
  if(event==0u)return (uint8_t)count;
  if(handler==255u){(void)opencfw_em9305_wsf_event_release(event);continue;}
  uintptr_t payload=*(volatile uint32_t *)event;
  (void)opencfw_em9305_wsf_event_release(payload-4u);
  (void)opencfw_em9305_init_connection_recycle_31ae64(event);
  (void)opencfw_em9305_wsf_critical_enter();
  uint32_t value=*(volatile uint8_t *)(uintptr_t)0x805ab4u;
  *(volatile uint8_t *)(uintptr_t)0x805ab4u=(uint8_t)(value+1u);
  (void)opencfw_em9305_wsf_critical_exit();count+=1u;
 }
}
/* Native31ad90..31ae62, including authentic indirect callback R1=callee.
 * Further ambient caller-saved registers are not asserted by this contract. */
uint32_t opencfw_em9305_init_connection_release_31ad90(uintptr_t connection)
{
 uint32_t drained=opencfw_em9305_init_connection_drain_3252b8(connection);
 (void)opencfw_em9305_wsf_critical_enter();
 uint32_t count=*(volatile uint8_t *)(uintptr_t)0x805ab5u;
 *(volatile uint8_t *)(uintptr_t)0x805ab5u=(uint8_t)(count+drained);
 (void)opencfw_em9305_wsf_critical_exit();
 (void)opencfw_em9305_init_connection_drain_32d5f4(connection);
 uintptr_t queue=connection+352u;uint8_t handler;
 for(;;){
  uintptr_t event=opencfw_em9305_wsf_event_remove(queue,(uintptr_t)&handler);
  if(event==0u)break;
  if(handler!=255u){(void)opencfw_em9305_wsf_critical_enter();count=*(volatile uint8_t *)(uintptr_t)0x805ab4u;*(volatile uint8_t *)(uintptr_t)0x805ab4u=(uint8_t)(count+1u);(void)opencfw_em9305_wsf_critical_exit();}
  (void)opencfw_em9305_wsf_event_release(event);
 }
 (void)opencfw_em9305_wsf_timer_stop(connection+384u);
 (void)opencfw_em9305_wsf_timer_stop(connection+728u);
 (void)opencfw_em9305_wsf_timer_stop(connection+476u);
 (void)opencfw_em9305_wsf_timer_stop(connection+496u);
 uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 uintptr_t callbacks=*(volatile uint32_t *)(uintptr_t)0x805cd8u;
 uint32_t id=(uint8_t)opencfw_em9305_associated_slot_sdiv((uint32_t)(connection-base),912u);
 if(callbacks!=0u){uintptr_t callback=*(volatile uint32_t *)(callbacks+4u);if(callback!=0u)(void)((uint32_t(*)(uint32_t,uintptr_t))callback)(id,callback);}
 uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x8027f4u;
 if(callback!=0u)(void)((uint32_t(*)(uint32_t,uintptr_t))callback)(id,callback);
 uintptr_t event=*(volatile uint32_t *)(connection+760u);
 *(volatile uint8_t *)connection=0u;
 if(event!=0u)(void)opencfw_em9305_wsf_event_release(event);
 (void)opencfw_em9305_command_count_down_30e48c();
 count=*(volatile uint8_t *)(uintptr_t)0x805a70u;
 *(volatile uint8_t *)(uintptr_t)0x805a70u=(uint8_t)(count-1u);
 return opencfw_em9305_common_release_304588(1u);
}
