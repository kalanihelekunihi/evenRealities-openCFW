#ifndef R1_NATIVE_EP_STORAGE_H
#define R1_NATIVE_EP_STORAGE_H
#include "native_log_bin.h"
/* Shared FAL partition/flash views have the same observed callback offsets. */
extern volatile uint8_t r1_ep_storage_initialized;
extern struct r1_log_partition *volatile r1_ep_storage_partition;
extern struct r1_log_flash *volatile r1_ep_storage_flash;
uint32_t r1_ep_record_read(uint32_t,void *,uint32_t);
uint32_t r1_ep_record_write(uint32_t,const void *,uint32_t);
uint32_t r1_ep_sector_erase(uint32_t);
uint32_t r1_ep_export_read(uint32_t,void *,uint32_t);
uint32_t r1_ep_export_has_records(void);
void r1_ep_export_crc(uint32_t *);
uint32_t r1_ep_export_length(void);
#endif
