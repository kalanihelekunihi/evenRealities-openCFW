extern uint32_t opencfw_em9305_command_vendor_mode_30d5a8(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_command_vendor_option_30d75c(uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_command_vendor_mask_30cf28(uint32_t,uint32_t);
/* Native30be3c branches306f70/306f8c: genuine two-register64-bit result. */
uint64_t opencfw_em9305_command_vendor_statistics_30be3c(uint32_t id,uint32_t associated)
{
 uint32_t high=0u,low=0u;
 if(associated!=0u){uintptr_t record=opencfw_em9305_radio_record_find_31aa64((uint8_t)id);if(record!=0u){high=*(volatile uint32_t *)(record+724u);low=*(volatile uint32_t *)(record+720u);}}
 else if(id<6u){uint32_t offset=opencfw_em9305_config_limit_mpyuw(id,784u);uintptr_t row=0x803ffcu+offset;low=*(volatile uint32_t *)row;high=*(volatile uint32_t *)(row+4u);}
 return ((uint64_t)high<<32)|low;
}
/* Native303264..303270: live product36-byte snapshot, actual forward copy. */
void opencfw_em9305_command_vendor_snapshot_303264(uintptr_t output)
{(void)opencfw_em9305_memcpy((void *)output,(const void *)(uintptr_t)0x8014f4u,36u);}
/* Native3328c8..3329b0: five vendor commands and fresh response opcode. */
uint32_t opencfw_em9305_dispatch_3328c8(uintptr_t request,uintptr_t input)
{
 uint32_t command=*(volatile uint16_t *)request,status=0u,size=1u,id=0u,associated=0u;
 switch(command){
 case 0xffd0u:{uint32_t c=*(volatile uint8_t *)(input+2u),b=*(volatile uint8_t *)(input+1u),d=*(volatile uint8_t *)(input+3u),e=*(volatile uint8_t *)(input+4u),a=*(volatile uint8_t *)input;uint32_t mask=b+(c<<8)+(d<<16)+(e<<24);status=opencfw_em9305_command_vendor_mask_30cf28(a,mask);break;}
 case 0xffd1u:{uint32_t b=*(volatile uint8_t *)(input+1u),a=*(volatile uint8_t *)input;status=opencfw_em9305_command_vendor_mode_30d5a8(a,b);break;}
 case 0xffd2u:{uint32_t c=*(volatile uint8_t *)(input+2u),b=*(volatile uint8_t *)(input+1u),a=*(volatile uint8_t *)input;status=opencfw_em9305_command_vendor_option_30d75c(a,b,c);break;}
 case 0xffdau:size=37u;break;
 case 0xffdeu:{uint32_t high=*(volatile uint8_t *)(input+1u),low=*(volatile uint8_t *)input,selector=*(volatile uint8_t *)(input+2u);id=low+(high<<8);associated=selector!=0u;size=6u;break;}
 default:return 0u;
 }
 uintptr_t response=opencfw_em9305_ll_response_allocate_32e428(size,*(volatile uint16_t *)request);if(response==0u)return 1u;
 *(volatile uint8_t *)response=(uint8_t)status;uintptr_t cursor=response+1u;
 command=*(volatile uint16_t *)request;
 if(command==0xffdau){uint8_t snapshot[36] __attribute__((aligned(4)));opencfw_em9305_command_vendor_snapshot_303264((uintptr_t)snapshot);(void)opencfw_em9305_memcpy((void *)cursor,snapshot,36u);}
 else if(command==0xffdeu){uint64_t counters=opencfw_em9305_command_vendor_statistics_30be3c((uint16_t)id,associated);*(volatile uint8_t *)(cursor+4u)=(uint8_t)(counters>>32u);*(volatile uint8_t *)cursor=(uint8_t)counters;*(volatile uint8_t *)(cursor+3u)=(uint8_t)(counters>>24u);*(volatile uint8_t *)(cursor+2u)=(uint8_t)(counters>>16u);*(volatile uint8_t *)(cursor+1u)=(uint8_t)(counters>>8u);}
 (void)opencfw_em9305_ll_event_send(cursor-6u);return 1u;
}
