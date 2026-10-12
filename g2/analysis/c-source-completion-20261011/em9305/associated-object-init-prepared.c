/* Native312918..312b84 full eight-way packet duration initialization.
 * All children are already selected authenticated native source providers. */
uint32_t opencfw_em9305_associated_object_init_312918(uintptr_t object,uint32_t requested)
{
 uintptr_t packet=*(volatile uint32_t *)(object+44u);
 uint32_t type=*(volatile uint8_t *)packet,index=type-2u,duration=0u,result=index;
 uint32_t kind,phy,mode,size;
 switch(index){
 case 0u:
  kind=*(volatile uint8_t *)(packet+13u);
  result=*(volatile uint32_t *)(packet+104u);duration=kind==3u?3088u:376u;
  if(result!=0u){
   size=*(volatile uint8_t *)(packet+149u);phy=*(volatile uint8_t *)(packet+12u);
   result=opencfw_em9305_radio_duration_piece_312b88(phy,0u,size);duration+=result+150u;
   uint32_t extra=*(volatile uint32_t *)(packet+108u);
   if(extra!=0u)duration+=kind==3u?3238u:526u;
  }
  break;
 case 1u:{
  size=*(volatile uint8_t *)(packet+124u);mode=*(volatile uint8_t *)(packet+14u);phy=*(volatile uint8_t *)(packet+12u);
  uint32_t initial=opencfw_em9305_radio_duration_piece_312b88(phy,mode,size);
  uint32_t flags=*(volatile uint8_t *)(packet+127u);
  uint32_t guard=opencfw_em9305_auxiliary_guard_interval();
  uint32_t adjusted=opencfw_em9305_channel_timing_adjust_312c5c(guard+initial);
  uint32_t count=(flags&1u)+((flags>>1u)&1u)+((flags>>2u)&1u);
  duration=(count-1u)*adjusted+initial;
  result=adjusted;
  uint32_t enabled=*(volatile uint32_t *)(packet+104u);
  if(enabled!=0u){
   kind=*(volatile uint8_t *)(packet+13u);
   uint32_t gap=count*150u,base=kind==3u?3088u:376u;
   result=(base&65535u)*(count&65535u);duration+=gap+result;
   uint32_t extra=*(volatile uint32_t *)(packet+108u);
   if(extra!=0u){
    size=*(volatile uint8_t *)(packet+149u);phy=*(volatile uint8_t *)(packet+12u);
    result=opencfw_em9305_radio_duration_piece_312b88(phy,0u,size);
    result=opencfw_em9305_native_mpywhl(result,count);
    duration+=gap+result;
   }
  }
  break;
 }
 case 4u:{
  uint32_t extended=*(volatile uint8_t *)(packet+132u);kind=*(volatile uint8_t *)(packet+13u);
  if(extended!=0u){
   duration=kind==3u?720u:(kind==2u?44u:80u);
   if(kind==3u)*(volatile uint32_t *)(object+16u)=17040u;
   result=*(volatile uint32_t *)(packet+100u);
   if(result!=0u){
    mode=*(volatile uint8_t *)(packet+15u);phy=*(volatile uint8_t *)(packet+12u);
    result=opencfw_em9305_radio_duration_piece_312b88(phy,mode==0u?2u:mode,36u);
    duration+=kind==3u?1916u:(kind==2u?400u:492u);
    duration+=result;
   }
  }else{
   duration=kind==3u?3792u:(kind==2u?236u:464u);
   if(kind==3u)*(volatile uint32_t *)(object+16u)=17040u;
   result=*(volatile uint32_t *)(packet+100u);
   if(result!=0u){
    mode=*(volatile uint8_t *)(packet+15u);size=*(volatile uint8_t *)(packet+124u);phy=*(volatile uint8_t *)(packet+12u);
    result=opencfw_em9305_radio_duration_piece_312b88(phy,mode==0u?2u:mode,size);
    duration+=result+150u+(kind==3u?17190u:(kind==2u?1214u:2270u));
   }
  }
  break;
 }
 case 5u:{
  uint32_t step=requested!=0u?requested:241u,limit=requested!=0u?requested:244u;
  result=*(volatile uint32_t *)(packet+116u);
  if(result!=0u){
   mode=*(volatile uint8_t *)(packet+14u);phy=*(volatile uint8_t *)(packet+12u);
   result=opencfw_em9305_radio_duration_piece_312b88(phy,mode,13u);duration=result;
   kind=*(volatile uint8_t *)(packet+13u);
   duration+=150u+(kind==3u?17190u:(kind==2u?1214u:2270u));
  }
  uintptr_t source=*(volatile uint32_t *)(object+40u);
  uint32_t amount=source!=0u?*(volatile uint16_t *)source:0u;
  mode=*(volatile uint8_t *)(packet+14u);phy=*(volatile uint8_t *)(packet+12u);
  if(limit<amount){
   result=opencfw_em9305_radio_duration_piece_312b88(phy,mode,step+16u);
   uint32_t quotient=opencfw_em9305_config_link_divu_prior(amount,step,step);
   result+=300u;
   uint32_t product=(uint32_t)((int32_t)(int16_t)step*(int32_t)(int16_t)quotient);
   result*=quotient;duration+=result;
   uint32_t remainder=amount-product;
   if((uint16_t)remainder!=0u){result=opencfw_em9305_radio_duration_piece_312b88(phy,mode,(uint16_t)(remainder+13u));duration+=result;}
  }else{
   uint32_t addition=*(volatile uint16_t *)(packet+100u);if(addition<13u)addition=13u;
   result=opencfw_em9305_radio_duration_piece_312b88(phy,mode,(uint16_t)(amount+addition));duration+=result;
  }
  break;
 }
 case 6u:
  {uintptr_t source=*(volatile uint32_t *)(object+40u);size=source!=0u?*(volatile uint16_t *)source:64u;if(size<64u)size=64u;}
  phy=*(volatile uint8_t *)(packet+12u);mode=*(volatile uint8_t *)(packet+14u);
  result=opencfw_em9305_radio_duration_312be4(phy,0u,0u,0u,size,0u,mode,0u);duration=result;break;
 case 7u:
  phy=*(volatile uint8_t *)(packet+12u);mode=*(volatile uint8_t *)(packet+14u);
  result=opencfw_em9305_radio_duration_312be4(phy,0u,0u,0u,0u,0u,mode,0u);duration=result;break;
 default:break;
 }
 *(volatile uint32_t *)(object+12u)=duration;
 return result;
}
