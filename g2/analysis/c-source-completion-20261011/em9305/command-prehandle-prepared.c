/* Native303270..303278: literal zero-fill52. */
uintptr_t opencfw_em9305_command_info_zero_303270(uintptr_t output)
{return (uintptr_t)opencfw_em9305_memset((void *)output,0u,52u);}
/* Native3032a8..3032b4: forward36-byte resident information copy. */
uintptr_t opencfw_em9305_command_info_copy_3032a8(uintptr_t output)
{return (uintptr_t)opencfw_em9305_memcpy((void *)output,(const void *)(uintptr_t)0x8017fcu,36u);}
extern uint32_t opencfw_em9305_command_pair_apply_307fa0(uint32_t,uint32_t);
/* Native30c580..30c5c0: full-width id check, readiness, busy and apply result. */
uint32_t opencfw_em9305_command_pair_set_30c580(uint32_t id,uint32_t value)
{
 if(opencfw_em9305_ll_stream_gate_30e510()==0u)return 12u;
 if(id>=3840u)return 18u;
 if(opencfw_em9305_command_ready_3213d0(id)==0u)return 66u;
 if(opencfw_em9305_address_busy_307cb8()!=0u)return 12u;
 return opencfw_em9305_command_pair_apply_307fa0(id,value)!=0u?0u:18u;
}
/* Native330bdc..330c60 full prehandler; fresh opcode after status store. */
uint32_t opencfw_em9305_command_prehandle_330bdc(uintptr_t request,uintptr_t input)
{
 uint32_t command=*(volatile uint16_t *)request,status;
 uintptr_t response;
 if(command==0xffdbu){status=0u;response=opencfw_em9305_ll_response_allocate_32e428(53u,0xffdbu);}
 else if(command==0xffb3u){
  uint32_t first_hi=*(volatile uint8_t *)(input+1u),second_hi=*(volatile uint8_t *)(input+3u);
  uint32_t first_lo=*(volatile uint8_t *)input,second_lo=*(volatile uint8_t *)(input+2u);
  status=opencfw_em9305_command_pair_set_30c580(first_lo+(first_hi<<8u),second_lo+(second_hi<<8u));
  response=opencfw_em9305_ll_response_allocate_32e428(1u,*(volatile uint16_t *)request);
 }else return 0u;
 if(response==0u)return 1u;
 *(volatile uint8_t *)response=(uint8_t)status;
 uint32_t fresh=*(volatile uint16_t *)request;
 _Alignas(4) uint8_t scratch[52];
 if(fresh==0xffdcu){
  (void)opencfw_em9305_command_info_copy_3032a8((uintptr_t)scratch);
  (void)opencfw_em9305_memcpy((void *)(response+1u),scratch,36u);
 }else if(fresh==0xffdbu){
  (void)opencfw_em9305_command_info_zero_303270((uintptr_t)scratch);
  (void)opencfw_em9305_memcpy((void *)(response+1u),scratch,52u);
 }
 (void)opencfw_em9305_ll_event_send(response-5u);return 1u;
}
