/* Native32e5d4..32e914: primary HCI command dispatch. Stack projections
 * intentionally retain native unwritten padding; helper/data contracts remain explicit. */
extern uint32_t opencfw_em9305_primary_vendor_32eb34(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_primary_private_304afc(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_primary_response_32e918(uintptr_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_primary_reset_mode_310718(uint32_t);
extern uint32_t opencfw_em9305_ll_special_mode_initialize(uint32_t);
extern uint32_t opencfw_em9305_command_primary_30de38(uintptr_t);
extern uint32_t opencfw_em9305_command_primary_30b190(uint32_t);
extern uint32_t opencfw_em9305_command_primary_30af98(uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_command_primary_30cac4(uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_primary_masks_332b60(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_command_primary_30e3ec(int32_t,int32_t);
extern uint32_t opencfw_em9305_command_primary_30d528(uint32_t);
extern uint32_t opencfw_em9305_command_primary_30d8a0(uint32_t,uint32_t);
uint32_t opencfw_em9305_ll_command_primary(uintptr_t request,uintptr_t input)
{
 if(opencfw_em9305_primary_vendor_32eb34(request,input)!=0u)return 1u;
 if(opencfw_em9305_primary_private_304afc(request,input)!=0u)return 1u;
 uint32_t command=*(volatile uint16_t *)request,status=0u,length=9u;
 _Alignas(4) uint8_t scratch[20];
 switch(command){
 case 0x0c03u:{uint32_t value=opencfw_em9305_primary_reset_mode_310718(2u);uintptr_t result=opencfw_em9305_ll_special_mode_initialize(value);(void)result;(void)opencfw_em9305_memset((void *)(uintptr_t)0x8056e8u,0u,24u);return 1u;}
 case 0x0c01u:(void)opencfw_em9305_primary_masks_332b60(0x8056e8u,input);length=1u;break;
 case 0x0c63u:(void)opencfw_em9305_primary_masks_332b60(0x8056f0u,input);length=1u;break;
 case 0x2001u:(void)opencfw_em9305_primary_masks_332b60(0x8056f8u,input);length=1u;break;
 case 0x0c48u:case 0x200fu:length=2u;break;
 case 0x0c49u:*(volatile uint8_t *)(uintptr_t)0x80571au=*(volatile uint8_t *)input;length=1u;break;
 case 0x2002u:length=4u;break;
 case 0x2005u:status=opencfw_em9305_command_primary_30de38(input);length=1u;break;
 case 0x2010u:status=opencfw_em9305_command_primary_30b190(command);length=1u;break;
 case 0x2011u:status=opencfw_em9305_command_primary_30af98(*(volatile uint8_t *)input,input+1u);length=1u;break;
 case 0x2012u:status=opencfw_em9305_command_primary_30cac4(*(volatile uint8_t *)input,input+1u);length=1u;break;
 case 0x201du:{uint32_t id=*(volatile uint8_t *)input;*(volatile uint8_t *)(scratch+8u)=(uint8_t)id;*(volatile uint16_t *)scratch=0u;*(volatile uint32_t *)(scratch+16u)=0u;*(volatile uint8_t *)(scratch+14u)=2u;*(volatile uint16_t *)(scratch+10u)=0u;*(volatile uint8_t *)(scratch+9u)=1u;*(volatile uint32_t *)(scratch+4u)=0x71764129u;*(volatile uint16_t *)(scratch+12u)=256u;status=opencfw_em9305_command_30cba0((uintptr_t)scratch);length=1u;break;}
 case 0x201eu:{uint32_t b2=*(volatile uint8_t *)(input+2u),b0=*(volatile uint8_t *)input,b1=*(volatile uint8_t *)(input+1u);*(volatile uint8_t *)(scratch+4u)=(uint8_t)b2;*(volatile uint16_t *)scratch=0u;*(volatile uint32_t *)(scratch+12u)=0u;*(volatile uint8_t *)(scratch+8u)=2u;*(volatile uint16_t *)(scratch+6u)=0u;*(volatile uint8_t *)(scratch+5u)=1u;*(volatile uint8_t *)(scratch+16u)=127u;*(volatile uint8_t *)(scratch+2u)=(uint8_t)b0;*(volatile uint8_t *)(scratch+3u)=(uint8_t)b1;status=opencfw_em9305_command_30e120((uintptr_t)scratch);length=1u;break;}
 case 0x201fu:case 0x204bu:length=3u;break;
 case 0x204cu:length=5u;break;
 case 0x204du:{uint32_t b1=*(volatile uint8_t *)(input+1u),b3=*(volatile uint8_t *)(input+3u),b0=*(volatile uint8_t *)input,b2=*(volatile uint8_t *)(input+2u);status=opencfw_em9305_command_primary_30e3ec((int16_t)(b0+(b1<<8u)),(int16_t)(b2+(b3<<8u)));length=1u;break;}
 case 0x204fu:{uint32_t b[7];b[6]=*(volatile uint8_t *)(input+6u);for(uint32_t i=0u;i<6u;i++)b[i]=*(volatile uint8_t *)(input+i);*(volatile uint8_t *)(scratch+14u)=(uint8_t)b[6];*(volatile uint16_t *)scratch=0u;*(volatile uint32_t *)(scratch+4u)=0x71764129u;*(volatile uint32_t *)(scratch+16u)=(uint32_t)(input+7u);for(uint32_t i=0u;i<6u;i++)*(volatile uint8_t *)(scratch+8u+i)=(uint8_t)b[i];status=opencfw_em9305_command_30cba0((uintptr_t)scratch);length=1u;break;}
 case 0x2050u:{uint32_t b[7];b[1]=*(volatile uint8_t *)(input+1u);b[0]=*(volatile uint8_t *)input;for(uint32_t i=2u;i<7u;i++)b[i]=*(volatile uint8_t *)(input+i);*(volatile uint8_t *)(scratch+3u)=(uint8_t)b[1];*(volatile uint16_t *)scratch=0u;*(volatile uint8_t *)(scratch+16u)=127u;*(volatile uint32_t *)(scratch+12u)=(uint32_t)(input+7u);*(volatile uint8_t *)(scratch+2u)=(uint8_t)b[0];for(uint32_t i=2u;i<7u;i++)*(volatile uint8_t *)(scratch+2u+i)=(uint8_t)b[i];status=opencfw_em9305_command_30e120((uintptr_t)scratch);length=1u;break;}
 case 0x0c82u:{uint32_t b1=*(volatile uint8_t *)(input+1u),b0=*(volatile uint8_t *)input;status=opencfw_em9305_command_primary_30d528((uint16_t)(b0+(b1<<8u)));length=1u;break;}
 case 0x0c84u:{uint32_t value=*(volatile uint8_t *)input;status=value!=0u&&value<17u?17u:0u;length=1u;break;}
 case 0x2074u:{uint32_t b1=*(volatile uint8_t *)(input+1u),b0=*(volatile uint8_t *)input;status=opencfw_em9305_command_primary_30d8a0(b0,b1!=0u);length=1u;break;}
 case 0x205fu:status=12u;length=1u;break;
 case 0x207bu:status=1u;length=1u;break;
 case 0x1002u:length=65u;break;
 case 0x1009u:length=7u;break;
 case 0u:length=1u;break;
 case 0x1001u:case 0x1003u:case 0x2003u:case 0x2018u:case 0x201cu:break;
 default:return 0u;
 }
 (void)opencfw_em9305_primary_response_32e918(request,(uint8_t)status,length);
 return 1u;
}
