extern uint32_t opencfw_em9305_associated_radio_callback_32b538(uintptr_t);
extern uint32_t opencfw_em9305_associated_packet_callback_32c69c(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_associated_object_init_312918(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_associated_slot_allocate_3133b4(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_associated_schedule_insert_312da4(uintptr_t,uint32_t);
/* Native32b2d0 true tail to32b538, represented with actual source relocation. */
uint32_t opencfw_em9305_associated_radio_tail_32b2d0(uintptr_t record)
{ return opencfw_em9305_associated_radio_callback_32b538(record); }
/* Native31896c..318986 keeps named XBFU and native low-bit BMSK semantics. */
uint32_t opencfw_em9305_associated_random_31896c(void)
{
 uint32_t value=opencfw_em9305_pal_random_step(),first,second;
 __asm__ volatile("xbfu %0,%1,0x28":"=r"(first):"r"(value));
 __asm__ volatile("xbfu %0,%1,0x10":"=r"(second):"r"(value));
 return (value&7u)+first+second+5u;
}
/* Native31b2fc..31b32a: exact signed low-word2824B record stride. */
uint32_t opencfw_em9305_associated_slot_query_31b2fc(uint32_t id,uintptr_t output)
{
 uint32_t offset=opencfw_em9305_native_mpywhl(id-4u,2824u);
 uintptr_t record=*(volatile uint32_t *)(uintptr_t)0x805c38u;record+=offset;
 if(*(volatile uint8_t *)(record+368u)!=1u)return 0u;
 uint32_t result=*(volatile uint32_t *)(record+388u);
 if(output!=0u){uint32_t extent=*(volatile uint32_t *)(record+392u);*(volatile uint32_t *)output=extent;}
 return result;
}
static uint32_t opencfw_em9305_associated_macwhul(uint32_t prior,uint32_t factor,uint32_t iteration)
{uint32_t result;__asm__ volatile("mov r58,%1\n\tmacwhul 0,%2,%3\n\tmov %0,r58":"=r"(result):"r"(prior),"r"(factor),"r"(iteration));return result;}
/* Native32b2d4..32b4e2 complete validation/record/scheduler parent. */
uint32_t opencfw_em9305_associated_validate_32b2d4(uintptr_t record)
{
 uintptr_t object=record+380u;
 (void)opencfw_em9305_memset((void *)object,0u,148u);
 *(volatile uint8_t *)(record+406u)=1u;*(volatile uint8_t *)(record+404u)=1u;
 *(volatile uint32_t *)(record+412u)=(uint32_t)(uintptr_t)opencfw_em9305_associated_radio_tail_32b2d0;
 *(volatile uint32_t *)(record+408u)=(uint32_t)(uintptr_t)opencfw_em9305_associated_radio_callback_32b538;
 *(volatile uint32_t *)(record+416u)=(uint32_t)record;
 *(volatile uint32_t *)(record+424u)=(uint32_t)(record+428u);
 *(volatile uint32_t *)(record+420u)=(uint32_t)(record+1144u);
 uint32_t random=opencfw_em9305_associated_random_31896c();
 int32_t power=*(volatile int8_t *)(record+60u);uint32_t channel=*(volatile uint8_t *)(record+697u);
 *(volatile uint8_t *)(record+696u)=(uint8_t)random;
 *(volatile uint8_t *)(record+428u)=8u;*(volatile uint8_t *)(record+429u)=(uint8_t)channel;
 if(power==127)power=*(volatile uint8_t *)(uintptr_t)0x805a9cu;
 uint32_t access=*(volatile uint32_t *)(record+372u);
 *(volatile uint8_t *)(record+430u)=(uint8_t)power;
 *(volatile uint32_t *)(record+432u)=access;
 uint32_t crc=opencfw_em9305_radio_crc_seed_318960();
 uint32_t mode=*(volatile uint8_t *)(record+69u);
 *(volatile uint32_t *)(record+436u)=crc;
 *(volatile uint32_t *)(record+568u)=(uint32_t)(record+1077u);
 *(volatile uint32_t *)(record+532u)=(uint32_t)(record+1077u);
 *(volatile uint16_t *)(record+1154u)=0u;
 uint32_t index=mode-1u,decoded=index<4u?(0x02010201u>>((index&3u)*8u)):0u;
 uint32_t phy=*(volatile uint8_t *)(record+63u);
 *(volatile uint8_t *)(record+443u)=(uint8_t)decoded;*(volatile uint8_t *)(record+442u)=(uint8_t)decoded;
 *(volatile uint32_t *)(record+588u)=(uint32_t)(uintptr_t)opencfw_em9305_associated_packet_callback_32c69c;
 *(volatile uint8_t *)(record+441u)=(uint8_t)phy;*(volatile uint8_t *)(record+440u)=(uint8_t)phy;
 (void)opencfw_em9305_associated_object_init_312918(object,0u);
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t spacing=*(volatile uint16_t *)(config+20u),budget=*(volatile uint32_t *)(record+72u);
 uint32_t maximum=*(volatile uint32_t *)(record+712u),minimum=*(volatile uint32_t *)(record+708u);
 if(budget>spacing)spacing=budget;
 uint32_t timing=0u;
 if(*(volatile uint8_t *)(record+804u)!=0u){uintptr_t callback=*(volatile uint32_t *)(uintptr_t)0x801a14u;if(callback!=0u)timing=((uint32_t (*)(void))callback)();}
 uint32_t size=*(volatile uint16_t *)(record+1144u);
 phy=*(volatile uint8_t *)(record+63u);
 uint32_t duration=opencfw_em9305_radio_duration_312be4(phy,0u,timing,(uint16_t)spacing,size,1u,2u,0u);
 config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t chosen=*(volatile uint16_t *)(config+28u);
 if(chosen<duration){size=*(volatile uint16_t *)(record+1144u);phy=*(volatile uint8_t *)(record+63u);chosen=opencfw_em9305_radio_duration_312be4(phy,0u,timing,(uint16_t)spacing,size,1u,2u,0u);}
 uint32_t extent=*(volatile uint32_t *)(record+392u);if(chosen>extent)extent=chosen;
 *(volatile uint32_t *)(record+392u)=extent;
 if(maximum<chosen)return 69u;
 if(chosen>minimum)minimum=chosen;
 int32_t delta=(int32_t)((uint32_t)record-*(volatile uint32_t *)(uintptr_t)0x805c38u),row;
 __asm__ volatile("div %0,%1,2824":"=r"(row):"r"(delta));
 volatile uint32_t allocation;
 uint32_t success=opencfw_em9305_associated_slot_allocate_3133b4((uint8_t)(row+4),1u,minimum,maximum,extent,(uintptr_t)&allocation,(uintptr_t)opencfw_em9305_associated_slot_query_31b2fc);
 if(success==0u)return 67u;
 uint32_t base=*(volatile uint32_t *)(record+2476u),selected=allocation;
 *(volatile uint32_t *)(record+700u)=selected;*(volatile uint32_t *)(record+400u)=selected;
 if(base==0u){selected=*(volatile uint32_t *)(record+700u);base=opencfw_em9305_pal_current_time();}
 delta=(int32_t)((uint32_t)record-*(volatile uint32_t *)(uintptr_t)0x805c38u);
 __asm__ volatile("div %0,%1,2824":"=r"(row):"r"(delta));
 uint32_t elapsed=opencfw_em9305_radio_schedule_313424(selected,(uint8_t)(row+4),base,0u,0u);
 uint32_t half=*(volatile uint32_t *)(record+36u);if(elapsed==half)elapsed=half>>1u;
 uint32_t first=elapsed+base,next=first,iteration=1u;
 for(;;){
  *(volatile uint32_t *)(record+388u)=next;
  if(opencfw_em9305_associated_schedule_insert_312da4(object,0u)!=0u)return 0u;
  uint32_t count=*(volatile uint16_t *)(record+752u);selected=*(volatile uint32_t *)(record+700u);
  count+=1u;next=opencfw_em9305_associated_macwhul(first,selected,iteration);
  *(volatile uint16_t *)(record+752u)=(uint16_t)count;iteration+=1u;
 }
}
