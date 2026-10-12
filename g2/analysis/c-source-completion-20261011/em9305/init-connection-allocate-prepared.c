/* Complete native316c58..316e58 connection allocator. Count is byte34;
 * slot stride uses native MPYWHL. Final base reload is deliberate. */
uintptr_t opencfw_em9305_init_connection_allocate_316c58(void)
{
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t count=*(volatile uint8_t *)(config+34u);
 if(count==0u)return 0u;
 uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u,slot=0u;
 uint32_t index;
 for(index=0u;index<count;index++){
  slot=base+opencfw_em9305_native_mpywhl(index,912u);
  if(*(volatile uint8_t *)slot==0u)break;
 }
 if(index==count)return 0u;
 uintptr_t header=slot+544u;
 (void)opencfw_em9305_memset((void *)slot,0u,912u);
 uint32_t handler=*(volatile uint8_t *)(uintptr_t)0x805b18u;
 uint32_t upper=*(volatile uint32_t *)(uintptr_t)0x805a94u;
 uint32_t lower=*(volatile uint32_t *)(uintptr_t)0x805a98u;
 uint32_t access=*(volatile uint32_t *)(uintptr_t)0x805a84u;
 uint32_t crc=*(volatile uint32_t *)(uintptr_t)0x805a88u;
 *(volatile uint16_t *)(slot+502u)=0x5401u;
 *(volatile uint16_t *)(slot+482u)=0x5301u;
 *(volatile uint16_t *)(slot+390u)=0x4701u;
 *(volatile uint16_t *)(header+190u)=0x5101u;
 config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 *(volatile uint16_t *)(header+36u)=328u;
 uint32_t cap=*(volatile uint16_t *)(config+38u);
 *(volatile uint16_t *)(header+32u)=328u;
 *(volatile uint32_t *)(slot+8u)=crc;
 if(cap>251u)cap=251u;
 uint32_t first=*(volatile uint16_t *)(uintptr_t)0x805ab6u;
 uint32_t second=*(volatile uint16_t *)(uintptr_t)0x805ab8u;
 *(volatile uint16_t *)(header+22u)=(uint16_t)cap;
 *(volatile uint16_t *)(header+24u)=(uint16_t)((cap<<6u)+976u);
 *(volatile uint8_t *)slot=1u;
 *(volatile uint16_t *)(slot+388u)=(uint16_t)index;
 *(volatile uint16_t *)(slot+480u)=(uint16_t)index;
 *(volatile uint16_t *)(slot+500u)=(uint16_t)index;
 *(volatile uint16_t *)(header+188u)=(uint16_t)index;
 *(volatile uint16_t *)(header+34u)=27u;
 *(volatile uint16_t *)(header+30u)=27u;
 *(volatile uint32_t *)(slot+4u)=access;
 *(volatile uint32_t *)(slot+548u)=lower;
 *(volatile uint32_t *)(slot+544u)=upper;
 *(volatile uint32_t *)(slot+540u)=lower;
 *(volatile uint32_t *)(slot+536u)=upper;
 *(volatile uint8_t *)(header-148u)=(uint8_t)handler;
 *(volatile uint8_t *)(header+196u)=(uint8_t)handler;
 *(volatile uint8_t *)(slot+488u)=(uint8_t)handler;
 *(volatile uint8_t *)(header-36u)=(uint8_t)handler;
 *(volatile uint16_t *)(header+26u)=(uint16_t)first;
 *(volatile uint16_t *)(header+28u)=(uint16_t)second;
 *(volatile uint16_t *)(slot+76u)=257u;
 first=opencfw_em9305_radio_limit_317b10(slot,slot+574u);
 *(volatile uint16_t *)(header+48u)=(uint16_t)first;
 second=opencfw_em9305_radio_limit_317b10(slot,slot+566u);
 uint32_t value=*(volatile uint32_t *)(uintptr_t)0x805accu;
 uint32_t interval=*(volatile uint16_t *)(uintptr_t)0x805ac8u;
 uint32_t accuracy=*(volatile uint8_t *)(uintptr_t)0x805acbu;
 uint32_t flags=*(volatile uint8_t *)(uintptr_t)0x805aa8u;
 uint32_t option=*(volatile uint8_t *)(uintptr_t)0x805acau;
 *(volatile uint16_t *)(header+46u)=(uint16_t)second;
 *(volatile uint8_t *)(header+54u)=2u;
 *(volatile uint8_t *)(header+55u)=2u;
 *(volatile uint8_t *)(header+56u)=2u;
 *(volatile uint16_t *)(header+50u)=(uint16_t)interval;
 *(volatile uint32_t *)(slot+616u)=value;
 uintptr_t callbacks=*(volatile uint32_t *)(uintptr_t)0x805cd8u;
 *(volatile uint8_t *)(header-142u)=6u;
 *(volatile uint8_t *)(header+52u)=(uint8_t)option;
 *(volatile uint8_t *)(header+202u)=(uint8_t)flags;
 *(volatile uint8_t *)(header+70u)=(uint8_t)accuracy;
 if(callbacks!=0u){uintptr_t callback=*(volatile uint32_t *)callbacks;if(callback!=0u)(void)((uint32_t(*)(uint32_t,uintptr_t))callback)((uint16_t)index,callback);}
 if((*(volatile uint8_t *)(header+4u)&2u)!=0u){
  uint32_t control=*(volatile uint8_t *)(uintptr_t)0x805a85u;
  if((control&128u)!=0u){
   uintptr_t original=base+opencfw_em9305_native_mpywhl(index,912u);
   config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
   value=*(volatile uint8_t *)(config+66u);
   *(volatile uint8_t *)(original+778u)=(uint8_t)value;
   config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
   *(volatile uint32_t *)(original+824u)=0u;
   *(volatile uint8_t *)(original+770u)=1u;
   *(volatile uint8_t *)(original+769u)=0u;
   value=*(volatile uint8_t *)(config+67u);
   *(volatile uint8_t *)(original+833u)=0u;
   *(volatile uint16_t *)(original+822u)=0u;
   *(volatile uint8_t *)(original+564u)=255u;
   *(volatile uint8_t *)(original+563u)=255u;
   *(volatile uint8_t *)(original+562u)=255u;
   *(volatile uint8_t *)(original+561u)=255u;
   *(volatile uint16_t *)(original+776u)=0u;
   *(volatile uint32_t *)(original+784u)=0u;
   *(volatile uint8_t *)(original+793u)=0u;
   *(volatile uint16_t *)(original+780u)=0u;
   *(volatile uint8_t *)(original+779u)=(uint8_t)value;
  }
 }
 uintptr_t original=base+opencfw_em9305_native_mpywhl(index,912u);
 value=*(volatile uint32_t *)(uintptr_t)0x805ad0u;
 *(volatile uint32_t *)(original+836u)=value;
 value=*(volatile uint32_t *)(uintptr_t)0x805ad4u;
 *(volatile uint32_t *)(original+840u)=value;
 value=*(volatile uint16_t *)(uintptr_t)0x805ad8u;
 *(volatile uint16_t *)(original+846u)=1u;
 *(volatile uint16_t *)(original+844u)=(uint16_t)value;
 (void)opencfw_em9305_command_count_30e4bc();
 value=*(volatile uint8_t *)(uintptr_t)0x805a70u;
 *(volatile uint8_t *)(uintptr_t)0x805a70u=(uint8_t)(value+1u);
 (void)opencfw_em9305_common_request_30455c(1u);
 base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 return base+opencfw_em9305_native_mpywhl(index,912u);
}
