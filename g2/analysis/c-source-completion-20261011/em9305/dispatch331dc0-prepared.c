extern uint32_t opencfw_em9305_command_vendor_byte_30cee4(int32_t);
extern void opencfw_em9305_command_product_version_303258(uintptr_t);
extern uint32_t opencfw_em9305_command_advertising_parameters_30ce18(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uintptr_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_command_advertising_data_30cdd8(uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_command_scan_response_30df98(uint32_t,uintptr_t);
extern void opencfw_em9305_command_advertising_enable_30aff8(uint32_t);
extern uint32_t opencfw_em9305_command_advertising_power_30bb50(uintptr_t);
/* Native331f00..331f5c: vendor-byte status and 32-byte version command. */
uint32_t opencfw_em9305_dispatch_331f00(uintptr_t request,uintptr_t input)
{
 uint32_t command=*(volatile uint16_t *)request;
 if(command!=0xfffbu&&command!=0xfff5u)return 0u;
 uint32_t size=33u,opcode=0xfffbu;
 if(command==0xfff5u){(void)opencfw_em9305_command_vendor_byte_30cee4((int8_t)*(volatile uint8_t *)input);size=1u;opcode=*(volatile uint16_t *)request;}
 uintptr_t response=opencfw_em9305_ll_response_allocate_32e428(size,opcode);
 if(response==0u)return 1u;
 *(volatile uint8_t *)response=0u;
 uintptr_t cursor=response+1u;
 if(*(volatile uint16_t *)request==0xfffbu){uint8_t version[32] __attribute__((aligned(4)));opencfw_em9305_command_product_version_303258((uintptr_t)version);(void)opencfw_em9305_memcpy((void *)cursor,version,32u);}
 (void)opencfw_em9305_ll_event_send(cursor-6u);
 return 1u;
}
/* Native331dc0..331ec0: full five-command dispatcher and vendor prefix. */
uint32_t opencfw_em9305_dispatch_331dc0(uintptr_t request,uintptr_t input)
{
 if(opencfw_em9305_dispatch_331f00(request,input)!=0u)return 1u;
 uint32_t command=*(volatile uint16_t *)request;
 if(command-0x2006u>=5u)return 0u;
 uint32_t status=0u,size=1u;
 if(command==0x2006u){
  uint32_t h0=*(volatile uint8_t *)(input+3u),h1=*(volatile uint8_t *)(input+1u),l0=*(volatile uint8_t *)(input+2u),l1=*(volatile uint8_t *)input;
  uint32_t type=*(volatile uint8_t *)(input+4u),own=*(volatile uint8_t *)(input+5u),peer=*(volatile uint8_t *)(input+6u);
  uint8_t address[6];(void)opencfw_em9305_memcpy(address,(const void *)(input+7u),6u);
  uint32_t channels=*(volatile uint8_t *)(input+13u),filter=*(volatile uint8_t *)(input+14u);
  status=opencfw_em9305_command_advertising_parameters_30ce18((uint16_t)((h1<<8)+l1),(uint16_t)((h0<<8)+l0),type,own,peer,(uintptr_t)address,channels,filter);
 }else if(command==0x2007u)size=2u;
 else if(command==0x2008u)status=opencfw_em9305_command_advertising_data_30cdd8(*(volatile uint8_t *)input,input+1u);
 else if(command==0x2009u)status=opencfw_em9305_command_scan_response_30df98(*(volatile uint8_t *)input,input+1u);
 else {opencfw_em9305_command_advertising_enable_30aff8(*(volatile uint8_t *)input);return 1u;}
 uintptr_t response=opencfw_em9305_ll_response_allocate_32e428(size,*(volatile uint16_t *)request);
 if(response==0u)return 1u;
 command=*(volatile uint16_t *)request;
 if(command-0x2008u<2u||command==0x2006u)*(volatile uint8_t *)response=(uint8_t)status;
 else if(command==0x2007u){uint8_t power=0u;uint32_t result=opencfw_em9305_command_advertising_power_30bb50((uintptr_t)&power);*(volatile uint8_t *)response=(uint8_t)result;*(volatile uint8_t *)(response+1u)=power;}
 (void)opencfw_em9305_ll_event_send(response-5u);
 return 1u;
}
