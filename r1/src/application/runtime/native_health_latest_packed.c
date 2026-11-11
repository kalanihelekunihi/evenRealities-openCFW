#include <stdint.h>
#include <stddef.h>
/* Packed volatile fields retain native unaligned access widths and order. */
typedef struct __attribute__((packed,may_alias)) { uint32_t value; } wire32;
typedef struct __attribute__((packed,may_alias)) { uint16_t value; } wire16;
_Static_assert(sizeof(wire32)==4 && _Alignof(wire32)==1 && sizeof(wire16)==2 && _Alignof(wire16)==1,"wire access ABI");
extern uint8_t r1_health_storage_hr_prefix[],r1_health_storage_hrv_prefix[],r1_health_storage_spo2_prefix[];
__attribute__((noinline)) uint32_t r1_hr_latest_packed(void *destination) {
 if(destination==NULL || *(const volatile uint8_t *)(r1_health_storage_hr_prefix+75)==0) return 0;
 ((volatile wire32 *)destination)->value = ((const volatile wire32 *)(r1_health_storage_hr_prefix+75))->value;
 *((volatile uint8_t *)destination+4) = *(const volatile uint8_t *)(r1_health_storage_hr_prefix+79);
 return 1;
}
__attribute__((noinline)) uint32_t r1_hrv_latest_packed(void *destination) {
 if(destination==NULL || ((const volatile wire16 *)(r1_health_storage_hrv_prefix+147))->value==0) return 0;
 ((volatile wire32 *)destination)->value = ((const volatile wire32 *)(r1_health_storage_hrv_prefix+147))->value;
 ((volatile wire16 *)((uint8_t *)destination+4))->value = ((const volatile wire16 *)(r1_health_storage_hrv_prefix+151))->value;
 return 1;
}
__attribute__((noinline)) uint32_t r1_spo2_latest_packed(void *destination) {
 if(destination==NULL || *(const volatile uint8_t *)(r1_health_storage_spo2_prefix+75)==0) return 0;
 ((volatile wire32 *)destination)->value = ((const volatile wire32 *)(r1_health_storage_spo2_prefix+75))->value;
 *((volatile uint8_t *)destination+4) = *(const volatile uint8_t *)(r1_health_storage_spo2_prefix+79);
 return 1;
}
