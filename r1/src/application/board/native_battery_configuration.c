#include <stdint.h>
#include "native_kv_class.h"
#include "native_battery_memory.h"
extern void *volatile r1_batcfg_record_kv_handle;
extern uint32_t r1_nv_modules_idle_check(void);
/* Ignore cached-read status as stock does. C entry frames initialize unwritten
 * bytes to zero instead of retaining the native private saved-R3 word. */
__attribute__((used,noinline)) uint32_t r1_batcfg_byte0_body(
 const volatile uint8_t *frame)
{
 (void)r1_kv_class_read(r1_batcfg_record_kv_handle,
                       (void *)(uintptr_t)frame, 4);
 return frame[0];
}
__attribute__((used,noinline)) uint32_t r1_batcfg_flag1_body(
 const volatile uint8_t *frame)
{
 (void)r1_kv_class_read(r1_batcfg_record_kv_handle,
                       (void *)(uintptr_t)frame, 4);
 return read16(frame+2) != 0;
}
__attribute__((used,noinline)) uint32_t r1_batcfg_word1_signed_body(
 const volatile uint8_t *frame)
{
 (void)r1_kv_class_read(r1_batcfg_record_kv_handle,
                       (void *)(uintptr_t)frame, 4);
 return (uint32_t)(int32_t)(int16_t)read16(frame+2);
}
#define CACHED_GETTER(name,body) \
 uint32_t name(void) { \
  _Alignas(4) uint8_t frame[4]={0}; return body(frame); \
 }
CACHED_GETTER(r1_batcfg_byte0_get,r1_batcfg_byte0_body)
CACHED_GETTER(r1_batcfg_flag1_get,r1_batcfg_flag1_body)
CACHED_GETTER(r1_batcfg_word1_signed_get,r1_batcfg_word1_signed_body)
#undef CACHED_GETTER

/* Stock 0x7bb94 and 0x7bbc0 update the four-byte cached power record. */
uint32_t r1_kv_power_byte_set(uint32_t value)
{
    _Alignas(4) uint8_t record[4];
    (void)r1_kv_class_read(r1_batcfg_record_kv_handle, record, sizeof(record));
    record[0] = (uint8_t)value;
    (void)r1_kv_class_write(r1_batcfg_record_kv_handle, record, sizeof(record));
    return r1_nv_modules_idle_check();
}

uint32_t r1_kv_power_field_set(uint32_t value)
{
    _Alignas(4) uint8_t record[4];
    (void)r1_kv_class_read(r1_batcfg_record_kv_handle, record, sizeof(record));
    record[2] = (uint8_t)value;
    record[3] = (uint8_t)(value >> 8u);
    (void)r1_kv_class_write(r1_batcfg_record_kv_handle, record, sizeof(record));
    return r1_nv_modules_idle_check();
}

/* Stock 0x7bbbc is a direct return from its caller-supplied R0. */
uint32_t r1_legacy_battery_hook_nop(uint32_t value) { return value; }
