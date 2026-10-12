extern uint32_t opencfw_em9305_compose_aux_encode_324438(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_compose_finalize_32412c(uintptr_t,uintptr_t,uintptr_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_compose_action_3237e8(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_compose_action_32366c(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_compose_action_323820(uintptr_t,uintptr_t);
/* Native3352f4 three typed callback identities; no stock code addresses copied. */
static uint32_t (*const opencfw_em9305_compose_actions_3352f4[3])(uintptr_t,uintptr_t)={opencfw_em9305_compose_action_3237e8,opencfw_em9305_compose_action_32366c,opencfw_em9305_compose_action_323820};
/* Native323dc0..32412a full compositor C control/data flow. */
uint32_t opencfw_em9305_radio_compose_323dc0(uintptr_t record,uint32_t forced,uint32_t allowed,uint32_t prefix,uintptr_t header,uintptr_t source,uintptr_t output,uint32_t type,uint32_t count)
{
 uint32_t present=0u,enabled=1u,remaining=0u,capacity=0u,aux=0u,power=0u,written=0u;
 uintptr_t channels=record+704u,cursor=output+4u,end=0u,body=output+3u;
 *(volatile uint8_t *)(header+4u)=0u;
 if(type==5u)type=count!=0u?4u:2u;
 else if((*(volatile uint8_t *)(uintptr_t)0x805a87u&1u)!=0u)enabled=0u;
 uint32_t include_address=record==0u?(type==3u||type==6u):((*(volatile uint16_t *)(record+32u)&32u)==0u||type==3u||type==6u);
 if(include_address!=0u&&((forced&1u)!=0u||(record!=0u&&(allowed&1u)!=0u&&(*(volatile uint8_t *)(channels+123u)&1u)==0u))){
  uint32_t low,high;
  if(record!=0u){high=*(volatile uint32_t *)(record+20u);low=*(volatile uint32_t *)(record+16u);}
  else {uintptr_t current=opencfw_em9305_auxiliary_ready_303f68();current=*(volatile uint32_t *)(current+36u);high=*(volatile uint32_t *)(current+744u);low=*(volatile uint32_t *)(current+740u);}
  (void)opencfw_em9305_radio_address_write_3045e8(cursor,low,high);cursor=output+10u;present=1u;
 }
 if((forced&2u)!=0u||(record!=0u&&(allowed&2u)!=0u&&(*(volatile uint8_t *)(channels+123u)&2u)==0u)){
  uint32_t low,high;present|=2u;
  if(record!=0u){high=*(volatile uint32_t *)(record+28u);low=*(volatile uint32_t *)(record+24u);}
  else {uintptr_t current=opencfw_em9305_auxiliary_ready_303f68();current=*(volatile uint32_t *)(current+36u);high=*(volatile uint32_t *)(current+752u);low=*(volatile uint32_t *)(current+748u);}
  (void)opencfw_em9305_radio_address_write_3045e8(cursor,low,high);cursor+=6u;
  if(record==0u)goto address_done;
 }
 if(record!=0u&&((forced&8u)!=0u||((allowed&8u)!=0u&&((*(volatile uint8_t *)(channels+123u)&8u)==0u||(count!=0u&&*(volatile uint8_t *)channels!=0u))))){
  uint32_t value=*(volatile uint16_t *)(record+(count!=0u?706u:64u));present|=8u;
  *(volatile uint8_t *)cursor=(uint8_t)value;cursor+=2u;
  uint32_t phy=*(volatile uint8_t *)(record+66u);value&=0xf00u;
  *(volatile uint8_t *)(cursor-1u)=(uint8_t)(((phy<<12u)+value)>>8u);
 }
address_done:
 capacity=(uint32_t)(output-cursor)+257u;
 if((forced&32u)!=0u||(record!=0u&&(allowed&32u)!=0u&&(*(volatile uint8_t *)(channels+123u)&32u)==0u)){capacity=(uint32_t)(output-cursor)+239u;aux=1u;}
 if((allowed&64u)!=0u){
  if(type==4u&&record==0u)power=0u;
  else if(record!=0u&&(type==4u||type==7u)){power=(*(volatile uint8_t *)(channels+12u)&64u)!=0u;}
  else if(type==8u)power=1u;
  else if(record!=0u)power=(*(volatile uint16_t *)(record+32u)&64u)!=0u;
  if(power!=0u)capacity-=1u;
 }
 if(enabled==0u)capacity=0u;
 if(source!=0u){
  uint32_t used=*(volatile uint16_t *)(source+10u),total=*(volatile uint16_t *)source;remaining=total-used;
  if((allowed&16u)!=0u&&record!=0u&&*(volatile uint8_t *)(source+12u)==0u){uint32_t limit=*(volatile uint8_t *)(record+76u);if(capacity>limit)capacity=limit;}
 }else remaining=0u;
 if((forced&16u)!=0u)goto payload_field;
 if((allowed&16u)==0u)goto no_payload_field;
 if(capacity<(uint16_t)remaining)goto payload_field;
 /* Native BNC then delay CMP record, followed by late basic block324114. */
 if(record==0u||type!=4u||*(volatile uint8_t *)(channels+102u)==1u)goto no_payload_field;
 if(*(volatile uint8_t *)(channels+100u)==0u)goto no_payload_field;
payload_field:
 end=cursor+3u;present|=16u;goto extra_fields;
no_payload_field:
 end=cursor;cursor=0u;
extra_fields:
 if(aux!=0u&&record!=0u){(void)opencfw_em9305_compose_aux_encode_324438(record,end);end+=18u;present|=32u;}
 if(power!=0u&&record!=0u){
  int32_t requested=*(volatile int8_t *)(record+2314u);
  uint32_t actual=opencfw_em9305_command_radio_power_310230(requested,1u);
  *(volatile uint8_t *)end=(uint8_t)actual;end+=1u;present|=64u;
 }
 if(type==4u||type==7u||(record!=0u&&type==2u&&*(volatile uint8_t *)(record+2809u)!=0u)){
  uint32_t other=type!=2u;
  for(uint32_t index=0u;index<3u;++index){
   if(index==2u&&((record==0u)||other!=0u))continue;
   if(record==0u)continue;
   uintptr_t state=record+index*96u;
   if(*(volatile uint8_t *)(state+80u)!=1u)continue;
   uint32_t bytes=*(volatile uint8_t *)(state+82u);
   uint32_t room=(uint8_t)((uint32_t)(body-end)+64u);
   if(room<(uint8_t)(bytes+2u))continue;
   uint32_t n=opencfw_em9305_compose_actions_3352f4[index](record,end);end+=n;written=1u;
  }
 }
 if((present|written)==0u)end=body;
 if((uint16_t)remaining!=0u){
  uint32_t available=(uint32_t)(output-end)+257u;
  if(available<capacity)capacity=available;
  uint32_t used=*(volatile uint16_t *)(source+10u);
  if(capacity>(uint16_t)remaining)capacity=(uint16_t)remaining;
  *(volatile uint16_t *)(source+10u)=(uint16_t)(used+(uint8_t)capacity);
 }else capacity=0u;
 uint32_t extra=(uint32_t)(end-body);
 *(volatile uint8_t *)(header+4u)=(uint8_t)(capacity+extra+1u);
 (void)opencfw_em9305_radio_encode_3239d4(output,header);
 uint32_t first=prefix<<6u;
 if(type==1u){
  uint32_t flags=*(volatile uint8_t *)(record+2820u);first|=flags;
  *(volatile uint8_t *)(output+2u)=(uint8_t)first;
  uint32_t total=*(volatile uint16_t *)source;uintptr_t input=*(volatile uint32_t *)(source+4u);
  (void)opencfw_em9305_memcpy((void *)(body+(uint16_t)extra),(const void *)input,total);
  uint32_t used=*(volatile uint16_t *)(source+10u);total=*(volatile uint16_t *)source;
  used-=(uint8_t)capacity;end+=total;*(volatile uint16_t *)(source+10u)=(uint16_t)used;
 }else *(volatile uint8_t *)(output+2u)=(uint8_t)(first|extra);
 *(volatile uint8_t *)body=(uint8_t)present;
 if(record!=0u)(void)opencfw_em9305_compose_finalize_32412c(record,cursor,header,present,type);
 return (uint8_t)(end-output);
}
