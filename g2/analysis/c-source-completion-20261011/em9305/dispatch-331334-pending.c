/* Authenticated full dispatch331334..3316e0. Both fragment loops retain
 * fresh capacity/count checks, native DSP preflight and overflow marker. */
uint32_t opencfw_em9305_dispatch_331334(uintptr_t input)
{
 uint32_t type=*(volatile uint8_t *)(input+2u);
 uintptr_t event;
 if(type==32u||type==52u){
  uint32_t flags=*(volatile uint8_t *)(uintptr_t)0x8056fcu;
  if((flags&(type==32u?16u:128u))==0u)return 0u;
  if((*(volatile uint8_t *)(uintptr_t)0x8056efu&32u)==0u)return 0u;
  uint32_t remaining,needed;
  uintptr_t cursor;
  if(type==32u){
   if(*(volatile uint8_t *)(input+18u)==255u)return 0u;
   remaining=*(volatile uint16_t *)(input+10u);
   uint32_t quotient,negative_product;
   __asm__ volatile("divu %0,%1,247":"=r"(quotient):"r"(remaining));
   __asm__ volatile("mpyw %0,%1,-247":"=r"(negative_product):"r"(quotient));
   needed=(uint8_t)(quotient+((uint16_t)negative_product!=(uint16_t)(0u-remaining)));
  }else{
   remaining=*(volatile uint8_t *)(input+13u);
   register uint32_t nr0 __asm__("r0");
   register uint32_t nr1 __asm__("r1");
   register uint32_t nr2 __asm__("r2")=remaining;
   __asm__ volatile("mov r0,243\n\tcmp r2,244\n\tsetlo r1,r0,r2\n\tmov r0,r2\n\tadd.nc r0,r0,12\n\textb.f 0,r0\n\tadd.ne r1,r1,1\n\textb r1,r1":"=&r"(nr0),"=&r"(nr1):"r"(nr2):"cc");
   needed=nr1;
  }
  uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
  uint32_t count=*(volatile uint8_t *)(uintptr_t)0x805718u;
  if(needed+count>*(volatile uint8_t *)(config+14u))return 0u;
  cursor=*(volatile uint32_t *)(input+(type==32u?12u:16u));
  uint32_t capped=0u;
  do{
   config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
   count=*(volatile uint8_t *)(uintptr_t)0x805718u;
   uint32_t chunk=remaining<244u?remaining:244u;
   if(count>=*(volatile uint8_t *)(config+14u))return 0u;
   event=type==32u?opencfw_em9305_ll_fragment_allocate_32e48c(62u,(uint8_t)(chunk+11u)):opencfw_em9305_ll_fragment_allocate_32e4a8(62u,(uint8_t)(chunk+11u));
   if(event==0u)return 0u;
   config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
   count=*(volatile uint8_t *)(uintptr_t)0x805718u;
   remaining-=chunk;
   capped=((uint8_t)(count+1u)==*(volatile uint8_t *)(config+14u))&&(remaining!=0u);
   *(volatile uint8_t *)(uintptr_t)0x805718u=(uint8_t)(count+1u);
   if(capped){remaining=0u;*(volatile uint8_t *)(input+(type==32u?9u:12u))=2u;}
   uintptr_t end=cursor+chunk;
   if(type==32u){
    uintptr_t original=*(volatile uint32_t *)(input+12u);
    uint32_t total=*(volatile uint16_t *)(input+10u),status=1u;
    if(total==(uint16_t)(end-original)){
     uint32_t mode=*(volatile uint8_t *)(input+9u);
     status=mode==255u?0xffffffffu:mode==2u?2u:0u;
    }
    *(volatile uint8_t *)event=37u;
    *(volatile uint8_t *)(event+1u)=*(volatile uint8_t *)(input+4u);
    *(volatile uint8_t *)(event+2u)=*(volatile uint8_t *)(input+5u);
    *(volatile uint8_t *)(event+3u)=*(volatile uint8_t *)(input+6u);
    *(volatile uint8_t *)(event+4u)=*(volatile uint8_t *)(input+7u);
    *(volatile uint8_t *)(event+5u)=*(volatile uint8_t *)(input+8u);
    *(volatile uint8_t *)(event+6u)=*(volatile uint8_t *)(input+16u);
    *(volatile uint8_t *)(event+7u)=*(volatile uint8_t *)(input+17u);
    uint32_t captured=*(volatile uint8_t *)(input+18u);
    *(volatile uint8_t *)(event+10u)=(uint8_t)chunk;
    *(volatile uint8_t *)(event+9u)=(uint8_t)status;
    *(volatile uint8_t *)(event+8u)=(uint8_t)captured;
    if(chunk!=0u)(void)opencfw_em9305_memcpy((void *)(event+11u),(const void *)cursor,chunk);
   }else (void)opencfw_em9305_ll_fragment_format_330f48(event,input,cursor,(uint8_t)chunk);
   (void)opencfw_em9305_ll_event_send(event-2u);
   cursor=end;
  }while(remaining!=0u);
  return capped^1u;
 }
 uint32_t bit,length,opcode;
 if(type==5u){bit=1u;length=34u;opcode=41u;}
 else if(type==30u){bit=8u;length=20u;opcode=36u;}
 else if(type==38u){bit=32u;length=24u;opcode=38u;}
 else if(type==53u){bit=64u;length=4u;opcode=39u;}
 else return 0u;
 uintptr_t flag_address=type==5u?0x8056fdu:0x8056fcu;
 if((*(volatile uint8_t *)flag_address&bit)==0u)return 0u;
 if((*(volatile uint8_t *)(uintptr_t)0x8056efu&32u)==0u)return 0u;
 if(type==5u){
  uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
  if(*(volatile uint8_t *)(config+4u)<13u)return 0u;
 }else if(type==30u&&*(volatile uint8_t *)(input+21u)==0u)return 0u;
 else if(type==38u&&*(volatile uint8_t *)(input+25u)==0u)return 0u;
 event=opencfw_em9305_ll_event_allocate(62u,length);
 if(event==0u)return 0u;
 *(volatile uint8_t *)event=(uint8_t)opcode;
 if(type==53u){
  *(volatile uint8_t *)(event+1u)=*(volatile uint8_t *)(input+4u);
  *(volatile uint8_t *)(event+2u)=*(volatile uint8_t *)(input+5u);
  *(volatile uint8_t *)(event+3u)=*(volatile uint8_t *)(input+6u);
 }
 if(type==5u){
  *(volatile uint8_t *)(event+1u)=*(volatile uint8_t *)(input+4u);
  *(volatile uint8_t *)(event+2u)=*(volatile uint8_t *)(input+6u);
  *(volatile uint8_t *)(event+3u)=*(volatile uint8_t *)(input+7u);
  *(volatile uint8_t *)(event+4u)=*(volatile uint8_t *)(input+8u);
  *(volatile uint8_t *)(event+5u)=*(volatile uint8_t *)(input+9u);
  (void)opencfw_em9305_radio_address_copy_304604(event+6u,input+10u);
  (void)opencfw_em9305_radio_address_copy_304604(event+12u,input+23u);
  (void)opencfw_em9305_radio_address_copy_304604(event+18u,input+29u);
  *(volatile uint8_t *)(event+24u)=*(volatile uint8_t *)(input+16u);
  *(volatile uint8_t *)(event+25u)=*(volatile uint8_t *)(input+17u);
  *(volatile uint8_t *)(event+26u)=*(volatile uint8_t *)(input+18u);
  *(volatile uint8_t *)(event+27u)=*(volatile uint8_t *)(input+19u);
  *(volatile uint8_t *)(event+28u)=*(volatile uint8_t *)(input+20u);
  *(volatile uint8_t *)(event+29u)=*(volatile uint8_t *)(input+21u);
  *(volatile uint8_t *)(event+30u)=*(volatile uint8_t *)(input+22u);
  *(volatile uint8_t *)(event+31u)=*(volatile uint8_t *)(input+35u);
  *(volatile uint8_t *)(event+32u)=*(volatile uint8_t *)(input+36u);
  *(volatile uint8_t *)(event+33u)=*(volatile uint8_t *)(input+37u);
 }
 if(type==30u){
  *(volatile uint8_t *)(event+1u)=*(volatile uint8_t *)(input+4u);
  *(volatile uint8_t *)(event+2u)=*(volatile uint8_t *)(input+6u);
  *(volatile uint8_t *)(event+3u)=*(volatile uint8_t *)(input+7u);
  *(volatile uint8_t *)(event+4u)=*(volatile uint8_t *)(input+8u);
  *(volatile uint8_t *)(event+5u)=*(volatile uint8_t *)(input+9u);
  (void)opencfw_em9305_radio_address_copy_304604(event+6u,input+10u);
  *(volatile uint8_t *)(event+12u)=*(volatile uint8_t *)(input+16u);
  *(volatile uint8_t *)(event+13u)=*(volatile uint8_t *)(input+18u);
  *(volatile uint8_t *)(event+14u)=*(volatile uint8_t *)(input+19u);
  *(volatile uint8_t *)(event+15u)=*(volatile uint8_t *)(input+20u);
  *(volatile uint8_t *)(event+16u)=*(volatile uint8_t *)(input+21u);
  *(volatile uint8_t *)(event+17u)=*(volatile uint8_t *)(input+22u);
  *(volatile uint8_t *)(event+18u)=*(volatile uint8_t *)(input+23u);
  *(volatile uint8_t *)(event+19u)=*(volatile uint8_t *)(input+24u);
 }
 if(type==38u){
  *(volatile uint8_t *)(event+1u)=*(volatile uint8_t *)(input+4u);
  *(volatile uint8_t *)(event+2u)=*(volatile uint8_t *)(input+6u);
  *(volatile uint8_t *)(event+3u)=*(volatile uint8_t *)(input+7u);
  *(volatile uint8_t *)(event+4u)=*(volatile uint8_t *)(input+8u);
  *(volatile uint8_t *)(event+5u)=*(volatile uint8_t *)(input+9u);
  *(volatile uint8_t *)(event+6u)=*(volatile uint8_t *)(input+10u);
  *(volatile uint8_t *)(event+7u)=*(volatile uint8_t *)(input+11u);
  *(volatile uint8_t *)(event+8u)=*(volatile uint8_t *)(input+12u);
  *(volatile uint8_t *)(event+9u)=*(volatile uint8_t *)(input+13u);
  (void)opencfw_em9305_radio_address_copy_304604(event+10u,input+14u);
  *(volatile uint8_t *)(event+16u)=*(volatile uint8_t *)(input+20u);
  *(volatile uint8_t *)(event+17u)=*(volatile uint8_t *)(input+22u);
  *(volatile uint8_t *)(event+18u)=*(volatile uint8_t *)(input+23u);
  *(volatile uint8_t *)(event+19u)=*(volatile uint8_t *)(input+24u);
  *(volatile uint8_t *)(event+20u)=*(volatile uint8_t *)(input+25u);
  *(volatile uint8_t *)(event+21u)=*(volatile uint8_t *)(input+26u);
  *(volatile uint8_t *)(event+22u)=*(volatile uint8_t *)(input+27u);
  *(volatile uint8_t *)(event+23u)=*(volatile uint8_t *)(input+28u);
 }
 (void)opencfw_em9305_ll_event_send(event-2u);
 return 1u;
}
