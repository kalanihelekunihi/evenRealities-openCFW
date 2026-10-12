extern uint32_t opencfw_em9305_command_records_commit_3096a8(uint32_t,uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_command_struct_commit_306cec(uintptr_t,uintptr_t);
/* Native30dc48..30dc6e: gate precedes ID validity; preserve captured arguments. */
uint32_t opencfw_em9305_command_records_apply_30dc48(uint32_t id,uint32_t count,uintptr_t records)
{
 if(opencfw_em9305_ll_stream_gate_30e510()==0u)return 12u;
 if(id>239u)return 18u;
 return opencfw_em9305_command_records_commit_3096a8(id,count,records);
}
/* Native332abc..332b60: header projection and either one or packed controls. */
uint32_t opencfw_em9305_command_struct_decode_332abc(uintptr_t header,uintptr_t pairs,uintptr_t controls,uintptr_t input)
{
 uint32_t first=*(volatile uint8_t *)input;
 *(volatile uint8_t *)(header+9u)=(uint8_t)first;
 uint32_t second=*(volatile uint8_t *)(input+1u);
 *(volatile uint8_t *)(header+10u)=(uint8_t)second;
 *(volatile uint8_t *)header=*(volatile uint8_t *)(input+2u);
 *(volatile uint8_t *)(header+1u)=*(volatile uint8_t *)(input+3u);
 uint32_t kind=*(volatile uint8_t *)(input+4u);
 *(volatile uint32_t *)(header+4u)=(uint32_t)(input+5u);
 *(volatile uint8_t *)(header+2u)=(uint8_t)kind;
 *(volatile uint8_t *)(header+8u)=*(volatile uint8_t *)(input+11u);
 uintptr_t cursor=input+12u;
 if(first!=255u&&second!=255u){
  uint32_t high=*(volatile uint8_t *)(input+13u),low=*(volatile uint8_t *)(input+12u);
  *(volatile uint16_t *)pairs=(uint16_t)((high<<8)+low);
  high=*(volatile uint8_t *)(input+15u);low=*(volatile uint8_t *)(input+14u);
  *(volatile uint16_t *)(pairs+2u)=(uint16_t)((high<<8)+low);
  cursor=input+16u+opencfw_em9305_ll_stream_control_decode_332a78(controls,input+16u);
 }else{
  uint32_t packed=0u;
  for(uint32_t bit=0u;bit<8u&&packed<3u;++bit){
   uint32_t mask=*(volatile uint8_t *)(header+8u);
   if((mask&(1u<<bit))==0u)continue;
   uintptr_t pair=pairs+packed*4u;
   uint32_t high=*(volatile uint8_t *)(cursor+1u),low=*(volatile uint8_t *)cursor;
   *(volatile uint16_t *)pair=(uint16_t)((high<<8)+low);
   high=*(volatile uint8_t *)(cursor+3u);low=*(volatile uint8_t *)(cursor+2u);
   *(volatile uint16_t *)(pair+2u)=(uint16_t)((high<<8)+low);
   uint32_t size=opencfw_em9305_ll_stream_control_decode_332a78(controls+packed*12u,cursor+4u);
   cursor+=size+4u;++packed;
  }
 }
 return (uint8_t)(cursor-input);
}
/* Native30b974..30b9ee: guarded single command or existing packed stream path. */
uint32_t opencfw_em9305_command_struct_apply_30b974(uintptr_t header,uintptr_t pairs,uintptr_t controls)
{
 uint32_t id=*(volatile uint8_t *)(header+9u);
 if(id==255u)return opencfw_em9305_ll_stream_command_30b7ec(header,pairs,controls);
 uint32_t stream=*(volatile uint8_t *)(header+10u);
 if(stream==255u)return opencfw_em9305_ll_stream_command_30b7ec(header,pairs,controls);
 if(id>239u)return 66u;
 if(stream>=16u)return 18u;
 uint32_t gate=opencfw_em9305_ll_stream_gate_30e510();
 uint32_t busy=*(volatile uint8_t *)(uintptr_t)0x805a74u;
 if(busy!=0u||gate==0u)return 12u;
 if(opencfw_em9305_ll_stream_header_valid_332f04(header)==0u)return 18u;
 if(opencfw_em9305_ll_stream_control_valid_332f00(controls)!=0u)return 18u;
 uint64_t address=opencfw_em9305_controller_pack_address(*(volatile uint32_t *)(header+4u));
 if(opencfw_em9305_ll_stream_address_busy_318200(*(volatile uint8_t *)(header+2u),(uint32_t)address,(uint32_t)(address>>32u))!=0u)return 11u;
 return opencfw_em9305_command_struct_commit_306cec(header,controls);
}
