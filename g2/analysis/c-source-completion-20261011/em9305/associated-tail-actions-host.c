#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
extern uint32_t opencfw_em9305_common_release_304588(uint32_t);
extern uint32_t opencfw_em9305_command_count_down_30e48c(void);
extern uint32_t opencfw_em9305_command_periodic_status_30e878(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_associated_schedule_drop_3136ac(uint32_t);
/* Native324a60..324a88 release, signed2824B row index, schedule removal and count. */
uint32_t opencfw_em9305_associated_release_324a60(uintptr_t record)
{
 (void)opencfw_em9305_common_release_304588(1u);
 int32_t delta=(int32_t)((uint32_t)record-*(volatile uint32_t *)(uintptr_t)0x805c38u),index=delta/2824;
 (void)opencfw_em9305_associated_schedule_drop_3136ac((uint8_t)(index+4));
 return opencfw_em9305_command_count_down_30e48c();
}
uint32_t opencfw_em9305_associated_action_324a8c(uintptr_t record)
{
 (void)opencfw_em9305_associated_release_324a60(record);
 return opencfw_em9305_command_periodic_status_30e878(*(volatile uint8_t *)(record+1u),0u);
}
uint32_t opencfw_em9305_associated_action_324aa0(uintptr_t record)
{ return opencfw_em9305_command_periodic_status_30e878(*(volatile uint8_t *)(record+1u),12u); }
uint32_t opencfw_em9305_associated_action_324c60(uintptr_t record)
{ return opencfw_em9305_command_periodic_status_30e878(*(volatile uint8_t *)(record+1u),0u); }

static uint8_t row[8],message[6];static unsigned released,removed,dropped,steps;
uint32_t opencfw_em9305_common_release_304588(uint32_t v){if(v!=1)abort();released++;return 911;}
uint32_t opencfw_em9305_associated_schedule_drop_3136ac(uint32_t id){removed++;dropped=id;return 92;}
uint32_t opencfw_em9305_command_count_down_30e48c(void){steps++;row[1]++;return 90;}
uint32_t opencfw_em9305_command_periodic_status_30e878(uint32_t id,uint32_t status){message[5]=(uint8_t)id;*(uint16_t*)(void*)message=(uint16_t)id;message[4]=(uint8_t)status;message[3]=(uint8_t)status;message[2]=29;return 0xfeed0912;}
int main(void){
 if(mmap((void*)0x805000,4096,3,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0)==MAP_FAILED)return 2;
 unsigned cases=0;
 for(int index=-128;index<128;index++)for(unsigned id=0;id<256;id++)for(unsigned action=0;action<3;action++){
 row[1]=id;released=removed=steps=0;*(volatile uint32_t*)0x805c38=(uint32_t)((uintptr_t)row-(uint32_t)(index*2824));
 uint32_t result=action==0?opencfw_em9305_associated_action_324a8c((uintptr_t)row):action==1?opencfw_em9305_associated_action_324aa0((uintptr_t)row):opencfw_em9305_associated_action_324c60((uintptr_t)row);
 unsigned finalid=(uint8_t)(id+(action==0)),status=action==1?12:0;
 if(result!=0xfeed0912||message[5]!=finalid||*(uint16_t*)(void*)message!=finalid||message[2]!=29||message[3]!=status||message[4]!=status||released!=(action==0)||removed!=(action==0)||steps!=(action==0)||(action==0&&dropped!=(uint8_t)(index+4)))abort();
 cases++;
 }
 printf("PASS %u associated tail ABI/index cases\n",cases);return 0;
}
