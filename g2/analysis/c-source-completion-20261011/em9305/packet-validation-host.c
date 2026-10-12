#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned classification,match,mode,peer_kind,associate,projects,associations;
uint32_t opencfw_em9305_radio_classify_314470(uint32_t a,uint32_t r,uintptr_t k,uintptr_t d){assert(a==0&&r<=1&&k==0x820013&&d==0x820008);return classification;}
uint32_t opencfw_em9305_radio_address_mode_303e5c(void){return mode;}
uint32_t opencfw_em9305_radio_address_match_303df8(uint32_t k,uint32_t l,uint32_t h){assert(k==0&&l==500&&h==600);return match;}
uint32_t opencfw_em9305_radio_peer_kind_3039f0(uint32_t k,uint32_t l,uint32_t h){assert(k==0&&l==500&&h==600);return peer_kind;}
uint32_t opencfw_em9305_radio_address_project_303b7c(uint32_t l,uint32_t h,uintptr_t k,uintptr_t p){assert(l==0x80&&h==0x4000);projects++;*(uint8_t *)k=9;*(uint32_t *)p=700;*(uint32_t *)(p+4)=800;return 0;}
uint32_t opencfw_em9305_radio_address_associate_303844(uint32_t l,uint32_t h,uint32_t k,uint32_t a,uint32_t b){assert(l==0x80&&h==0x4000&&k==9&&a==700&&b==800);associations++;return associate;}
uint64_t opencfw_em9305_controller_pack_address(uintptr_t address)
{
 volatile uint8_t *bytes=(volatile uint8_t *)address;
 uint32_t second=bytes[1],third=bytes[2],first=bytes[0];
 uint32_t sixth=bytes[5],fourth=bytes[3],fifth=bytes[4];
 uint32_t low=first|(second<<8)|(third<<16)|(fourth<<24);
 uint32_t high=fifth|(sixth<<8);
 return ((uint64_t)high<<32)|low;
}
/* Authenticated packet validation303404..303650. Descriptor cursor is
 * output+8 after native ST.AB; output kind/status bytes are consequently
 * output18/19 and output20/21. Address projection children remain genuine. */
