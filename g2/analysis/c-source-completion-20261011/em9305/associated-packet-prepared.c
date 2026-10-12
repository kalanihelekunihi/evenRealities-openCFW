extern uint32_t opencfw_em9305_associated_packet_refill_3259fc(uintptr_t);
extern uint32_t opencfw_em9305_associated_packet_continue_323ac8(uintptr_t,uintptr_t,uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_associated_packet_start_3243e0(uintptr_t,uintptr_t,uintptr_t,uint32_t);
static inline uint32_t opencfw_em9305_associated_packet_high_product(uint32_t value,uint32_t factor)
{uint32_t result;__asm__ volatile("mpymu %0,%1,%2":"=r"(result):"r"(value),"r"(factor));return result;}
/* Native32c69c..32c7e2 registered packet callback, saved return slot692. */
uint32_t opencfw_em9305_associated_packet_callback_32c69c(uintptr_t object,uint32_t continuing)
{
 uintptr_t record=*(volatile uint32_t *)(object+36u),state=record+176u;
 uint32_t channel=*(volatile uint8_t *)(record+697u),saved=*(volatile uint32_t *)(record+692u);
 *(volatile uint8_t *)(record+429u)=(uint8_t)channel;
 if(continuing!=0u){
  uint32_t enabled=*(volatile uint8_t *)(record+804u),consumed=*(volatile uint16_t *)(record+1154u);
  if(enabled!=0u){uint32_t count=*(volatile uint8_t *)(record+806u);*(volatile uint8_t *)(record+806u)=(uint8_t)(count-1u);}
  uint32_t size=*(volatile uint16_t *)(record+1144u);
  if(consumed<size||*(volatile uint8_t *)(record+806u)!=0u)(void)opencfw_em9305_associated_packet_refill_3259fc(record);
  uint32_t result=opencfw_em9305_associated_packet_continue_323ac8(record,record+1077u,record+1144u,1u);
  uintptr_t cursor=*(volatile uint32_t *)(record+1148u);
  uint32_t available=*(volatile uint16_t *)(record+1154u);
  *(volatile uint16_t *)(record+564u)=(uint16_t)result;
  *(volatile uint32_t *)(record+576u)=(uint32_t)(cursor+consumed);
  *(volatile uint16_t *)(record+572u)=(uint16_t)(available-consumed);
 }else{
  uint32_t custom=*(volatile uint8_t *)(record+2809u),restore=0u;
  *(volatile uint16_t *)(record+1154u)=0u;
  if(custom==0u)(void)opencfw_em9305_associated_packet_refill_3259fc(record);
  if(*(volatile uint8_t *)state==1u){
   uint32_t timestamp=*(volatile uint32_t *)(object+8u),target=*(volatile uint32_t *)(state+4u),elapsed=target-timestamp;
   if(elapsed<=599u){
    uint32_t period=*(volatile uint16_t *)(record+190u),increment=*(volatile uint8_t *)(record+193u);
    uint32_t low=*(volatile uint32_t *)(state+60u),high=*(volatile uint32_t *)(state+64u);
    uint32_t next=low+increment;high+=(next<low);
    elapsed+=period*1250u;
    *(volatile uint32_t *)(state+60u)=next;*(volatile uint32_t *)(state+64u)=high;
   }
   uint32_t quantized;
   if(elapsed<0x77fc4u){
    quantized=opencfw_em9305_associated_packet_high_product(elapsed,0x11111112u)>>1u;
    *(volatile uint8_t *)(state+12u)=0u;
   }else{
    uint32_t high=opencfw_em9305_associated_packet_high_product(elapsed,0x69d0369eu);
    *(volatile uint8_t *)(state+12u)=1u;
    quantized=(elapsed*3u+high)>>10u;
   }
   uint32_t period=*(volatile uint16_t *)(record+190u);
   *(volatile uint16_t *)(record+186u)=(uint16_t)quantized;
   if(period==0u||period*1250u<elapsed){restore=1u;*(volatile uint8_t *)state=255u;}
  }
  custom=*(volatile uint8_t *)(record+2809u);
  if(custom!=0u){
   uintptr_t callback=*(volatile uint32_t *)(record+2816u);
   (void)((uint32_t (*)(uintptr_t,uintptr_t))callback)(record,callback);
  }else{
   uint32_t result=opencfw_em9305_associated_packet_start_3243e0(record,record+1077u,record+1144u,1u);
   *(volatile uint16_t *)(record+528u)=(uint16_t)result;
  }
  if(restore!=0u)*(volatile uint8_t *)state=1u;
  uint32_t available=*(volatile uint16_t *)(record+1154u);
  uintptr_t cursor=*(volatile uint32_t *)(record+1148u);
  *(volatile uint16_t *)(record+536u)=(uint16_t)available;
  *(volatile uint32_t *)(record+540u)=(uint32_t)cursor;
 }
 return saved;
}
