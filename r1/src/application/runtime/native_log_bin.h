#ifndef R1_NATIVE_LOG_BIN_H
#define R1_NATIVE_LOG_BIN_H
#include <stdint.h>
struct r1_log_partition {uint8_t prefix[52];uint32_t base,length;};
struct r1_log_flash {uint8_t prefix[40];uint32_t (*read)(uint32_t,void *,uint32_t);uint32_t (*write)(uint32_t,const void *,uint32_t);uint32_t (*erase)(uint32_t,uint32_t);};
extern volatile uint8_t r1_log_bin_initialized,r1_log_bin_sector;
extern struct r1_log_partition *volatile r1_log_bin_partition;
extern struct r1_log_flash *volatile r1_log_bin_flash;
extern volatile uint32_t r1_log_bin_offset;
uint32_t r1_log_bin_sector_count(void);
void r1_log_bin_write(const void *,uint32_t);
#endif
