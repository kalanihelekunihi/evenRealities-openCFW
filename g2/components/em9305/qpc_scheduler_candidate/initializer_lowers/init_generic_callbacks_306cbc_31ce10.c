#include <stdint.h>
extern uintptr_t opencfw_em9305_radio_record_find_31aa64(uint32_t);
/* Full native306cbc..306ce8. Input second survives the finder in R12;
 * record flag write is the unconditional branch delay slot. */
uint32_t opencfw_em9305_callback_306cbc(uint32_t id,uint32_t second){
 uintptr_t record=opencfw_em9305_radio_record_find_31aa64(id);
 if(record==0u)return 66u;
 uint32_t flags=*(volatile uint8_t*)(record+32u);
 *(volatile uint8_t*)(record+2808u)=(uint8_t)second;
 if((flags&16u)!=0u)*(volatile uint8_t*)(uintptr_t)0x805400u=(uint8_t)second;
 return 0u;
}
/* Full native31ce10..31ce4c; LP count captured once; zero count avoids
 * reading the record-array base. Return delay slot sets R0 zero. */
uint32_t opencfw_em9305_callback_31ce10(void){
 uintptr_t configuration=*(volatile uint32_t*)(uintptr_t)0x805cacu;
 uint32_t count=*(volatile uint8_t*)(configuration+57u);
 if(count!=0u){uintptr_t record=*(volatile uint32_t*)(uintptr_t)0x805c3cu;
  do{if(*(volatile uint8_t*)record!=0u&&*(volatile uint8_t*)(record+3u)==1u){uint32_t flags=*(volatile uint8_t*)(record+273u);*(volatile uint8_t*)(record+273u)=(uint8_t)(flags|1u);}record+=512u;}while(--count!=0u);
 }
 return 0u;
}
