/* Complete native3205c4..320748. Source children preserve genuine contracts;
 * modulo uses selected named ARC REMU helper, including native zero-divisor behavior. */
uint32_t opencfw_em9305_init_callback_3205c4(uintptr_t object,uint32_t argument)
{
 uintptr_t record=*(volatile uint32_t *)(object+44u),extra=record+160u;
 if(*(volatile uint8_t *)(extra+28u)==0u)return 0u;
 uintptr_t output=*(volatile uint32_t *)(record+104u);
 if(output==0u)return 0u;
 uintptr_t input=argument;
 uint32_t index=*(volatile uint16_t *)(uintptr_t)0x803c0cu;
 uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 uint32_t offset=(uint32_t)(uint16_t)index*912u;
 uintptr_t slot=base+offset;
 uint32_t high=*(volatile uint32_t *)(extra+12u),low=*(volatile uint32_t *)(extra+8u);
 uint32_t origin=*(volatile uint32_t *)extra;
 uint32_t count=*(volatile uint8_t *)(record+185u);
 (void)opencfw_em9305_radio_address_write_3045e8(output+8u,low,high);
 uint32_t flags=*(volatile uint8_t *)(uintptr_t)0x803bd5u;
 uint32_t kind=*(volatile uint8_t *)(record+186u);
 uintptr_t descriptor=0x803d1cu;
 *(volatile uint8_t *)(descriptor+3u)=(uint8_t)kind;
 if((flags&2u)==0u){*(volatile uint32_t *)(uintptr_t)0x803c08u=0u;*(volatile uint32_t *)(uintptr_t)0x803c04u=0u;}
 else {
  _Alignas(4) uint32_t pair[2];uint32_t identity;
  if(*(volatile uint8_t *)(extra+24u)==1u){
   identity=*(volatile uint8_t *)input>>7u; /* delayed load precedes address-pack child */
   uint64_t packed=opencfw_em9305_controller_pack_address(input+8u);
   pair[0]=(uint32_t)packed;pair[1]=(uint32_t)(packed>>32u);
   if((pair[1]&0xc000u)==0x4000u){
    high=*(volatile uint32_t *)(extra+20u);low=*(volatile uint32_t *)(extra+16u);
    kind=*(volatile uint8_t *)(record+187u);
    *(volatile uint32_t *)(uintptr_t)0x803c08u=pair[1];
    *(volatile uint32_t *)(uintptr_t)0x803c04u=pair[0];
    (void)opencfw_em9305_radio_peer_set_303cc0(kind,low,high,(uintptr_t)pair);
   }else {*(volatile uint32_t *)(uintptr_t)0x803c08u=0u;*(volatile uint32_t *)(uintptr_t)0x803c04u=0u;}
  }else {
   pair[0]=*(volatile uint32_t *)(record+84u);pair[1]=*(volatile uint32_t *)(record+88u);
   high=*(volatile uint32_t *)(extra+20u);low=*(volatile uint32_t *)(extra+16u);
   kind=*(volatile uint8_t *)(record+187u);
   uint32_t previous=*(volatile uint32_t *)(record+80u);
   uint32_t found=opencfw_em9305_radio_peer_pair_303a40(kind,low,high,(uintptr_t)pair);
   if(found!=0u){identity=1u;*(volatile uint32_t *)(uintptr_t)0x803c08u=pair[1];*(volatile uint32_t *)(uintptr_t)0x803c04u=pair[0];}
   else {identity=(previous>>1u)&1u;*(volatile uint32_t *)(uintptr_t)0x803c08u=0u;*(volatile uint32_t *)(uintptr_t)0x803c04u=0u;}
  }
  output=*(volatile uint32_t *)(record+104u);
  (void)opencfw_em9305_radio_address_write_3045e8(output+2u,pair[0],pair[1]);
  *(volatile uint8_t *)(descriptor+2u)=(uint8_t)identity;
 }
 output=*(volatile uint32_t *)(record+104u);
 (void)opencfw_em9305_radio_encode_3239d4(output,descriptor);
 offset=(uint32_t)(uint16_t)index*912u;
 uintptr_t freshbase=*(volatile uint32_t *)(uintptr_t)0x805c70u;
 uint32_t stamp=origin+(count<<3u);
 uintptr_t originalslot=base+offset;
 uint32_t slotindex=opencfw_em9305_associated_slot_sdiv((uint32_t)(slot-freshbase),912u);
 uint32_t period=*(volatile uint16_t *)(originalslot+266u);
 uint32_t elapsed=opencfw_em9305_radio_schedule_313424((uint32_t)(uint16_t)period*1250u,(uint8_t)slotindex,stamp+1832u,0u,0u);
 struct opencfw_em9305_native_product_pair product=opencfw_em9305_native_mpydu_329154(elapsed,0x1a36e3u);
 period=*(volatile uint16_t *)(originalslot+266u);
 uint32_t scaled=((product.high<<1u)|(product.low>>31u))&0xffffu;
 uint32_t quotient=opencfw_em9305_schedule_remu(scaled,period);
 output=*(volatile uint32_t *)(record+104u);
 uint32_t duration=(uint32_t)(uint16_t)period*1250u;
 *(volatile uint8_t *)(output+22u)=(uint8_t)quotient;
 uint32_t remainder=opencfw_em9305_schedule_remu(elapsed,duration);
 output=*(volatile uint32_t *)(record+104u);
 *(volatile uint8_t *)(output+23u)=(uint8_t)(quotient>>8u);
 uint32_t next=remainder+stamp;
 uint32_t type=*(volatile uint8_t *)(descriptor+1u);
 next+=1832u;
 *(volatile uint16_t *)(uintptr_t)0x803c00u=(uint16_t)quotient;
 *(volatile uint32_t *)(originalslot+24u)=next;
 uint32_t enabled=0u;
 if(type==1u)enabled=(*(volatile uint8_t *)input&32u)!=0u;
 *(volatile uint8_t *)(uintptr_t)0x803c11u=(uint8_t)enabled;
 return 1u;
}
