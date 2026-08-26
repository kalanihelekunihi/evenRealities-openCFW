#ifndef OPEN_CFW_SERVICE_TOUCH_DFU_HOST_H
#define OPEN_CFW_SERVICE_TOUCH_DFU_HOST_H
#include <stddef.h>
#include <stdint.h>
extern uintptr_t touch_dfu_ops_words[4];
extern uintptr_t touch_dfu_file_handle;
extern uint8_t *touch_dfu_firmware_buffer;
extern uint32_t touch_dfu_firmware_size;
extern uint32_t touch_dfu_current_version_cache;
#define OPEN_CFW_TOUCH_OPS ((open_cfw_touch_ops_t *)(void *)touch_dfu_ops_words)
#define OPEN_CFW_TOUCH_FILE_HANDLE touch_dfu_file_handle
#define OPEN_CFW_TOUCH_FIRMWARE_BUFFER touch_dfu_firmware_buffer
#define OPEN_CFW_TOUCH_FIRMWARE_SIZE touch_dfu_firmware_size
#define OPEN_CFW_TOUCH_CURRENT_VERSION_CACHE touch_dfu_current_version_cache
#define OPEN_CFW_TOUCH_FILE_OPEN(path, mode) host_touch_file_open((path), (mode))
#define OPEN_CFW_TOUCH_FILE_READ(data, size, file) host_touch_file_read((data), 1u, (size), (file))
#define OPEN_CFW_TOUCH_FILE_SEEK(file, offset) host_touch_file_seek((file), (int32_t)(offset), 0u)
#define OPEN_CFW_TOUCH_FILE_CLOSE(file) host_touch_file_close((file))
#define OPEN_CFW_TOUCH_ALLOCATE(size) host_touch_allocate((size))
#define OPEN_CFW_TOUCH_FREE(pointer) host_touch_free((pointer))
#define OPEN_CFW_TOUCH_DELAY(ticks) host_touch_delay((ticks))
#define OPEN_CFW_TOUCH_RESET() host_touch_reset_controller()
#define OPEN_CFW_TOUCH_SWITCH_TO_DFU() host_touch_switch_to_dfu()
#define OPEN_CFW_TOUCH_READ_CURRENT_VERSION(version) host_touch_read_current_version((version))
uintptr_t host_touch_file_open(const char *path, const char *mode);
uint32_t host_touch_file_read(void *data, uint32_t element_size,
    uint32_t element_count, uintptr_t file);
int32_t host_touch_file_seek(uintptr_t file, int32_t offset, uint32_t origin);
void host_touch_file_close(uintptr_t file);
void *host_touch_allocate(uint32_t size);
void host_touch_free(void *pointer);
void host_touch_delay(uint32_t ticks);
void host_touch_reset_controller(void);
int32_t host_touch_switch_to_dfu(void);
int32_t host_touch_read_current_version(uint32_t *version);
#endif
