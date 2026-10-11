/* Native330f08..330f46: three mixed-width reloads per word preserve aliases. */
uint32_t opencfw_em9305_ll_test_response_330f08(uintptr_t packet,uint32_t status,uint32_t id,uintptr_t input)
{
 *(volatile uint8_t *)(packet+1u)=(uint8_t)id;
 *(volatile uint8_t *)packet=(uint8_t)status;
 *(volatile uint8_t *)(packet+2u)=(uint8_t)(id>>8u);
 for(uint32_t index=0u;index<3u;++index) {
  uintptr_t source=input+4u*index,destination=packet+3u+4u*index;
  *(volatile uint8_t *)destination=(uint8_t)*(volatile uint32_t *)source;
  *(volatile uint8_t *)(destination+1u)=(uint8_t)(*(volatile uint32_t *)source>>8u);
  *(volatile uint8_t *)(destination+2u)=(uint8_t)*(volatile uint16_t *)(source+2u);
  *(volatile uint8_t *)(destination+3u)=*(volatile uint8_t *)(source+3u);
 }
 return (uint32_t)packet;
}
