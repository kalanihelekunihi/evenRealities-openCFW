/* Native32cb58..32cbec full slave update validation and instant publish. */
uint32_t opencfw_em9305_slave_phy_apply_32cb58(uintptr_t record)
{
 int32_t first=(int8_t)*(volatile uint8_t *)(uintptr_t)0x80281cu;
 if(first<0)return opencfw_em9305_receive_terminate_325c08(record,74u);
 int32_t second=(int8_t)*(volatile uint8_t *)(uintptr_t)0x80281du;
 if(second<0)return opencfw_em9305_receive_terminate_325c08(record,74u);
 if((first|second)==0)return opencfw_em9305_receive_terminate_325c08(record,110u);
 uint32_t anchor=*(volatile uint16_t *)(record+262u);
 uint32_t instant=*(volatile uint16_t *)(uintptr_t)0x80281eu;
 if((uint16_t)(instant-anchor)>=32767u)return opencfw_em9305_receive_terminate_325c08(record,73u);
 if(first!=0){
  uint32_t supported=opencfw_em9305_phy_supported_31b39c();
  if((supported&(uint32_t)first)==0u)return opencfw_em9305_receive_terminate_325c08(record,74u);
  second=*(volatile uint8_t *)(uintptr_t)0x80281du;
 }
 if((uint8_t)second!=0u){
  uint32_t supported=opencfw_em9305_phy_supported_31b39c();
  if((supported&(uint32_t)second)==0u)return opencfw_em9305_receive_terminate_325c08(record,74u);
 }
 uint32_t value=*(volatile uint8_t *)(uintptr_t)0x80281cu,valid=1u;
 if(value>=5u||((0x17u>>value)&1u)==0u){
  (void)opencfw_em9305_receive_terminate_325c08(record,74u);valid=0u;
 }
 value=*(volatile uint8_t *)(uintptr_t)0x80281du;
 if(value>=5u||value==3u)return opencfw_em9305_receive_terminate_325c08(record,74u);
 if(valid==0u)return 0u;
 uint32_t directions=*(volatile uint16_t *)(uintptr_t)0x80281cu;
 instant=*(volatile uint16_t *)(uintptr_t)0x80281eu;
 *(volatile uint16_t *)(record+722u)=(uint16_t)directions;
 *(volatile uint16_t *)(record+724u)=(uint16_t)instant;
 return instant;
}
