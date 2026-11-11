#ifndef R1_NATIVE_EXPORT_SNAPSHOT_H
#define R1_NATIVE_EXPORT_SNAPSHOT_H
#include <stdint.h>

struct r1_export_file_descriptor {
    uint32_t identifier;
    uint32_t length;
    uint32_t crc;
    uint32_t (*prepare)(uint32_t *);
    uint32_t (*read)(uint32_t,void *,uint32_t);
    uint32_t (*start)(void);
    uint32_t (*finish)(void);
    const uint8_t *marker;
};

extern struct r1_export_file_descriptor r1_log_export_file;
extern volatile int8_t r1_log_export_start_sector;
extern volatile uint16_t r1_log_export_cache_length;
uint32_t r1_log_export_snapshot_read(uint32_t,void *,uint32_t);
uint32_t r1_log_export_snapshot_prepare(uint32_t *);
#endif
