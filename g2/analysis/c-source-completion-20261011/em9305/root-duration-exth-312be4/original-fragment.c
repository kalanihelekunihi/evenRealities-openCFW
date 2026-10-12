uint32_t opencfw_em9305_radio_duration_piece_312b88(uint32_t phy,uint32_t mode,uint32_t size)
{
 if(phy==2u) return 36u+(size<<2);
 if(phy!=3u) return (size<<3)+64u;
 uint32_t product;
 uint32_t factor=mode==1u?2u:8u,base=27u+(size<<3);
 __asm__ volatile("mpywhl %0,%1,%2":"=r"(product):"r"(base),"r"(factor));
 return product+376u;
}
/* Native312be4..312c5c: fullword thresholds, DIVU and native word/DSP
 * multiplication retained. Only remainder/piece calls explicitly truncate. */
uint32_t opencfw_em9305_radio_duration_312be4(uint32_t phy,uint32_t requested,uint32_t timing,uint32_t spacing,uint32_t size,uint32_t extended,uint32_t mode,uint32_t overhead)
{
 uint32_t first=66u,last=66u;
 if(extended==0u){
  first=overhead;last=overhead;
  if(overhead==0u){first=10u;last=5u;}
 }
 uint32_t divisor=requested,threshold=requested;
 if(requested==0u){divisor=257u-first;threshold=257u-last;}
 uint32_t full_size=first+divisor,result;
 if(threshold>=size){
  result=opencfw_em9305_radio_duration_piece_312b88(phy,mode,(uint16_t)(last+size));
 }else{
  uint32_t quotient,product;
  __asm__ volatile("divu %0,%1,%2":"=r"(quotient):"r"(size),"r"(divisor));
  __asm__ volatile("mpyw %0,%1,%2":"=r"(product):"r"(quotient),"r"(divisor));
  uint32_t remainder=size-product;
  uint32_t has_remainder=(uint16_t)remainder;
  if(has_remainder==0u) quotient-=1u;
  uint32_t piece=opencfw_em9305_radio_duration_piece_312b88(phy,mode,full_size);
  piece+=spacing+300u;
  __asm__ volatile("mpywhul %0,%1,%2":"=r"(result):"r"(piece),"r"(quotient));
  if(has_remainder!=0u)
   result+=opencfw_em9305_radio_duration_piece_312b88(phy,mode,(uint16_t)(remainder+last));
 }
 return result+timing;
}
