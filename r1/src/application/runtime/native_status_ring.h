#ifndef R1_NATIVE_STATUS_RING_H
#define R1_NATIVE_STATUS_RING_H
#include <stdint.h>
struct r1_status_record {uint32_t packed,timestamp;};
extern volatile uint8_t r1_status_read_index,r1_status_write_index;
extern volatile uint16_t r1_status_dropped;
extern struct r1_status_record r1_status_records[16];
extern volatile uint16_t r1_ep_flash_cursor;
void r1_ep_export_ring_flush(void);
void r1_ep_sector_erase_if_dirty(uint32_t);
#endif
