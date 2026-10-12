#define _GNU_SOURCE
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned allocations,sends,fail_at;static uintptr_t packets[300];static uint32_t lengths[300];
static uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t n){assert(n==246);unsigned i=allocations++;lengths[i]=n;if(i==fail_at)return 0;return 0x830000+i*512;}
static uintptr_t opencfw_em9305_ll_event_allocate(uint32_t code,uint32_t n){assert(code==62);unsigned i=allocations++;lengths[i]=n;if(i==fail_at)return 0;return 0x830002+i*512;}
static uint32_t opencfw_em9305_ll_event_send(uintptr_t p){packets[sends++]=p+2;return 99;}
static void *opencfw_em9305_memcpy(void *d,const void *s,uint32_t n){return memcpy(d,s,n);}
static uintptr_t opencfw_em9305_radio_address_copy_304604(uintptr_t d,uintptr_t s){memcpy((void *)d,(void *)s,6);return d;}
/* Authenticated fragmented-report helpers32e48c/32e4a8/330f48. Fixed246
 * allocator request, header old-address store then two-byte advance. */
uintptr_t opencfw_em9305_ll_fragment_allocate_32e48c(uint32_t code,uint32_t length)
{
 uintptr_t block=opencfw_em9305_wsf_event_allocate(246u);
 if(block==0u)return 0u;
 *(volatile uint8_t *)(block+1u)=(uint8_t)length;
 *(volatile uint8_t *)block=(uint8_t)code;
 return block+2u;
}
uintptr_t opencfw_em9305_ll_fragment_allocate_32e4a8(uint32_t code,uint32_t length)
{
 uintptr_t block=opencfw_em9305_wsf_event_allocate(246u);
 if(block==0u)return 0u;
 *(volatile uint8_t *)(block+1u)=(uint8_t)length;
 *(volatile uint8_t *)block=(uint8_t)code;
 return block+2u;
}
uintptr_t opencfw_em9305_ll_fragment_format_330f48(uintptr_t output,uintptr_t input,uintptr_t data,uint32_t bytes)
{
 uintptr_t original=*(volatile uint32_t *)(input+16u);
 uintptr_t end=data+bytes;
 uint32_t expected=*(volatile uint8_t *)(input+13u);
 uint32_t status=1u;
 if((uint16_t)(end-original)==expected){
  uint32_t mode=*(volatile uint8_t *)(input+12u);
  status=mode==255u?0xffffffffu:mode==2u?2u:0u;
 }
 *(volatile uint8_t *)output=40u;
 *(volatile uint8_t *)(output+1u)=*(volatile uint8_t *)(input+4u);
 *(volatile uint8_t *)(output+2u)=*(volatile uint8_t *)(input+5u);
 uint32_t captured=*(volatile uint8_t *)(input+6u);
 *(volatile uint8_t *)(output+4u)=1u;
 *(volatile uint8_t *)(output+3u)=(uint8_t)captured;
 *(volatile uint8_t *)(output+5u)=*(volatile uint8_t *)(input+8u);
 *(volatile uint8_t *)(output+6u)=*(volatile uint8_t *)(input+9u);
 *(volatile uint8_t *)(output+7u)=*(volatile uint8_t *)(input+10u);
 captured=*(volatile uint8_t *)(input+11u);
 *(volatile uint8_t *)(output+10u)=(uint8_t)bytes;
 *(volatile uint8_t *)(output+9u)=(uint8_t)status;
 *(volatile uint8_t *)(output+8u)=(uint8_t)captured;
 if(bytes==0u)return output;
 return (uintptr_t)opencfw_em9305_memcpy((void *)(output+11u),(const void *)data,bytes);
}

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
  uintptr_t config;
  uintptr_t cursor;
  if(type==32u){
   if(*(volatile uint8_t *)(input+18u)==255u)return 0u;
   remaining=*(volatile uint16_t *)(input+10u);
   config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
   uint32_t quotient,negative_product;
   quotient=remaining/247u;
   negative_product=0u-quotient*247u;
   needed=(uint8_t)(quotient+((uint16_t)negative_product!=(uint16_t)(0u-remaining)));
  }else{
   remaining=*(volatile uint8_t *)(input+13u);
   needed=(remaining>243u)+((uint8_t)(remaining+(remaining>=244u?12u:0u))!=0u);
   config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
  }
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

