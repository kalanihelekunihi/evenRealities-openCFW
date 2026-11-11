#ifndef R1_NATIVE_HOURLY_STATE_H
#define R1_NATIVE_HOURLY_STATE_H
#include <stddef.h>
#include <stdint.h>
typedef struct __attribute__((may_alias)) {
    uint8_t hour,reserved;
    uint16_t count;
    uint32_t sum;
} r1_hourly_record;
/* Native 0x20016648: five rows, followed by the 80-byte stress prefix at
 * 0x20016670. A native kind-5 access aliases the prefix's first eight bytes. */
struct r1_hourly_stress_storage {
    r1_hourly_record rows[5];
    uint8_t stress[80];
};
extern struct r1_hourly_stress_storage r1_health_hourly_stress_storage;
_Static_assert(sizeof(r1_hourly_record)==8 && offsetof(r1_hourly_record,count)==2 && offsetof(r1_hourly_record,sum)==4,"native hourly record");
_Static_assert(offsetof(struct r1_hourly_stress_storage,stress)==40 && sizeof(struct r1_hourly_stress_storage)==120,"native hourly/stress overlap");
#define r1_health_storage_stress_prefix (r1_health_hourly_stress_storage.stress)
static inline volatile r1_hourly_record *r1_hourly_record_at(uint32_t kind)
{
    return (volatile r1_hourly_record *)(uintptr_t)
        ((uint32_t)(uintptr_t)&r1_health_hourly_stress_storage+(kind<<3));
}
#endif