extern uint32_t opencfw_em9305_radio_address_project_303b7c(uint32_t,uint32_t,uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_radio_address_associate_303844(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
uint32_t opencfw_em9305_radio_packet_check_303404(uint32_t packet,uintptr_t policy,uint32_t resolve,uintptr_t output)
{
 uintptr_t input=(uintptr_t)packet;
 uint32_t type=*(volatile uint8_t *)input&15u;
 uint32_t allowed=*(volatile uint16_t *)policy;
 if((allowed&(1u<<type))==0u){
  if(type==9u&&(*(volatile uint8_t *)(policy+4u)&128u)!=0u)return 1u;
  return 0u;
 }
 uint32_t mask=1u<<type;
 if((mask&896u)!=0u)return 1u;
 uint32_t length=*(volatile uint8_t *)(input+1u)&63u;
 *(volatile uint8_t *)(output+16u)=(uint8_t)type;
 *(volatile uint8_t *)(output+17u)=(uint8_t)length;
 uint32_t header=*(volatile uint8_t *)input;
 uint64_t address=opencfw_em9305_controller_pack_address(input+2u);
 uint32_t low=(uint32_t)address,high=(uint32_t)(address>>32u);
 uint32_t flags=*(volatile uint32_t *)(policy+4u);
 *(volatile uint32_t *)(output+12u)=high;
 *(volatile uint32_t *)(output+8u)=low;
 *(volatile uint32_t *)(output+4u)=high;
 *(volatile uint32_t *)output=low;
 uintptr_t descriptor=output+8u,kind_cell=output+19u;
 uint32_t kind=(header>>6u)&1u;
 *(volatile uint8_t *)(output+19u)=(uint8_t)kind;
 *(volatile uint8_t *)(output+18u)=(uint8_t)kind;
 uint32_t classification=opencfw_em9305_radio_classify_314470((flags>>6u)&1u,resolve,kind_cell,descriptor);
 if(classification==1u||classification==3u)return 0u;
 flags=*(volatile uint32_t *)(policy+4u);
 high=*(volatile uint32_t *)(descriptor+4u);
 low=*(volatile uint32_t *)descriptor;
 kind=*(volatile uint8_t *)kind_cell;
 uint32_t secondary=0u;
 if((flags&4u)!=0u&&((kind!=0u)^((flags>>3u)&1u))==0u){
  uint32_t wanted_low=*(volatile uint32_t *)(policy+16u);
  uint32_t wanted_high=*(volatile uint32_t *)(policy+20u);
  secondary=3u;
  if(((wanted_low^low)|(wanted_high^high))==0u)secondary=2u;
 }
 uint32_t filter=*(volatile uint16_t *)(policy+2u);
 uint32_t decision=0u;
 if((filter&mask)!=0u){
  if((low|high)==0u&&opencfw_em9305_radio_address_mode_303e5c()!=0u)decision=2u;
  else decision=(opencfw_em9305_radio_address_match_303df8(kind!=0u,low,high)==0u)+2u;
 }
 uint32_t ordinary=(classification!=2u);
 uint32_t selected=(classification==2u)*2u,accepted=2u;
 if(decision<secondary){
  flags=*(volatile uint32_t *)(policy+4u);
  if((flags&4u)!=0u){
   uint32_t wanted_high=*(volatile uint32_t *)(policy+20u);
   uint32_t actual_high=*(volatile uint32_t *)(descriptor+4u);
   uint32_t wanted_low=*(volatile uint32_t *)(policy+16u);
   uint32_t actual_low=*(volatile uint32_t *)descriptor;
   uint32_t actual_kind=*(volatile uint8_t *)kind_cell;
   uint32_t mismatch=(actual_kind!=0u)^((flags>>3u)&1u);
   if(((wanted_high^actual_high)|(wanted_low^actual_low))!=0u)mismatch|=1u;
   if(mismatch==0u)selected=2u;
   accepted=selected;
   if(((~mismatch|ordinary)&1u)==0u)return 0u;
  }
 }else{
  filter=*(volatile uint16_t *)(policy+2u);
  if((filter&mask)!=0u){
   high=*(volatile uint32_t *)(descriptor+4u);
   low=*(volatile uint32_t *)descriptor;
   kind=*(volatile uint8_t *)kind_cell;
   if((low|high)!=0u||opencfw_em9305_radio_address_mode_303e5c()==0u){
    uint32_t matched=opencfw_em9305_radio_address_match_303df8(kind!=0u,low,high);
    if(matched!=0u)selected=2u;
    accepted=selected;
    if((matched|ordinary)!=1u)return 0u;
   }
  }
 }
 *(volatile uint8_t *)(descriptor+13u)=1u;
 *(volatile uint8_t *)(descriptor+12u)=(uint8_t)(accepted==2u);
 if(type>=6u||(42u&(1u<<type))==0u)return 1u;
 int32_t second_header=(int8_t)*(volatile uint8_t *)input; /* LDB.AB accesses old input, then advances by8. */
 address=opencfw_em9305_controller_pack_address(input+8u);
 uint32_t peer_low=(uint32_t)address,peer_high=(uint32_t)(address>>32u);
 flags=*(volatile uint32_t *)(policy+4u);
 high=*(volatile uint32_t *)(descriptor+4u);
 kind=*(volatile uint8_t *)kind_cell;
 low=*(volatile uint32_t *)descriptor;
 uint32_t pair[2]={low,high};
 uint8_t projected_kind=(uint8_t)kind;
 if((flags&16u)!=0u){
  if(second_header<0&&(peer_high&0xc000u)==0x4000u){
   if(resolve!=0u){
    (void)opencfw_em9305_radio_address_project_303b7c(peer_low,peer_high,(uintptr_t)&projected_kind,(uintptr_t)pair);
    low=pair[0];high=pair[1];kind=projected_kind;
   }
   if(opencfw_em9305_radio_address_associate_303844(peer_low,peer_high,kind,low,high)!=0u)return 1u;
  }else{
   if((opencfw_em9305_radio_peer_kind_3039f0(kind!=0u,low,high)&254u)==2u)return 0u;
  }
 }
 flags=*(volatile uint32_t *)(policy+4u);
 if((flags&1u)==0u)return 1u;
 if((((second_header<0)^((flags>>1u)&1u))&1u)==0u){
  uint32_t wanted_low=*(volatile uint32_t *)(policy+8u);
  uint32_t wanted_high=*(volatile uint32_t *)(policy+12u);
  if(((peer_low^wanted_low)|(peer_high^wanted_high))==0u)return 1u;
 }
 if(second_header>=0||(peer_high&0xc000u)!=0x4000u||(flags&32u)==0u)return 0u;
 *(volatile uint8_t *)(descriptor+13u)=0u;
 return 1u;
}


static void reset(unsigned type,unsigned allowed,unsigned flags){memset((void *)0x800000,0,0x100000);classification=2;match=1;mode=peer_kind=associate=projects=associations=0;*(uint8_t *)0x810000=type;*(uint8_t *)0x810001=63;*(uint32_t *)0x810002=500;*(uint16_t *)0x810006=600;*(uint16_t *)0x811000=allowed?1u<<type:0;*(uint32_t *)0x811004=flags;}
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;for(unsigned type=0;type<16;type++)for(unsigned allowed=0;allowed<2;allowed++)for(classification=0;classification<5;classification++)for(unsigned filter=0;filter<2;filter++)for(match=0;match<2;match++){unsigned c=classification,m=match;reset(type,allowed,0);classification=c;match=m;*(uint16_t *)0x811002=filter?1u<<type:0;unsigned r=opencfw_em9305_radio_packet_check_303404(0x810000,0x811000,0,0x820000);unsigned expected=!allowed?0:(type>=7&&type<=9)?1:(c==1||c==3)?0:filter&&!m&&c==2?0:1;assert(r==expected);if(allowed&&!(type>=7&&type<=9)&&c!=1&&c!=3&&expected){assert(*(uint8_t *)0x820010==type&&*(uint8_t *)0x820011==63&&*(uint32_t *)0x820000==500&&*(uint32_t *)0x820004==600&&*(uint8_t *)0x820015==1);}cases++;}
reset(9,0,128);assert(opencfw_em9305_radio_packet_check_303404(0x810000,0x811000,0,0x820000)==1);cases++;
for(unsigned c=0;c<3;c+=2)for(unsigned same=0;same<2;same++){reset(0,1,4);classification=c;*(uint32_t *)0x811010=same?500:501;*(uint32_t *)0x811014=600;unsigned r=opencfw_em9305_radio_packet_check_303404(0x810000,0x811000,0,0x820000);assert(r==(same||c==0));if(r)assert(*(uint8_t *)0x820014==(same?1:0));cases++;}
for(unsigned type=1;type<6;type+=2)for(unsigned random=0;random<2;random++)for(unsigned permit=0;permit<2;permit++){reset(type,1,1|(permit?32:0));*(uint8_t *)0x810000=type|(random?128:0);*(uint8_t *)0x810008=0x80;*(uint16_t *)0x81000c=0x4000;assert(opencfw_em9305_radio_packet_check_303404(0x810000,0x811000,0,0x820000)==(random&&permit));if(random&&permit)assert(*(uint8_t *)0x820015==0);cases++;}
reset(1,1,1);*(uint32_t *)0x811008=0;*(uint32_t *)0x81100c=0;assert(opencfw_em9305_radio_packet_check_303404(0x810000,0x811000,0,0x820000)==1);cases++;
for(unsigned a=0;a<2;a++){reset(1,1,16);*(uint8_t *)0x810000=129;*(uint8_t *)0x810008=0x80;*(uint16_t *)0x81000c=0x4000;associate=a;assert(opencfw_em9305_radio_packet_check_303404(0x810000,0x811000,1,0x820000)==1&&projects==1&&associations==1);cases++;}
reset(1,1,16);peer_kind=2;assert(opencfw_em9305_radio_packet_check_303404(0x810000,0x811000,0,0x820000)==0);cases++;printf("PASS %u\n",cases);}
