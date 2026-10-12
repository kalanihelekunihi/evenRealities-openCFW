/* Native32eb34..32eec6: full vendor router. Sparse packet tails and scratch
 * outputs follow genuine provider writes; no invented response defaults. */
extern uint32_t opencfw_em9305_vendor_control_3101f0(uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_vendor_control_31035c(uint32_t);
extern uint32_t opencfw_em9305_vendor_control_310358(uint32_t);
extern uint32_t opencfw_em9305_vendor_command_30be48(uintptr_t);
extern uint32_t opencfw_em9305_vendor_command_30d87c(uintptr_t);
extern uint32_t opencfw_em9305_vendor_command_30d9b4(uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_vendor_command_31071c(uint32_t);
extern uint32_t opencfw_em9305_vendor_command_30cd5c(uint32_t);
extern uint32_t opencfw_em9305_vendor_command_30db24(uint32_t);
extern uint32_t opencfw_em9305_vendor_command_30e034(uint32_t);
extern uint32_t opencfw_em9305_vendor_allocator_second_313fa8(uint32_t);
extern uint32_t opencfw_em9305_vendor_query_30bc40(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_vendor_query_30e0d4(uint32_t);
extern uint32_t opencfw_em9305_vendor_query_313760(void);
extern uint32_t opencfw_em9305_vendor_query_30bb30(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_vendor_query_30bda4(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_vendor_query_30bd94(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_vendor_query_30be2c(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_vendor_query_30bc04(uintptr_t,uintptr_t,uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_vendor_query_30bb84(uintptr_t,uintptr_t,uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_vendor_snapshot_30329c(uintptr_t);
extern uint32_t opencfw_em9305_vendor_snapshot_3032c0(uintptr_t);
uint32_t opencfw_em9305_primary_vendor_32eb34(uintptr_t request,uintptr_t input)
{
 uint32_t command=*(volatile uint16_t *)request,length=1u,status=0u;
 _Alignas(4) uint8_t scratch[64];
 switch(command){
 case 0xfff0u:(void)opencfw_em9305_controller_set_address(input);break;
 case 0xffa0u:*(volatile uint8_t *)(uintptr_t)0x8058ccu=1u;break;
 case 0xffa1u:*(volatile uint8_t *)(uintptr_t)0x8057a8u=1u;break;
 case 0xffa2u:{uint32_t b3=*(volatile uint8_t *)(input+3u),b2=*(volatile uint8_t *)(input+2u),b1=*(volatile uint8_t *)(input+1u),b0=*(volatile uint8_t *)input;uint32_t result=opencfw_em9305_vendor_control_3101f0(b0,b1,(uint16_t)(b2+(b3<<8u)));status=result!=0u?0u:18u;break;}
 case 0xffa3u:{uint32_t result=opencfw_em9305_vendor_control_31035c(*(volatile uint8_t *)input);if(result!=0u)result=opencfw_em9305_vendor_control_310358(*(volatile uint8_t *)(input+1u));status=result!=0u?0u:18u;break;}
 case 0xffc0u:length=57u;break;
 case 0xffcdu:status=1u;break;
 case 0xfff1u:status=opencfw_em9305_vendor_command_30be48(input);length=7u;break;
 case 0xfff2u:status=opencfw_em9305_vendor_command_30d87c(input);break;
 case 0xfff3u:{uint32_t low,high=0u;uintptr_t enable_input;
  if(*(volatile uint8_t *)(request+2u)==5u){uint32_t b1=*(volatile uint8_t *)(input+1u),b0=*(volatile uint8_t *)input,b2=*(volatile uint8_t *)(input+2u),b3=*(volatile uint8_t *)(input+3u);low=b0+(b1<<8u)+(b2<<16u)+(b3<<24u);enable_input=input+4u;}
  else{uint64_t bits=opencfw_em9305_ll_pack64_304648(input);low=(uint32_t)bits;high=(uint32_t)(bits>>32u);enable_input=input+8u;}
  uint32_t enable=*(volatile uint8_t *)enable_input;status=opencfw_em9305_vendor_command_30d9b4(low,high,enable!=0u);break;}
 case 0xfff4u:length=39u;break;
 case 0xfff9u:(void)opencfw_em9305_vendor_command_31071c(*(volatile uint8_t *)input!=0u);break;
 case 0xfffau:length=35u;break;
 case 0xfffeu:length=29u;break;
 case 0xffffu:status=12u;break;
 case 0xffe1u:{uint64_t bits=opencfw_em9305_ll_pack64_304648(input);uint32_t flags=(uint32_t)bits,enabled=*(volatile uint8_t *)(input+8u)!=0u;
  if((flags&1u)!=0u)(void)opencfw_em9305_vendor_command_30cd5c(enabled);
  if((flags&8u)!=0u)(void)opencfw_em9305_vendor_command_30db24(enabled);
  if((flags&4u)!=0u){uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x805858u;if(callback!=0u)(void)((uint32_t (*)(uint32_t))callback)(enabled);}break;}
 case 0xffe6u:{uint32_t b1=*(volatile uint8_t *)(input+1u),b0=*(volatile uint8_t *)input,b2=*(volatile uint8_t *)(input+2u),b3=*(volatile uint8_t *)(input+3u);status=opencfw_em9305_vendor_command_30e034(b0+(b1<<8u)+(b2<<16u)+(b3<<24u));break;}
 default:return 0u;
 }
 uintptr_t packet=opencfw_em9305_ll_response_allocate_32e428(length,*(volatile uint16_t *)request);
 if(packet==0u)return 1u;
 *(volatile uint8_t *)packet=(uint8_t)status;
 uintptr_t payload=packet+1u;
 command=*(volatile uint16_t *)request;
 if(command==0xfffau){
  uint32_t value=opencfw_em9305_pal_status_secondary();
  *(volatile uint8_t *)payload=(uint8_t)value;
  *(volatile uint8_t *)(payload+1u)=(uint8_t)(value>>8u);
  value=opencfw_em9305_pal_pending_consume(0u);
  *(volatile uint8_t *)(payload+2u)=(uint8_t)value;
  value=opencfw_em9305_pal_pending_consume(0u);
  uint32_t shifted=value>>8u;
  *(volatile uint8_t *)(payload+3u)=(uint8_t)shifted;
  value=opencfw_em9305_controller_allocator_query(shifted);
  *(volatile uint8_t *)(payload+4u)=(uint8_t)value;
  *(volatile uint8_t *)(payload+7u)=(uint8_t)(value>>24u);
  *(volatile uint8_t *)(payload+6u)=(uint8_t)(value>>16u);
  shifted=value>>8u;
  *(volatile uint8_t *)(payload+5u)=(uint8_t)shifted;
  value=opencfw_em9305_vendor_allocator_second_313fa8(shifted);
  *(volatile uint8_t *)(payload+8u)=(uint8_t)value;
  *(volatile uint8_t *)(payload+10u)=(uint8_t)(value>>16u);
  *(volatile uint8_t *)(payload+9u)=(uint8_t)(value>>8u);
  *(volatile uint8_t *)(payload+11u)=(uint8_t)(value>>24u);
  *(volatile uint16_t *)scratch=0u;
  uint32_t prior=opencfw_em9305_vendor_query_30bc40((uintptr_t)scratch,(uintptr_t)(scratch+48u));
  uint32_t first=*(volatile uint16_t *)scratch,second=*(volatile uint16_t *)(scratch+48u);
  *(volatile uint8_t *)(payload+17u)=0u;
  *(volatile uint8_t *)(payload+12u)=(uint8_t)first;
  *(volatile uint8_t *)(payload+14u)=(uint8_t)second;
  *(volatile uint8_t *)(payload+16u)=0u;
  *(volatile uint8_t *)(payload+13u)=(uint8_t)(first>>8u);
  *(volatile uint8_t *)(payload+15u)=(uint8_t)(second>>8u);
  value=opencfw_em9305_vendor_query_30e0d4(prior);
  *(volatile uint8_t *)(payload+18u)=(uint8_t)value;
  *(volatile uint8_t *)(payload+19u)=(uint8_t)(value>>8u);
  value=opencfw_em9305_vendor_query_313760();
  uint32_t last=*(volatile uint16_t *)(uintptr_t)0x805838u;
  *(volatile uint8_t *)(payload+20u)=(uint8_t)value;
  *(volatile uint8_t *)(payload+22u)=(uint8_t)last;
  *(volatile uint8_t *)(payload+21u)=(uint8_t)(value>>8u);
  *(volatile uint8_t *)(payload+23u)=(uint8_t)(last>>8u);
 }else if(command==0xffc0u){
  *(volatile uint16_t *)scratch=0u;
  (void)opencfw_em9305_vendor_query_30bb30((uintptr_t)scratch,(uintptr_t)(scratch+48u));
  *(volatile uint8_t *)payload=*(volatile uint8_t *)scratch;
  uint32_t right=*(volatile uint16_t *)(scratch+48u),left=*(volatile uint8_t *)(scratch+1u);
  *(volatile uint16_t *)(scratch+46u)=0u;
  *(volatile uint8_t *)(payload+2u)=(uint8_t)right;
  *(volatile uint8_t *)(payload+1u)=(uint8_t)left;
  *(volatile uint8_t *)(payload+3u)=(uint8_t)(right>>8u);
  (void)opencfw_em9305_vendor_query_30bda4((uintptr_t)(scratch+46u),(uintptr_t)(scratch+62u));
  right=*(volatile uint16_t *)(scratch+62u);left=*(volatile uint16_t *)(scratch+46u);
  *(volatile uint8_t *)(payload+6u)=(uint8_t)right;
  *(volatile uint8_t *)(payload+4u)=(uint8_t)left;
  *(volatile uint8_t *)(payload+7u)=(uint8_t)(right>>8u);
  *(volatile uint16_t *)(scratch+44u)=0u;
  *(volatile uint8_t *)(payload+5u)=(uint8_t)(left>>8u);
  (void)opencfw_em9305_vendor_query_30bd94((uintptr_t)(scratch+44u),(uintptr_t)(scratch+60u));
  right=*(volatile uint16_t *)(scratch+60u);left=*(volatile uint16_t *)(scratch+44u);
  *(volatile uint8_t *)(payload+10u)=(uint8_t)right;
  *(volatile uint8_t *)(payload+8u)=(uint8_t)left;
  *(volatile uint8_t *)(payload+11u)=(uint8_t)(right>>8u);
  *(volatile uint16_t *)(scratch+42u)=0u;
  *(volatile uint8_t *)(payload+9u)=(uint8_t)(left>>8u);
  (void)opencfw_em9305_vendor_query_30be2c((uintptr_t)(scratch+42u),(uintptr_t)(scratch+58u));
  left=*(volatile uint16_t *)(scratch+42u);right=*(volatile uint16_t *)(scratch+58u);
  *(volatile uint8_t *)(payload+12u)=(uint8_t)left;
  *(volatile uint8_t *)(payload+14u)=(uint8_t)right;
  *(volatile uint8_t *)(payload+13u)=(uint8_t)(left>>8u);
  *(volatile uint8_t *)(payload+15u)=(uint8_t)(right>>8u);
  *(volatile uint8_t *)(scratch+41u)=0u;*(volatile uint8_t *)(scratch+40u)=0u;
  (void)opencfw_em9305_vendor_query_30bc04((uintptr_t)(scratch+41u),(uintptr_t)(scratch+56u),(uintptr_t)(scratch+40u),(uintptr_t)(scratch+54u));
  uint32_t a=*(volatile uint16_t *)(scratch+56u),b=*(volatile uint8_t *)(scratch+40u),c=*(volatile uint16_t *)(scratch+54u),d=*(volatile uint8_t *)(scratch+41u);
  *(volatile uint8_t *)(payload+20u)=(uint8_t)b;
  *(volatile uint8_t *)(payload+22u)=(uint8_t)c;
  *(volatile uint8_t *)(payload+16u)=(uint8_t)d;
  *(volatile uint8_t *)(payload+18u)=(uint8_t)a;
  *(volatile uint8_t *)(payload+19u)=(uint8_t)(a>>8u);
  *(volatile uint8_t *)(payload+23u)=(uint8_t)(c>>8u);
  *(volatile uint8_t *)(payload+17u)=0u;*(volatile uint8_t *)(payload+21u)=0u;
  *(volatile uint8_t *)(scratch+39u)=0u;*(volatile uint8_t *)(scratch+38u)=0u;
  (void)opencfw_em9305_vendor_query_30bb84((uintptr_t)(scratch+39u),(uintptr_t)(scratch+52u),(uintptr_t)(scratch+38u),(uintptr_t)(scratch+50u));
  a=*(volatile uint16_t *)(scratch+52u);c=*(volatile uint16_t *)(scratch+50u);d=*(volatile uint8_t *)(scratch+39u);b=*(volatile uint8_t *)(scratch+38u);
  *(volatile uint8_t *)(payload+26u)=(uint8_t)a;
  *(volatile uint8_t *)(payload+30u)=(uint8_t)c;
  *(volatile uint8_t *)(payload+25u)=0u;*(volatile uint8_t *)(payload+29u)=0u;
  *(volatile uint8_t *)(payload+24u)=(uint8_t)d;
  *(volatile uint8_t *)(payload+28u)=(uint8_t)b;
  *(volatile uint8_t *)(payload+27u)=(uint8_t)(a>>8u);
  *(volatile uint8_t *)(payload+31u)=(uint8_t)(c>>8u);
 }else if(command==0xfff4u){
  (void)opencfw_em9305_vendor_snapshot_30329c((uintptr_t)scratch);
  (void)opencfw_em9305_memcpy((void *)payload,scratch,38u);
 }else if(command==0xfffeu){
  (void)opencfw_em9305_vendor_snapshot_3032c0((uintptr_t)scratch);
  (void)opencfw_em9305_memcpy((void *)payload,scratch,28u);
 }
 (void)opencfw_em9305_ll_event_send(packet-5u);
 return 1u;
}
