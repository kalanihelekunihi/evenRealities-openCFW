#include <stdint.h>
#include <stddef.h>
#include "native_hourly_state.h"
uint32_t r1_hr_hour_query(uint32_t kind,uint32_t hour,volatile uint32_t *sum,volatile uint16_t *count)
{
 if(!sum || !count)return kind;
 *sum=0;*count=0;
 if(kind>5)return kind;
 volatile r1_hourly_record *record=r1_hourly_record_at(kind);
 if(!record->count || record->hour!=hour)return (uint32_t)(uintptr_t)record;
 *sum=record->sum;
 uint32_t fresh=record->count;
 *count=(uint16_t)fresh;
 return fresh;
}

/* Stock 0x5acc4: shared record owner, ordered hour/sum/count stores. */
void r1_shared_hourly_accumulator_restore(uint32_t kind,uint32_t hour,uint32_t sum,uint32_t count)
{
 if(kind>5 || !count)return;
 volatile r1_hourly_record *record=r1_hourly_record_at(kind);
 record->hour=(uint8_t)hour;record->sum=sum;record->count=(uint16_t)count;
}
