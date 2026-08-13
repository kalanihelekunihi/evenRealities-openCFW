#include <stddef.h>
#include <stdint.h>
#include "wsf_efs.h"

volatile uintptr_t open_cfw_wsf_efs_sink;

void *memcpy(void *destination, const void *source, size_t count)
{
    uint8_t *dst = destination;
    const uint8_t *src = source;
    while (count-- != 0) {
        *dst++ = *src++;
    }
    return destination;
}

void *memset(void *destination, int value, size_t count)
{
    uint8_t *dst = destination;
    while (count-- != 0) {
        *dst++ = (uint8_t)value;
    }
    return destination;
}

static uint8_t media_init(void) { return 0; }
static uint8_t media_erase(uint32_t address, uint32_t size) { return (uint8_t)(address ^ size); }
static uint8_t media_read(uint8_t *buffer, uint32_t address, uint32_t size) { return (uint8_t)((uintptr_t)buffer ^ address ^ size); }
static uint8_t media_write(const uint8_t *buffer, uint32_t address, uint32_t size) { return (uint8_t)((uintptr_t)buffer ^ address ^ size); }
static uint8_t media_command(uint8_t command, uint32_t parameter) { return (uint8_t)(command ^ parameter); }

__attribute__((used))
void open_cfw_wsf_efs_closure_root(void)
{
    uint8_t buffer[4] = {0};
    wsfEsfAttributes_t attributes = {{0}, {0}, 0, 0};
    const wsfEfsMedia_t media = {0, 4096, 256, media_init, media_erase, media_read, media_write, media_command};
    open_cfw_wsf_efs_sink ^= (uintptr_t)WsfEfsGetFileByHandle(0);
    WsfEfsInit();
    open_cfw_wsf_efs_sink ^= WsfEfsRegisterMedia(&media, 0);
    open_cfw_wsf_efs_sink ^= WsfEfsAddFile(256, 0, &attributes, WSF_EFS_FILE_OFFSET_ANY);
    open_cfw_wsf_efs_sink ^= WsfEfsRemoveFile(0);
    open_cfw_wsf_efs_sink ^= WsfEfsErase(0);
    open_cfw_wsf_efs_sink ^= WsfEfsGetAttributes(0, &attributes);
    open_cfw_wsf_efs_sink ^= WsfEfsSetAttributes(0, &attributes);
    open_cfw_wsf_efs_sink ^= WsfEfsGet(0, 0, buffer, sizeof(buffer));
    open_cfw_wsf_efs_sink ^= WsfEfsPut(0, 0, buffer, sizeof(buffer));
    open_cfw_wsf_efs_sink ^= (uintptr_t)WsfEfsGetFileName(0);
    open_cfw_wsf_efs_sink ^= (uintptr_t)WsfEfsGetFileVersion(0);
    open_cfw_wsf_efs_sink ^= WsfEfsGetFileMaxSize(0);
    open_cfw_wsf_efs_sink ^= WsfEfsGetFileSize(0);
    open_cfw_wsf_efs_sink ^= WsfEfsGetFileType(0);
    open_cfw_wsf_efs_sink ^= WsfEfsGetFilePermissions(0);
    open_cfw_wsf_efs_sink ^= WsfEfsMediaSpecificCommand(0, 0, 0);
}
