#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
static unsigned allocated,sent,fail,shrink;
static uint8_t copies[300][300];static unsigned offsets[300],sizes[300];
uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t bytes){
 if(fail)return 0;
 uintptr_t p=0x840000u+allocated*512u;++allocated;sizes[allocated-1]=bytes;memset((void*)p,0xa5,300);
 if(shrink)*(uint8_t*)0x80700e=1;
 return p;
}
uintptr_t opencfw_em9305_ll_event_allocate(uint32_t type,uint32_t bytes){uintptr_t p=opencfw_em9305_wsf_event_allocate(bytes+2);if(!p)return 0;*(uint8_t*)p=type;*(uint8_t*)(p+1)=bytes;return p+2;}
uint32_t opencfw_em9305_ll_event_send(uintptr_t p){unsigned i=sent++;uintptr_t base=0x840000u+i*512u;offsets[i]=p-base;memcpy(copies[i],(void*)base,300);return 0xfeed;}
uintptr_t opencfw_em9305_radio_address_copy_304604(uintptr_t o,uintptr_t i){for(unsigned n=0;n<6;++n)*(uint8_t*)(o+n)=*(uint8_t*)(i+n);return o;}
void *opencfw_em9305_memcpy(void*o,const void*i,uint32_t n){for(unsigned x=0;x<n;++x)((uint8_t*)o)[x]=((const uint8_t*)i)[x];return o;}
/* Native32e470..32e48c: fixed249-byte allocation with variable payload header. */
uintptr_t opencfw_em9305_event_allocate_large_32e470(uint32_t type,uint32_t bytes)
{
 uintptr_t event=opencfw_em9305_wsf_event_allocate(249u);
 if(!event)return 0u;
 *(volatile uint8_t *)(event+1u)=(uint8_t)bytes;
 *(volatile uint8_t *)event=(uint8_t)type;
 return event+2u;
}
static inline uint32_t opencfw_em9305_event_mpyw_negative(uint32_t q,uint32_t d){return (uint32_t)((int32_t)(int16_t)q*-(int32_t)d);}
/* Native330848..330bdc: full event switch, live capacity and fragmented payloads. */
uint32_t opencfw_em9305_dispatch_330848(uintptr_t packet)
{
 uint32_t type=*(volatile uint8_t *)(packet+2u);
 uintptr_t event;
 if(type==23u||type==32u){
  uint32_t bit=type==23u?4u:6u;
  if((*(volatile uint8_t *)(uintptr_t)0x8056f9u&(1u<<bit))==0u)return 0u;
  if((*(volatile uint8_t *)(uintptr_t)0x8056efu&32u)==0u)return 0u;
  uint32_t divisor=type==23u?229u:247u;
  uint32_t length=*(volatile uint16_t *)(packet+(type==23u?28u:10u));
  uintptr_t product=*(volatile uint32_t *)(uintptr_t)0x805cacu;
  uint32_t quotient=length/divisor;
  uint32_t negative=opencfw_em9305_event_mpyw_negative(quotient,divisor);
  uint32_t needed=(uint8_t)(quotient+((uint16_t)negative!=(uint16_t)(0u-length)));
  uint32_t count=*(volatile uint8_t *)(uintptr_t)0x805718u;
  uint32_t capacity=*(volatile uint8_t *)(product+14u);
  if(needed+count>capacity)return 0u;
  uintptr_t data=*(volatile uint32_t *)(packet+(type==23u?32u:12u));
  uint32_t remaining=length,stopped;
  do{
   product=*(volatile uint32_t *)(uintptr_t)0x805cacu;
   count=*(volatile uint8_t *)(uintptr_t)0x805718u;
   uint32_t chunk=remaining<divisor?remaining:divisor;
   capacity=*(volatile uint8_t *)(product+14u);
   if(count>=capacity)return 0u;
   event=type==23u?opencfw_em9305_wsf_event_allocate(231u):opencfw_em9305_event_allocate_large_32e470(62u,(uint8_t)(chunk+8u));
   if(!event)return 0u;
   if(type==23u){*(volatile uint8_t *)event=62u;*(volatile uint8_t *)(event+1u)=(uint8_t)(chunk+26u);}
   product=*(volatile uint32_t *)(uintptr_t)0x805cacu;
   count=*(volatile uint8_t *)(uintptr_t)0x805718u;
   remaining-=chunk;
   capacity=*(volatile uint8_t *)(product+14u);
   uint32_t next=count+1u;
   if(type==23u){
    *(volatile uint8_t *)(uintptr_t)0x805718u=(uint8_t)next;
    stopped=(remaining!=0u)&&((uint8_t)next==capacity);
    uint32_t flags=*(volatile uint16_t *)(packet+4u);
    if(stopped){flags|=64u;remaining=0u;*(volatile uint16_t *)(packet+4u)=(uint16_t)flags;}
    uintptr_t initial=*(volatile uint32_t *)(packet+32u);
    uint32_t total=*(volatile uint16_t *)(packet+28u);
    uintptr_t end=data+chunk;
    uint32_t projected=(flags&31u)|32u;
    if(total==(uint16_t)(end-initial))projected=flags;
    *(volatile uint8_t *)(event+4u)=(uint8_t)projected;
    *(volatile uint8_t *)(event+3u)=1u;*(volatile uint8_t *)(event+2u)=13u;
    *(volatile uint8_t *)(event+5u)=(uint8_t)(projected>>8u);
    *(volatile uint8_t *)(event+6u)=*(volatile uint8_t *)(packet+6u);
    (void)opencfw_em9305_radio_address_copy_304604(event+7u,packet+7u);
    for(uint32_t i=13u;i<=20u;++i)*(volatile uint8_t *)(event+i)=*(volatile uint8_t *)(packet+i);
    (void)opencfw_em9305_radio_address_copy_304604(event+21u,packet+21u);
    *(volatile uint8_t *)(event+27u)=(uint8_t)chunk;
    (void)opencfw_em9305_memcpy((void *)(event+28u),(const void *)data,chunk);
    (void)opencfw_em9305_ll_event_send(event);data=end;
   }else{
    stopped=(remaining!=0u)&&((uint8_t)next==capacity);
    *(volatile uint8_t *)(uintptr_t)0x805718u=(uint8_t)next;
    if(stopped){remaining=0u;*(volatile uint8_t *)(packet+9u)=2u;}
    uintptr_t initial=*(volatile uint32_t *)(packet+12u);
    uint32_t total=*(volatile uint16_t *)(packet+10u);
    uintptr_t end=data+chunk;uint32_t projected=1u;
    if(total==(uint16_t)(end-initial))projected=(*(volatile uint8_t *)(packet+9u)==2u)?2u:0u;
    *(volatile uint8_t *)event=15u;
    for(uint32_t i=1u;i<=4u;++i)*(volatile uint8_t *)(event+i)=*(volatile uint8_t *)(packet+i+3u);
    uint32_t last=*(volatile uint8_t *)(packet+8u);
    *(volatile uint8_t *)(event+7u)=(uint8_t)chunk;
    *(volatile uint8_t *)(event+6u)=(uint8_t)projected;
    *(volatile uint8_t *)(event+5u)=(uint8_t)last;
    if((uint8_t)chunk)(void)opencfw_em9305_memcpy((void *)(event+8u),(const void *)data,chunk);
    (void)opencfw_em9305_ll_event_send(event-2u);data=end;
   }
  }while(remaining!=0u);
  return stopped^1u;
 }
 if(type==24u){
  event=opencfw_em9305_ll_event_allocate(14u,4u);if(!event)return 0u;
  *(volatile uint8_t *)(event+2u)=32u;*(volatile uint8_t *)(event+1u)=66u;
  *(volatile uint8_t *)event=1u;
  *(volatile uint8_t *)(event+3u)=*(volatile uint8_t *)(packet+3u);
  (void)opencfw_em9305_ll_event_send(event-2u);return 1u;
 }
 if(type==25u){
  if((*(volatile uint8_t *)(uintptr_t)0x8056fau&1u)==0u)return 0u;
  if((*(volatile uint8_t *)(uintptr_t)0x8056efu&32u)==0u)return 0u;
  event=opencfw_em9305_ll_event_allocate(62u,1u);if(!event)return 0u;
  *(volatile uint8_t *)event=17u;(void)opencfw_em9305_ll_event_send(event-2u);return 1u;
 }
 if(type==30u||type==31u||type==38u){
  uintptr_t feature=type==38u?0x8056fau:0x8056f9u;
  uint32_t bit=type==30u?5u:7u;
  if((*(volatile uint8_t *)feature&(1u<<bit))==0u)return 0u;
  if((*(volatile uint8_t *)(uintptr_t)0x8056efu&32u)==0u)return 0u;
  uint32_t bytes=type==30u?16u:(type==31u?3u:20u);
  event=opencfw_em9305_ll_event_allocate(62u,bytes);if(!event)return 0u;
  if(type==31u){
   *(volatile uint8_t *)event=16u;
   *(volatile uint8_t *)(event+1u)=*(volatile uint8_t *)(packet+4u);
   *(volatile uint8_t *)(event+2u)=*(volatile uint8_t *)(packet+5u);
  }else{
   *(volatile uint8_t *)event=type==30u?14u:24u;
   *(volatile uint8_t *)(event+1u)=*(volatile uint8_t *)(packet+4u);
   uint32_t last=type==30u?5u:9u;
   for(uint32_t i=2u;i<=last;++i)*(volatile uint8_t *)(event+i)=*(volatile uint8_t *)(packet+i+4u);
   uint32_t dest=type==30u?6u:10u,src=type==30u?10u:14u;
   (void)opencfw_em9305_radio_address_copy_304604(event+dest,packet+src);
   *(volatile uint8_t *)(event+dest+6u)=*(volatile uint8_t *)(packet+src+6u);
   for(uint32_t i=7u;i<=9u;++i)*(volatile uint8_t *)(event+dest+i)=*(volatile uint8_t *)(packet+src+i+1u);
  }
  (void)opencfw_em9305_ll_event_send(event-2u);return 1u;
 }
 return 0u;
}

