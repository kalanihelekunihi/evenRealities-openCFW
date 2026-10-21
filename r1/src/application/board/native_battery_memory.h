#ifndef R1_NATIVE_BATTERY_MEMORY_H
#define R1_NATIVE_BATTERY_MEMORY_H
#include <stdint.h>
/* Cortex-M4 SRAM views preserve the native unaligned halfword/word accesses.
 * Compile these selected units with -munaligned-access; do not apply to MMIO. */
typedef struct __attribute__((packed,may_alias)) { uint16_t value; } r1_battery_word16;
typedef struct __attribute__((packed,may_alias)) { uint32_t value; } r1_battery_word32;
static inline uint16_t read16(const volatile uint8_t *p) { return ((const volatile r1_battery_word16 *)(const volatile void *)p)->value; }
static inline uint32_t read32(const volatile uint8_t *p) { return ((const volatile r1_battery_word32 *)(const volatile void *)p)->value; }
static inline void write16(volatile uint8_t *p,uint32_t v) { ((volatile r1_battery_word16 *)(volatile void *)p)->value=(uint16_t)v; }
static inline void write32(volatile uint8_t *p,uint32_t v) { ((volatile r1_battery_word32 *)(volatile void *)p)->value=v; }
#endif
