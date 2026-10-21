#include <stdint.h>
/* Getter6abe4 advertises736 bytes at native2001e054, within cold-zero RAM.
 * The producer lifecycle remains unresolved. Do not populate with vendor data
 * or change736 to the initializer's distinct896-byte admission constant. */
volatile uint8_t r1_crash_payload[736] __attribute__((section(".bss.r1.crash.payload"),aligned(4)));
void *r1_crash_record_marker_set(volatile uint16_t *length)
{
 if(!length)return (void *)0;
 *length=736;
 return (void *)(uintptr_t)r1_crash_payload;
}
