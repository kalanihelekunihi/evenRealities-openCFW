extern uint32_t opencfw_em9305_init_schedule_compare_318b78(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_init_schedule_finish_31ec40(uintptr_t);
/* Full native320908..320976. Delay320938 saves the input object pointer,
 * not the insertion result; every retry uses that same slot+16 object. */
uint32_t opencfw_em9305_init_callback_320908(uintptr_t object,uint32_t incoming)
{
 (void)incoming;
 if(*(volatile uint8_t *)(uintptr_t)0x803c28u!=0u){
  uint32_t index=*(volatile uint16_t *)(uintptr_t)0x803c0cu;
  uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
  uintptr_t connection=base+(uint32_t)(uint16_t)index*912u;
  uint32_t initial=*(volatile uint32_t *)(connection+24u);
  uintptr_t schedule=connection+16u;
  uintptr_t compare=(uintptr_t)opencfw_em9305_init_schedule_compare_318b78;
  if(opencfw_em9305_associated_schedule_insert_312da4(schedule,compare)==0u){
   uint32_t iteration=1u;
   do{
    uint32_t period=*(volatile uint16_t *)(connection+266u);
    uint32_t scaled=(uint32_t)(uint16_t)iteration*(uint32_t)(uint16_t)period;
    uint32_t counter=*(volatile uint16_t *)(connection+262u);
    uint32_t offset=opencfw_em9305_native_mpywhl(scaled,1250u);
    *(volatile uint16_t *)(connection+262u)=(uint16_t)(counter+1u);
    *(volatile uint32_t *)(connection+24u)=initial+offset;
    uint32_t success=opencfw_em9305_associated_schedule_insert_312da4(schedule,compare);
    iteration+=1u;if(success!=0u)break;
   }while(1);
  }
 }
 *(volatile uint32_t *)(object+36u)=0x803b94u;
 return opencfw_em9305_init_schedule_finish_31ec40(object);
}
