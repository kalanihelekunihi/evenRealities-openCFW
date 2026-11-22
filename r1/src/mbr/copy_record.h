#ifndef R1_MBR_COPY_RECORD_H
#define R1_MBR_COPY_RECORD_H

#include <stdint.h>

#define R1_MBR_COPY_MAGIC 0x52314d42u
#define R1_MBR_COPY_PAGE 0x000fe000u
#define R1_MBR_BOOTLOADER_BASE 0x000f8000u
#define R1_MBR_BOOTLOADER_LIMIT 0x000fe000u
#define R1_MBR_APPLICATION_BASE 0x00027000u
#define R1_MBR_PAGE_BYTES 4096u
#define R1_MBR_STAGE_TAG_ADDRESS 0x000007fcu
#define R1_MBR_STAGE_TAG 0x52315354u
#define R1_MBR_STAGE_ENTRY 0x00000801u
#define R1_MBR_CORDIO_INIT_TAG_ADDRESS 0x000008fcu
#define R1_MBR_CORDIO_INIT_TAG 0x52314349u
#define R1_MBR_CORDIO_INIT_ENTRY 0x00000901u
#define R1_MBR_COMMAND_TAG_ADDRESS 0x00000afcu
#define R1_MBR_COMMAND_TAG 0x5231434du
#define R1_MBR_COMMAND_ENTRY 0x00000b01u

typedef enum {
    R1_MBR_STAGE_OK = 0,
    R1_MBR_STAGE_UNSUPPORTED,
    R1_MBR_STAGE_FORBIDDEN,
    R1_MBR_STAGE_LENGTH,
    R1_MBR_STAGE_ADDRESS,
    R1_MBR_STAGE_FLASH_ERROR
} r1_mbr_stage_result_t;

typedef struct {
    uint32_t magic;
    uint32_t magic_inverse;
    uint32_t source;
    uint32_t length_words;
    uint32_t destination;
    uint32_t checksum;
} r1_mbr_copy_record_t;

static inline uint32_t r1_mbr_copy_checksum(uint32_t source,
                                             uint32_t length_words,
                                             uint32_t destination)
{
    return R1_MBR_COPY_MAGIC ^ source ^ length_words ^ destination ^ 0xa5a55a5au;
}

#endif