static void setup(unsigned type,unsigned limit){memset((void *)0x800000,0,0x100000);for(unsigned n=0;n<40;n++)*(uint8_t *)(uintptr_t)(0x810000+n)=n;*(uint8_t *)0x810002=type;*(uint8_t *)0x8056fc=255;*(uint8_t *)0x8056fd=1;*(uint8_t *)0x8056ef=32;*(uint32_t *)0x805cac=0x820000;*(uint8_t *)0x82000e=limit;*(uint8_t *)0x820004=13;allocations=sends=0;fail_at=999;}
int main(void){assert(mmap((void *)0x800000,0x100000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==(void *)0x800000);unsigned cases=0;
for(unsigned type=0;type<256;type++){if(type==5||type==30||type==32||type==38||type==52||type==53)continue;setup(type,10);assert(opencfw_em9305_dispatch_331334(0x810000)==0&&allocations==0);cases++;}
unsigned types[]={5,30,38,53},lens[]={34,20,24,4},ops[]={41,36,38,39};for(unsigned t=0;t<4;t++)for(unsigned alloc=0;alloc<2;alloc++){setup(types[t],10);if(!alloc)fail_at=0;assert(opencfw_em9305_dispatch_331334(0x810000)==alloc&&allocations==1&&sends==alloc&&lengths[0]==lens[t]);if(alloc){uint8_t *e=(uint8_t *)packets[0];assert(e[0]==ops[t]&&e[1]==4);if(types[t]==53)assert(e[2]==5&&e[3]==6);else assert(e[2]==6&&e[3]==7&&e[4]==8&&e[5]==9);if(types[t]==5)assert(!memcmp(e+6,(void *)0x81000a,6)&&!memcmp(e+12,(void *)0x810017,6)&&!memcmp(e+18,(void *)0x81001d,6)&&e[33]==37);if(types[t]==30)assert(!memcmp(e+6,(void *)0x81000a,6)&&e[12]==16&&e[13]==18&&e[19]==24);if(types[t]==38)assert(e[9]==13&&!memcmp(e+10,(void *)0x81000e,6)&&e[16]==20&&e[17]==22&&e[23]==28);}cases++;}
for(unsigned variant=0;variant<2;variant++)for(unsigned length=0;length<(variant?256:1000);length++)for(unsigned limit=0;limit<7;limit++)for(unsigned fail=0;fail<3;fail++){setup(variant?52:32,limit);if(variant){*(uint8_t *)0x81000d=length;*(uint32_t *)0x810010=0x850000;}else{*(uint16_t *)0x81000a=length;*(uint32_t *)0x81000c=0x850000;}for(unsigned n=0;n<1000;n++)*(uint8_t *)(uintptr_t)(0x850000+n)=n;fail_at=fail==2?999:fail;unsigned needed=variant?(unsigned)((length>243)+((uint8_t)(length+(length>=244?12:0))!=0)):(length+246)/247;unsigned actual=(length+243)/244;if(actual==0)actual=1;unsigned possible=needed<=limit;unsigned n=possible?(actual<limit?actual:limit):0;unsigned expected=possible&&actual<=limit&&fail_at>=actual;assert(opencfw_em9305_dispatch_331334(0x810000)==expected);unsigned sent=fail_at<n?fail_at:n;assert(sends==sent&&*(uint8_t *)0x805718==sent);unsigned offset=0;for(unsigned i=0;i<sends;i++){uint8_t *e=(uint8_t *)packets[i];unsigned chunk=length-offset<244?length-offset:244;assert(e[0]==(variant?40:37)&&e[10]==chunk&&!memcmp(e+11,(void *)(uintptr_t)(0x850000+offset),chunk));offset+=chunk;}cases++;}
printf("PASS %u\n",cases);}
