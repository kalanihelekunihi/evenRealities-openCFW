#include <stdint.h>
#include <stddef.h>
typedef struct {uint8_t hour,reserved;uint16_t count;uint32_t sum;} r1_hourly_record;
_Static_assert(sizeof(r1_hourly_record)==8 && offsetof(r1_hourly_record,count)==2 && offsetof(r1_hourly_record,sum)==4,"native hourly record");
/* Six records at native20016648, inside authenticated cold zero range.
 * Producers and real health initialization remain independent providers. */
volatile r1_hourly_record r1_hourly_accumulators[6] __attribute__((section(".bss.r1.hourly.accumulators"),aligned(4)));
uint32_t r1_hr_hour_query(uint32_t kind,uint32_t hour,volatile uint32_t *sum,volatile uint16_t *count)
{
 if(!sum || !count)return kind;
 *sum=0;*count=0;
 if(kind>5)return kind;
 volatile r1_hourly_record *record=&r1_hourly_accumulators[kind];
 if(!record->count || record->hour!=hour)return (uint32_t)(uintptr_t)record;
 *sum=record->sum;
 uint32_t fresh=record->count;
 *count=(uint16_t)fresh;
 return fresh;
}
