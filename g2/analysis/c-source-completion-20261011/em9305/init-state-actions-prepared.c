/* Native334458/33445e: six-byte state-status events with attributed
 * halfword/byte field roles and no callback/code pointer payload. */
struct opencfw_em9305_init_state_status {uint16_t handle;uint8_t event,status;uint16_t value;};
_Static_assert(sizeof(struct opencfw_em9305_init_state_status)==6u,"native state status size");
static const struct opencfw_em9305_init_state_status opencfw_em9305_init_state_status_334458={0u,8u,12u,12u};
static const struct opencfw_em9305_init_state_status opencfw_em9305_init_state_status_33445e={0u,8u,0u,0u};
uint32_t opencfw_em9305_init_state_action_31b4a4(uintptr_t incoming,uint32_t state)
{
 (void)incoming;(void)state;
 _Alignas(4) struct opencfw_em9305_init_state_status event=opencfw_em9305_init_state_status_334458;
 return opencfw_em9305_ll_event_callback_30e79c((uintptr_t)&event);
}
/* Native3257a4..3257e2:38 defined event bytes in40-byte native caller frame.
 * Bytes38/39 are padding outside the qualified event extent. */
uint32_t opencfw_em9305_init_state_status_send_3257a4(uint32_t code,uint32_t id,uint32_t low,uint32_t high)
{
 _Alignas(4) uint8_t event[38];
 (void)opencfw_em9305_memset(event,0u,36u);
 *(volatile uint16_t *)(event+36u)=0xffffu;event[35]=0xffu;
 event[9]=(uint8_t)id;event[4]=(uint8_t)code;event[3]=(uint8_t)code;event[2]=5u;
 (void)opencfw_em9305_radio_address_write_3045e8((uintptr_t)(event+10u),low,high);
 return opencfw_em9305_ll_event_callback_30e79c((uintptr_t)event);
}
uint32_t opencfw_em9305_init_state_action_31b4c8(uintptr_t incoming,uint32_t state)
{
 (void)incoming;(void)state;
 uintptr_t request=*(volatile uint32_t *)(uintptr_t)0x805c78u;
 uint32_t high=*(volatile uint32_t *)(request+28u);
 uint32_t low=*(volatile uint32_t *)(request+24u);
 uint32_t id=*(volatile uint8_t *)(request+32u);
 return opencfw_em9305_init_state_status_send_3257a4(12u,id,low,high);
}
/* Native30e49c..30e4a8: secondary byte counter and address return. */
uint32_t opencfw_em9305_init_state_count_down_30e49c(void)
{
 uint32_t count=*(volatile uint8_t *)(uintptr_t)0x805a76u;
 *(volatile uint8_t *)(uintptr_t)0x805a76u=(uint8_t)(count-1u);return 0x805a76u;
}
/* Native322884..3228a4: clear each owned event before release, fresh second
 * event loaded after first release. Native zero/child R0 retained. */
uint32_t opencfw_em9305_init_state_events_clear_322884(uintptr_t record)
{
 uintptr_t event=*(volatile uint32_t *)(record+300u);
 *(volatile uint32_t *)(record+300u)=0u;
 if(event!=0u)(void)opencfw_em9305_wsf_event_release(event);
 event=*(volatile uint32_t *)(record+308u);
 *(volatile uint32_t *)(record+308u)=0u;
 if(event!=0u)return opencfw_em9305_wsf_event_release(event);
 return 0u;
}
/* Native325740..3257a2: complete cleanup. The native second loop advances
 * record by48 on every iteration; retain this observed CFG, not a fixed queue. */
uint32_t opencfw_em9305_init_state_cleanup_325740(uintptr_t record)
{
 (void)opencfw_em9305_command_count_down_30e48c();
 if(record==(uintptr_t)0x804fd8u)*(volatile uint8_t *)(uintptr_t)0x805a73u=0u;
 else *(volatile uint8_t *)(uintptr_t)0x805a74u=0u;
 if((*(volatile uint8_t *)(record+66u)&1u)!=0u)(void)opencfw_em9305_init_state_count_down_30e49c();
 (void)opencfw_em9305_init_state_events_clear_322884(record);
 volatile uint8_t handler;
 for(;;){uintptr_t event=opencfw_em9305_wsf_event_remove(record+40u,(uintptr_t)&handler);
  if(event==0u)break;
  (void)opencfw_em9305_wsf_event_release(event);
 }
 for(;;){record+=48u;uintptr_t event=opencfw_em9305_wsf_event_remove(record,(uintptr_t)&handler);
  if(event==0u)return 0u;
  (void)opencfw_em9305_wsf_event_release(event);
 }
}
uint32_t opencfw_em9305_init_state_action_31b614(uintptr_t incoming,uint32_t state)
{
 (void)incoming;(void)state;
 uint32_t index=*(volatile uint16_t *)(uintptr_t)0x803c0cu;
 uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 (void)opencfw_em9305_receive_terminate_325c08(base+index*912u,76u);
 (void)opencfw_em9305_common_release_304588(1u);
 return opencfw_em9305_init_state_cleanup_325740((uintptr_t)0x803b94u);
}
uint32_t opencfw_em9305_init_state_action_31b648(uintptr_t incoming,uint32_t state)
{
 (void)incoming;(void)state;
 uint32_t index=*(volatile uint16_t *)(uintptr_t)0x803c0cu;
 uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 (void)opencfw_em9305_receive_terminate_325c08(base+index*912u,77u);
 (void)opencfw_em9305_common_release_304588(1u);
 (void)opencfw_em9305_init_state_cleanup_325740((uintptr_t)0x803b94u);
 _Alignas(4) struct opencfw_em9305_init_state_status event=opencfw_em9305_init_state_status_33445e;
 (void)opencfw_em9305_ll_event_callback_30e79c((uintptr_t)&event);
 uintptr_t record=0x803cacu;
 uint32_t high=*(volatile uint32_t *)(record+16u),low=*(volatile uint32_t *)(record+12u);
 uint32_t kind=*(volatile uint8_t *)record;
 return opencfw_em9305_init_state_status_send_3257a4(2u,kind&15u,low,high);
}