int main(void){
 if(mmap((void*)0x800000,0x90000,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;
 uintptr_t p=0x810000;unsigned cases=0;
 for(unsigned type=0;type<256;++type)for(unsigned gates=0;gates<16;++gates)for(fail=0;fail<2;++fail){
  allocated=sent=shrink=0;for(unsigned i=0;i<64;++i)*(uint8_t*)(p+i)=i*7+1;*(uint8_t*)(p+2)=type;
  *(uint8_t*)0x8056f9=(gates&1)?255:0;*(uint8_t*)0x8056fa=(gates&2)?255:0;*(uint8_t*)0x8056ef=(gates&4)?32:0;
  *(uint32_t*)0x805cac=0x807000;*(uint8_t*)0x80700e=0;*(uint8_t*)0x805718=0;
  unsigned active=type==24||((type==25||type==38)?((gates&2)&&(gates&4)):((type==30||type==31)?((gates&1)&&(gates&4)):0));
  unsigned got=opencfw_em9305_dispatch_330848(p);if(got!=(active&&!fail)||sent!=(active&&!fail))return 3;
  if(sent){uint8_t expected[300];memset(expected,0xa5,300);unsigned len=type==24?4:type==25?1:type==30?16:type==31?3:20;expected[0]=type==24?14:62;expected[1]=len;
   if(type==24){expected[2]=1;expected[3]=66;expected[4]=32;expected[5]=*(uint8_t*)(p+3);}
   if(type==25)expected[2]=17;
   if(type==31){expected[2]=16;expected[3]=*(uint8_t*)(p+4);expected[4]=*(uint8_t*)(p+5);}
   if(type==30||type==38){expected[2]=type==30?14:24;expected[3]=*(uint8_t*)(p+4);unsigned last=type==30?5:9;for(unsigned i=2;i<=last;++i)expected[2+i]=*(uint8_t*)(p+i+4);unsigned d=type==30?6:10,src=type==30?10:14;for(unsigned i=0;i<=6;++i)expected[2+d+i]=*(uint8_t*)(p+src+i);for(unsigned i=7;i<=9;++i)expected[2+d+i]=*(uint8_t*)(p+src+i+1);}
   if(offsets[0]||memcmp(expected,copies[0],300))return 4;
  }++cases;
 }
 const unsigned lengths[]={0,1,228,229,230,246,247,248,458,494,495,65534,65535};
 for(unsigned kind=0;kind<2;++kind)for(unsigned n=0;n<sizeof lengths/sizeof lengths[0];++n)for(unsigned cap=0;cap<3;++cap)for(unsigned old=0;old<2;++old)for(unsigned mode=0;mode<3;++mode){
  unsigned type=kind?32:23,length=lengths[n],d=kind?247:229,c=cap==0?0:cap==1?2:255,count=old?1:0;
  fail=mode==1;shrink=mode==2;allocated=sent=0;memset((void*)p,0,64);*(uint8_t*)(p+2)=type;
  *(uint8_t*)0x8056f9=255;*(uint8_t*)0x8056ef=32;*(uint32_t*)0x805cac=0x807000;*(uint8_t*)0x80700e=c;*(uint8_t*)0x805718=count;
  *(uint16_t*)(p+(kind?10:28))=length;*(uint32_t*)(p+(kind?12:32))=0x820000;
  for(unsigned i=0;i<65536;++i)*(uint8_t*)(uintptr_t)(0x820000u+i)=i*13;
  unsigned need=(uint8_t)((length+d-1)/d);unsigned expected_sent=0,expected_result=0;
  if(need+count<=c&&count<c&&!fail){unsigned rem=length;unsigned curr=count;do{if(curr>=c)break;unsigned chunk=rem<d?rem:d;rem-=chunk;++curr;++expected_sent;if(shrink){c=1;if(rem&&((uint8_t)curr==c)){rem=0;expected_result=0;break;}}if(!rem)expected_result=1;}while(rem);}
  unsigned result=opencfw_em9305_dispatch_330848(p);
  if(result!=expected_result||sent!=expected_sent){printf("fragment bad %u %u %u %u %u %u %u %u %u\n",kind,length,cap,old,mode,result,expected_result,sent,expected_sent);return 5;}
  unsigned progress=0;for(unsigned i=0;i<sent;++i){unsigned chunk=length-progress<d?length-progress:d;unsigned off=kind?10:28;if(offsets[i])return 6;
   uint8_t expected[300];memset(expected,0xa5,300);expected[0]=62;expected[1]=(uint8_t)(chunk+(kind?8:26));
   if(kind){expected[2]=15;for(unsigned j=3;j<=7;++j)expected[j]=0;expected[8]=progress+chunk==length?0:1;expected[9]=chunk;if(sizes[i]!=249)return 8;}
   else{expected[2]=13;expected[3]=1;expected[4]=progress+chunk==length?0:32;for(unsigned j=5;j<27;++j)expected[j]=0;expected[27]=chunk;if(sizes[i]!=231)return 9;}
   for(unsigned j=0;j<chunk;++j)expected[off+j]=(uint8_t)((progress+j)*13);
   if(memcmp(expected,copies[i],300))return 7;
   progress+=chunk;
  }
  ++cases;
 }
 printf("PASS %u\n",cases);return 0;
}
