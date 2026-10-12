#include <stdint.h>
#include <assert.h>
#include <stdio.h>
uint32_t old_opencfw_em9305_radio_duration_piece_312b88(uint32_t phy,uint32_t mode,uint32_t size)
{
 if(phy==2u) return 36u+(size<<2);
 if(phy!=3u) return (size<<3)+64u;
 uint32_t product;
 uint32_t factor=mode==1u?2u:8u,base=27u+(size<<3);
 product=(uint32_t)((int64_t)(int32_t)base*(int16_t)factor);
 return product+376u;
}
/* Native312be4..312c5c: fullword thresholds, DIVU and native word/DSP
 * multiplication retained. Only remainder/piece calls explicitly truncate. */
uint32_t old_opencfw_em9305_radio_duration_312be4(uint32_t phy,uint32_t requested,uint32_t timing,uint32_t spacing,uint32_t size,uint32_t extended,uint32_t mode,uint32_t overhead)
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
  result=old_opencfw_em9305_radio_duration_piece_312b88(phy,mode,(uint16_t)(last+size));
 }else{
  uint32_t quotient,product;
  assert(divisor!=0u);quotient=size/divisor;
  product=(uint32_t)((int32_t)(int16_t)quotient*(int16_t)divisor);
  uint32_t remainder=size-product;
  uint32_t has_remainder=(uint16_t)remainder;
  if(has_remainder==0u) quotient-=1u;
  uint32_t piece=old_opencfw_em9305_radio_duration_piece_312b88(phy,mode,full_size);
  piece+=spacing+300u;
  result=piece*(uint16_t)quotient;
  if(has_remainder!=0u)
   result+=old_opencfw_em9305_radio_duration_piece_312b88(phy,mode,(uint16_t)(remainder+last));
 }
 return result+timing;
}
uint32_t opencfw_em9305_radio_duration_piece_312b88(uint32_t phy,uint32_t mode,uint32_t size)
{
 if(phy==2u) return 36u+(size<<2);
 if(phy!=3u) return (size<<3)+64u;
 uint32_t product;
 uint32_t factor=mode==1u?2u:8u,base=27u+(size<<3);
 product=(uint32_t)((int64_t)(int32_t)base*(int16_t)factor);
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
  result=opencfw_em9305_radio_duration_piece_312b88(phy,mode,(uint32_t)(int32_t)(int16_t)(last+size));
 }else{
  uint32_t quotient,product;
  assert(divisor!=0u);quotient=size/divisor;
  product=(uint32_t)((int32_t)(int16_t)quotient*(int16_t)divisor);
  uint32_t remainder=size-product;
  uint32_t has_remainder=(uint16_t)remainder;
  if(has_remainder==0u) quotient-=1u;
  uint32_t piece=opencfw_em9305_radio_duration_piece_312b88(phy,mode,full_size);
  piece+=spacing+300u;
  result=piece*(uint16_t)quotient;
  if(has_remainder!=0u)
   result+=opencfw_em9305_radio_duration_piece_312b88(phy,mode,(uint32_t)(int32_t)(int16_t)(remainder+last));
 }
 return result+timing;
}

/* Independent word-level model of native312be4/312b88; nonzero divider
 * routes only. Host DSP models do not establish ARC runtime equivalence. */
static uint32_t piece(uint32_t p,uint32_t m,uint32_t n){
 if(p==2u)return 36u+(n<<2);
 if(p!=3u)return (n<<3)+64u;
 return (uint32_t)((int64_t)(int32_t)(27u+(n<<3))*(m==1u?2:8))+376u;
}
static uint32_t native(uint32_t p,uint32_t request,uint32_t spacing,uint32_t n,uint32_t overhead){
 uint32_t r13=overhead?overhead:5u,r2=overhead?overhead:10u;
 uint32_t r14=request?request:257u-r2,limit=request?request:257u-r13;
 if(limit>=n)return piece(p,0u,(uint32_t)(int32_t)(int16_t)(r13+n));
 assert(r14!=0u);uint32_t q=n/r14;
 uint32_t prod=(uint32_t)((int32_t)(int16_t)q*(int16_t)r14),rem=n-prod;
 if((uint16_t)rem==0u)--q;
 uint32_t total=(piece(p,0u,r2+r14)+spacing+300u)*(uint16_t)q;
 if((uint16_t)rem!=0u)total+=piece(p,0u,(uint32_t)(int32_t)(int16_t)(rem+r13));
 return total;
}
int main(void){unsigned changes=0,cases=0;
 const uint32_t routes[][4]={{0,64,0,0},{0,500,0,0},{50000,40000,0,0},{20000,55000,40000,5}};
 for(uint32_t phy=1;phy<=3;++phy)for(unsigned i=0;i<4;++i){
  uint32_t r=routes[i][0],n=routes[i][1],o=routes[i][2],sp=routes[i][3];
  uint32_t wanted=native(phy,r,sp,n,o);
  uint32_t got=opencfw_em9305_radio_duration_312be4(phy,r,0,sp,n,0,0,o);
  uint32_t prior=old_opencfw_em9305_radio_duration_312be4(phy,r,0,sp,n,0,0,o);
  assert(got==wanted);if(prior!=wanted)++changes;++cases;
 }
 assert(changes==6);printf("EXTH regression: %u cases PASS; %u prior mismatches\n",cases,changes);return 0;
}
