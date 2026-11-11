#include <stddef.h>
#include "native_status_ring.h"
/* Native status publisher 0x5e118: control cells at 0x20006938,
 * 0x20006939 and 0x2000693c; records at 0x20019bc8.
 * Stock RW startup initializes the control cells to zero; the zero-init
 * startup handler clears the 128-byte record array. Unowned control bytes
 * between these cells are deliberately not represented here. */
volatile uint8_t r1_status_read_index __attribute__((section(".r1.status.read")))=0;
volatile uint8_t r1_status_write_index __attribute__((section(".r1.status.write")))=0;
volatile uint16_t r1_status_dropped __attribute__((section(".r1.status.dropped"),aligned(2)))=0;
_Static_assert(sizeof(struct r1_status_record)==8 &&
               offsetof(struct r1_status_record,timestamp)==4,
               "native status record layout");
struct r1_status_record r1_status_records[16] __attribute__((section(".r1.status.records"),aligned(4)))={0};
