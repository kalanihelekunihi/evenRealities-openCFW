#ifndef OPEN_CFW_SERVICE_CODEC_DFU_HOST_H
#define OPEN_CFW_SERVICE_CODEC_DFU_HOST_H
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
extern uint8_t *codec_dfu_boot_buffer;
extern uint32_t codec_dfu_boot_size;
extern uint8_t *codec_dfu_firmware_buffer;
extern uint32_t codec_dfu_firmware_size;
extern uint8_t codec_dfu_version_cache[4];
extern uint8_t codec_dfu_boot_header[32];
extern uint8_t codec_dfu_flash_scratch[8192];
void host_dfu_clear_tx(void);
uint32_t host_dfu_copy_tx(uint8_t *destination, uint32_t capacity);
#define OPEN_CFW_DFU_BOOT_BUFFER codec_dfu_boot_buffer
#define OPEN_CFW_DFU_BOOT_SIZE codec_dfu_boot_size
#define OPEN_CFW_DFU_FIRMWARE_BUFFER codec_dfu_firmware_buffer
#define OPEN_CFW_DFU_FIRMWARE_SIZE codec_dfu_firmware_size
#define OPEN_CFW_DFU_VERSION_CACHE codec_dfu_version_cache
#define OPEN_CFW_DFU_BOOT_HEADER codec_dfu_boot_header
#define OPEN_CFW_DFU_FLASH_SCRATCH codec_dfu_flash_scratch
#endif
