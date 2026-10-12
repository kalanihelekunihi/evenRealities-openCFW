/* Native306cec..306d7c: single-stream projection, fresh record reloads,
 * sparse event275 and nonfatal allocation failure. */
uint32_t opencfw_em9305_command_struct_commit_306cec(uintptr_t header,uintptr_t controls)
{
 uintptr_t record=opencfw_em9305_radio_record_find_31aa64(*(volatile uint8_t *)(header+9u));
 if(record==0u)return 66u;
 uintptr_t pointer=record+0xafcu;
 uintptr_t target=*(volatile uint32_t *)pointer;
 (void)opencfw_em9305_memcpy((void *)(target+82u),(const void *)controls,12u);
 target=*(volatile uint32_t *)pointer;
 uint32_t kind=*(volatile uint8_t *)(header+1u),address_kind=*(volatile uint8_t *)(header+2u);
 uintptr_t address=*(volatile uint32_t *)(header+4u);
 *(volatile uint8_t *)(target+65u)=(uint8_t)kind;
 *(volatile uint8_t *)(target+66u)=(uint8_t)address_kind;
 uint64_t packed=opencfw_em9305_controller_pack_address(address);
 target=*(volatile uint32_t *)pointer;
 uint32_t stream=*(volatile uint8_t *)(header+10u);
 *(volatile uint8_t *)(record+0x8d5u)=1u;
 *(volatile uint32_t *)(target+68u)=(uint32_t)packed;
 *(volatile uint32_t *)(target+72u)=(uint32_t)(packed>>32u);
 *(volatile uint8_t *)(target+76u)=(uint8_t)stream;
 uintptr_t message=opencfw_em9305_wsf_event_allocate(20u);
 if(message==0u)return 0u;
 *(volatile uint16_t *)(message+2u)=275u;
 uint32_t id=*(volatile uint8_t *)(header+9u);
 kind=*(volatile uint8_t *)(header+1u);address_kind=*(volatile uint8_t *)(header+2u);
 *(volatile uint16_t *)message=(uint16_t)id;
 address=*(volatile uint32_t *)(header+4u);
 *(volatile uint8_t *)(message+5u)=(uint8_t)kind;
 *(volatile uint8_t *)(message+6u)=(uint8_t)address_kind;
 packed=opencfw_em9305_controller_pack_address(address);
 *(volatile uint32_t *)(message+8u)=(uint32_t)packed;
 uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 *(volatile uint32_t *)(message+12u)=(uint32_t)(packed>>32u);
 (void)opencfw_em9305_wsf_task_message_send(handler,message);
 return 0u;
}
