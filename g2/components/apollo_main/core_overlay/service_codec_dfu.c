/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of platform/audio/service_codec_dfu.c. */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifndef OPEN_CFW_SELECTOR
#define OPEN_CFW_SELECTOR 0
#endif

enum {
    OPEN_CFW_DFU_OK = 0,
    OPEN_CFW_DFU_ERROR = -1,
    OPEN_CFW_DFU_NO_UPGRADE = 1,
    OPEN_CFW_DFU_PACKAGE_HEADER_BYTES = 16,
    OPEN_CFW_DFU_RECORD_BYTES = 16,
    OPEN_CFW_DFU_BOOT_HEADER_BYTES = 32,
    OPEN_CFW_DFU_TRANSFER_CHUNK = 256,
    OPEN_CFW_DFU_FLASH_CHUNK = 0x2000,
    OPEN_CFW_DFU_TIMEOUT_MS = 10000,
    OPEN_CFW_DFU_STAGE_BAUD = 1000000,
    OPEN_CFW_DFU_FLASH_START_TIMEOUT = 9000000,
    OPEN_CFW_DFU_BOOT_TYPE = 1,
    OPEN_CFW_DFU_FIRMWARE_TYPE = 2,
    OPEN_CFW_DFU_MAGIC = 0x4b505746u
};

typedef struct {
    uint32_t type;
    uint32_t size;
    uint32_t file_offset;
    uint32_t crc32;
} open_cfw_dfu_record_t;

#ifndef OPEN_CFW_DFU_BOOT_BUFFER
#define OPEN_CFW_DFU_BOOT_BUFFER \
    (*(uint8_t **)(uintptr_t)0x20074930u)
#endif
#ifndef OPEN_CFW_DFU_BOOT_SIZE
#define OPEN_CFW_DFU_BOOT_SIZE (*(uint32_t *)(uintptr_t)0x20074934u)
#endif
#ifndef OPEN_CFW_DFU_FIRMWARE_BUFFER
#define OPEN_CFW_DFU_FIRMWARE_BUFFER \
    (*(uint8_t **)(uintptr_t)0x20074938u)
#endif
#ifndef OPEN_CFW_DFU_FIRMWARE_SIZE
#define OPEN_CFW_DFU_FIRMWARE_SIZE (*(uint32_t *)(uintptr_t)0x2007493cu)
#endif
#ifndef OPEN_CFW_DFU_VERSION_CACHE
#define OPEN_CFW_DFU_VERSION_CACHE ((uint8_t *)(uintptr_t)0x20074940u)
#endif
#ifndef OPEN_CFW_DFU_BOOT_HEADER
#define OPEN_CFW_DFU_BOOT_HEADER ((uint8_t *)(uintptr_t)0x2007395cu)
#endif
#ifndef OPEN_CFW_DFU_FLASH_SCRATCH
#define OPEN_CFW_DFU_FLASH_SCRATCH ((uint8_t *)(uintptr_t)0x2035ee18u)
#endif

#ifndef OPEN_CFW_DFU_FILE_OPEN
uintptr_t open_cfw_dfu_file_open(const char *path, const char *mode);
#define OPEN_CFW_DFU_FILE_OPEN(path, mode) open_cfw_dfu_file_open((path), (mode))
#endif
#ifndef OPEN_CFW_DFU_FILE_READ
uint32_t open_cfw_dfu_file_read(void *data, uint32_t element_size,
    uint32_t element_count, uintptr_t file);
#define OPEN_CFW_DFU_FILE_READ(data, size, file) \
    open_cfw_dfu_file_read((data), 1u, (size), (file))
#endif
#ifndef OPEN_CFW_DFU_FILE_SEEK
int32_t open_cfw_dfu_file_seek(uintptr_t file, int32_t offset, uint32_t origin);
#define OPEN_CFW_DFU_FILE_SEEK(file, offset) \
    open_cfw_dfu_file_seek((file), (int32_t)(offset), 0u)
#endif
#ifndef OPEN_CFW_DFU_FILE_CLOSE
void open_cfw_dfu_file_close(uintptr_t file);
#define OPEN_CFW_DFU_FILE_CLOSE(file) open_cfw_dfu_file_close((file))
#endif
#ifndef OPEN_CFW_DFU_ALLOCATE
void *open_cfw_dfu_allocate(uint32_t size);
#define OPEN_CFW_DFU_ALLOCATE(size) open_cfw_dfu_allocate((size))
#endif
#ifndef OPEN_CFW_DFU_FREE
void open_cfw_dfu_free(void *pointer);
#define OPEN_CFW_DFU_FREE(pointer) open_cfw_dfu_free((pointer))
#endif
#ifndef OPEN_CFW_DFU_CRC32
uint32_t open_cfw_dfu_crc32(const void *data, uint32_t size);
#define OPEN_CFW_DFU_CRC32(data, size) open_cfw_dfu_crc32((data), (size))
#endif
#ifndef OPEN_CFW_DFU_CRC32_SEEDED
uint32_t open_cfw_dfu_crc32_seeded(uint32_t seed, uint32_t size,
    const void *data);
#define OPEN_CFW_DFU_CRC32_SEEDED(seed, size, data) \
    open_cfw_dfu_crc32_seeded((seed), (size), (data))
#endif
#ifndef OPEN_CFW_DFU_UART_INIT
int32_t open_cfw_dfu_uart_init(void);
#define OPEN_CFW_DFU_UART_INIT() open_cfw_dfu_uart_init()
#endif
#ifndef OPEN_CFW_DFU_UART_CLOSE
int32_t open_cfw_dfu_uart_close(void);
#define OPEN_CFW_DFU_UART_CLOSE() open_cfw_dfu_uart_close()
#endif
#ifndef OPEN_CFW_DFU_UART_SET_BAUD
int32_t open_cfw_dfu_uart_set_baud(uint32_t baud);
#define OPEN_CFW_DFU_UART_SET_BAUD(baud) open_cfw_dfu_uart_set_baud((baud))
#endif
#ifndef OPEN_CFW_DFU_UART_WRITE
int32_t open_cfw_dfu_uart_write(const uint8_t *data, uint32_t size);
#define OPEN_CFW_DFU_UART_WRITE(data, size) \
    open_cfw_dfu_uart_write((data), (size))
#endif
#ifndef OPEN_CFW_DFU_UART_READ
int32_t open_cfw_dfu_uart_read(uint8_t *data, uint32_t size);
#define OPEN_CFW_DFU_UART_READ(data, size) \
    open_cfw_dfu_uart_read((data), (size))
#endif
#ifndef OPEN_CFW_DFU_TIME_MS
uint64_t open_cfw_dfu_time_ms(void);
#define OPEN_CFW_DFU_TIME_MS() open_cfw_dfu_time_ms()
#endif
#ifndef OPEN_CFW_DFU_DELAY
void open_cfw_dfu_delay(uint32_t ticks);
#define OPEN_CFW_DFU_DELAY(ticks) open_cfw_dfu_delay((ticks))
#endif
#ifndef OPEN_CFW_DFU_CODEC_REBOOT
void open_cfw_dfu_codec_reboot(bool skip_boot_wait);
#define OPEN_CFW_DFU_CODEC_REBOOT(skip) open_cfw_dfu_codec_reboot((skip))
#endif
#ifndef OPEN_CFW_DFU_CODEC_VERSION
int32_t open_cfw_dfu_codec_version(uint8_t *version, uint32_t timeout_ms);
#define OPEN_CFW_DFU_CODEC_VERSION(version, timeout) \
    open_cfw_dfu_codec_version((version), (timeout))
#endif

#ifndef OPEN_CFW_DFU_LOAD_PACKAGE
int32_t open_cfw_dfu_load_package(void);
#define OPEN_CFW_DFU_LOAD_PACKAGE() open_cfw_dfu_load_package()
#endif
#ifndef OPEN_CFW_DFU_RELEASE_PACKAGE
void open_cfw_dfu_release_package(void);
#define OPEN_CFW_DFU_RELEASE_PACKAGE() open_cfw_dfu_release_package()
#endif
#ifndef OPEN_CFW_DFU_WAIT_TOKEN
int32_t open_cfw_dfu_wait_token(const uint8_t *token, uint32_t token_size,
    uint32_t timeout_ms);
#define OPEN_CFW_DFU_WAIT_TOKEN(token, size, timeout) \
    open_cfw_dfu_wait_token((token), (size), (timeout))
#endif
#ifndef OPEN_CFW_DFU_READ_BOOT_HEADER
int32_t open_cfw_dfu_read_boot_header(void);
#define OPEN_CFW_DFU_READ_BOOT_HEADER() open_cfw_dfu_read_boot_header()
#endif
#ifndef OPEN_CFW_DFU_STAGE1
int32_t open_cfw_dfu_download_boot_stage1(void);
#define OPEN_CFW_DFU_STAGE1() open_cfw_dfu_download_boot_stage1()
#endif
#ifndef OPEN_CFW_DFU_STAGE2
int32_t open_cfw_dfu_download_boot_stage2(void);
#define OPEN_CFW_DFU_STAGE2() open_cfw_dfu_download_boot_stage2()
#endif
#ifndef OPEN_CFW_DFU_FLASH
int32_t open_cfw_dfu_flash_image(void);
#define OPEN_CFW_DFU_FLASH() open_cfw_dfu_flash_image()
#endif
#ifndef OPEN_CFW_DFU_RUN
int32_t open_cfw_svc_codec_dfu(void);
#define OPEN_CFW_DFU_RUN() open_cfw_svc_codec_dfu()
#endif

int32_t open_cfw_dfu_format_version(uint32_t version, char *output,
    uint32_t capacity);
int32_t open_cfw_dfu_parse_version_bytes(const uint8_t *bytes,
    uint32_t *version);
int32_t open_cfw_dfu_get_package_version(uint32_t *version);
int32_t open_cfw_dfu_validate_firmware_header(uint8_t *header);
bool open_cfw_dfu_host_is_little_endian(void);
uint32_t open_cfw_dfu_bswap32(uint32_t value);
uint32_t open_cfw_dfu_host_to_be32(uint32_t value);

static __attribute__((always_inline, unused)) inline uint32_t open_cfw_dfu_u32(
    const uint8_t *data)
{
    return (uint32_t)data[0] | ((uint32_t)data[1] << 8) |
        ((uint32_t)data[2] << 16) | ((uint32_t)data[3] << 24);
}

static __attribute__((always_inline, unused)) inline void open_cfw_dfu_put_be32(
    uint8_t *data, uint32_t value)
{
    data[0] = (uint8_t)(value >> 24);
    data[1] = (uint8_t)(value >> 16);
    data[2] = (uint8_t)(value >> 8);
    data[3] = (uint8_t)value;
}

static __attribute__((always_inline, unused)) inline void open_cfw_dfu_copy(
    uint8_t *destination, const uint8_t *source, uint32_t size)
{
    uint32_t index;
    for (index = 0u; index < size; ++index) {
        destination[index] = source[index];
    }
}

static __attribute__((always_inline, unused)) inline void open_cfw_dfu_clear(
    uint8_t *destination, uint32_t size)
{
    uint32_t index;
    for (index = 0u; index < size; ++index) {
        destination[index] = 0u;
    }
}

static __attribute__((always_inline, unused)) inline uint32_t
open_cfw_dfu_append_decimal(uint8_t *destination, uint32_t value)
{
    uint8_t reversed[10];
    uint32_t count = 0u;
    uint32_t index;
    do {
        reversed[count++] = (uint8_t)('0' + (value % 10u));
        value /= 10u;
    } while (value != 0u);
    for (index = 0u; index < count; ++index) {
        destination[index] = reversed[count - index - 1u];
    }
    return count;
}

static __attribute__((always_inline, unused)) inline int32_t
open_cfw_dfu_write_all(const uint8_t *data, uint32_t size)
{
    int32_t result = OPEN_CFW_DFU_UART_WRITE(data, size);
    return result < 0 || (result != 0 && (uint32_t)result != size) ? -1 : 0;
}

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 1
__attribute__((used, noinline))
int32_t open_cfw_dfu_load_package(void)
{
    char path[20];
    char mode[3];
    uint8_t header[OPEN_CFW_DFU_PACKAGE_HEADER_BYTES];
    uint8_t raw_record[OPEN_CFW_DFU_RECORD_BYTES];
    open_cfw_dfu_record_t boot = {0u, 0u, 0u, 0u};
    open_cfw_dfu_record_t firmware = {0u, 0u, 0u, 0u};
    uintptr_t file = 0u;
    uint32_t count;
    uint32_t index;
    int32_t status = OPEN_CFW_DFU_ERROR;

    path[0]='/'; path[1]='f'; path[2]='i'; path[3]='r'; path[4]='m';
    path[5]='w'; path[6]='a'; path[7]='r'; path[8]='e'; path[9]='/';
    path[10]='c'; path[11]='o'; path[12]='d'; path[13]='e'; path[14]='c';
    path[15]='.'; path[16]='b'; path[17]='i'; path[18]='n'; path[19]=0;
    mode[0]='r'; mode[1]='b'; mode[2]=0;
    OPEN_CFW_DFU_RELEASE_PACKAGE();
    file = OPEN_CFW_DFU_FILE_OPEN(path, mode);
    if (file == 0u || OPEN_CFW_DFU_FILE_READ(header, sizeof(header), file)
            != (uint32_t)sizeof(header) || open_cfw_dfu_u32(header) != OPEN_CFW_DFU_MAGIC) {
        goto done;
    }
    count = open_cfw_dfu_u32(header + 8);
    if (count == 0u || count > 64u) {
        goto done;
    }
    for (index = 0u; index < count; ++index) {
        open_cfw_dfu_record_t record;
        if (OPEN_CFW_DFU_FILE_READ(raw_record, sizeof(raw_record), file)
                != (uint32_t)sizeof(raw_record)) {
            goto done;
        }
        record.type = open_cfw_dfu_u32(raw_record);
        record.size = open_cfw_dfu_u32(raw_record + 4);
        record.file_offset = open_cfw_dfu_u32(raw_record + 8);
        record.crc32 = open_cfw_dfu_u32(raw_record + 12);
        if (record.type == OPEN_CFW_DFU_BOOT_TYPE) {
            boot = record;
        } else if (record.type == OPEN_CFW_DFU_FIRMWARE_TYPE) {
            firmware = record;
        }
    }
    if (boot.size < OPEN_CFW_DFU_BOOT_HEADER_BYTES || firmware.size == 0u ||
        boot.file_offset < OPEN_CFW_DFU_PACKAGE_HEADER_BYTES ||
        firmware.file_offset < OPEN_CFW_DFU_PACKAGE_HEADER_BYTES) {
        goto done;
    }
    OPEN_CFW_DFU_BOOT_BUFFER = (uint8_t *)OPEN_CFW_DFU_ALLOCATE(boot.size);
    OPEN_CFW_DFU_FIRMWARE_BUFFER =
        (uint8_t *)OPEN_CFW_DFU_ALLOCATE(firmware.size);
    if (OPEN_CFW_DFU_BOOT_BUFFER == NULL || OPEN_CFW_DFU_FIRMWARE_BUFFER == NULL) {
        goto done;
    }
    if (OPEN_CFW_DFU_FILE_SEEK(file, boot.file_offset) != 0 ||
        OPEN_CFW_DFU_FILE_READ(OPEN_CFW_DFU_BOOT_BUFFER, boot.size, file)
            != boot.size ||
        OPEN_CFW_DFU_CRC32(OPEN_CFW_DFU_BOOT_BUFFER, boot.size) != boot.crc32 ||
        OPEN_CFW_DFU_FILE_SEEK(file, firmware.file_offset) != 0 ||
        OPEN_CFW_DFU_FILE_READ(OPEN_CFW_DFU_FIRMWARE_BUFFER, firmware.size, file)
            != firmware.size ||
        OPEN_CFW_DFU_CRC32(OPEN_CFW_DFU_FIRMWARE_BUFFER, firmware.size)
            != firmware.crc32) {
        goto done;
    }
    OPEN_CFW_DFU_BOOT_SIZE = boot.size;
    OPEN_CFW_DFU_FIRMWARE_SIZE = firmware.size;
    status = OPEN_CFW_DFU_OK;
done:
    if (file != 0u) {
        OPEN_CFW_DFU_FILE_CLOSE(file);
    }
    if (status != OPEN_CFW_DFU_OK) {
        OPEN_CFW_DFU_RELEASE_PACKAGE();
    }
    return status;
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 2
__attribute__((used, noinline))
void open_cfw_dfu_release_package(void)
{
    if (OPEN_CFW_DFU_BOOT_BUFFER != NULL) {
        OPEN_CFW_DFU_FREE(OPEN_CFW_DFU_BOOT_BUFFER);
        OPEN_CFW_DFU_BOOT_BUFFER = NULL;
        OPEN_CFW_DFU_BOOT_SIZE = 0u;
    }
    if (OPEN_CFW_DFU_FIRMWARE_BUFFER != NULL) {
        OPEN_CFW_DFU_FREE(OPEN_CFW_DFU_FIRMWARE_BUFFER);
        OPEN_CFW_DFU_FIRMWARE_BUFFER = NULL;
        OPEN_CFW_DFU_FIRMWARE_SIZE = 0u;
    }
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 3
__attribute__((used, noinline))
int32_t open_cfw_dfu_format_version(uint32_t version, char *output,
    uint32_t capacity)
{
    uint8_t values[4];
    uint32_t position = 0u;
    uint32_t part;
    values[0]=(uint8_t)(version>>24); values[1]=(uint8_t)(version>>16);
    values[2]=(uint8_t)(version>>8); values[3]=(uint8_t)version;
    if (output == NULL || capacity < 16u) return OPEN_CFW_DFU_ERROR;
    for (part=0u; part<4u; ++part) {
        uint8_t value=values[part];
        if (value>=100u) output[position++]=(char)('0'+value/100u);
        if (value>=10u) output[position++]=(char)('0'+(value/10u)%10u);
        output[position++]=(char)('0'+value%10u);
        if (part!=3u) output[position++]='.';
    }
    output[position]=0;
    return (int32_t)position;
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 4
__attribute__((used, noinline))
int32_t open_cfw_dfu_parse_version_bytes(const uint8_t *bytes,
    uint32_t *version)
{
    if (bytes == NULL || version == NULL) return OPEN_CFW_DFU_ERROR;
    *version=((uint32_t)bytes[0]<<24)|((uint32_t)bytes[1]<<16)|
        ((uint32_t)bytes[2]<<8)|(uint32_t)bytes[3];
    return OPEN_CFW_DFU_OK;
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 5
__attribute__((used, noinline))
int32_t open_cfw_dfu_get_package_version(uint32_t *version)
{
    char path[20]; char mode[3]; uint8_t header[16]; uintptr_t file; int32_t status=-1;
    if (version==NULL) return -1;
    path[0]='/'; path[1]='f'; path[2]='i'; path[3]='r'; path[4]='m';
    path[5]='w'; path[6]='a'; path[7]='r'; path[8]='e'; path[9]='/';
    path[10]='c'; path[11]='o'; path[12]='d'; path[13]='e'; path[14]='c';
    path[15]='.'; path[16]='b'; path[17]='i'; path[18]='n'; path[19]=0;
    mode[0]='r'; mode[1]='b'; mode[2]=0;
    file=OPEN_CFW_DFU_FILE_OPEN(path,mode); if(file==0u) return -1;
    if(OPEN_CFW_DFU_FILE_READ(header,16u,file)==16 &&
       open_cfw_dfu_u32(header)==OPEN_CFW_DFU_MAGIC){*version=open_cfw_dfu_u32(header+4);status=0;}
    OPEN_CFW_DFU_FILE_CLOSE(file); return status;
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 6
__attribute__((used, noinline))
int32_t open_cfw_dfu_validate_firmware_header(uint8_t *header)
{
    uint32_t offset;
    if(header==NULL) return -1;
    for(offset=8u;offset<=20u;offset+=4u){uint32_t v=open_cfw_dfu_u32(header+offset);open_cfw_dfu_put_be32(header+offset,v);}
    return 0;
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 7
__attribute__((used, noinline)) bool open_cfw_dfu_host_is_little_endian(void)
{ const uint16_t value=1u; return *(const uint8_t *)&value==1u; }
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 8
__attribute__((used, noinline)) uint32_t open_cfw_dfu_bswap32(uint32_t value)
{ return (value>>24)|((value>>8)&0xff00u)|((value<<8)&0xff0000u)|(value<<24); }
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 9
__attribute__((used, noinline)) uint32_t open_cfw_dfu_host_to_be32(uint32_t value)
{ return open_cfw_dfu_host_is_little_endian()?open_cfw_dfu_bswap32(value):value; }
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 10
__attribute__((used, noinline))
int32_t open_cfw_dfu_wait_token(const uint8_t *token,uint32_t token_size,uint32_t timeout_ms)
{
    uint64_t start; uint32_t matched=0u; uint8_t byte;
    if(token==NULL||token_size==0u) return -1; start=OPEN_CFW_DFU_TIME_MS();
    while(OPEN_CFW_DFU_TIME_MS()-start<timeout_ms){
        int32_t count=OPEN_CFW_DFU_UART_READ(&byte,1u);
        if(count<=0){OPEN_CFW_DFU_DELAY(1u);continue;}
        if(byte==token[matched]){if(++matched==token_size)return 0;}
        else matched=(byte==token[0])?1u:0u;
    }
    return -1;
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 11
__attribute__((used, noinline)) int32_t open_cfw_dfu_read_boot_header(void)
{
    if (OPEN_CFW_DFU_BOOT_BUFFER == NULL ||
        OPEN_CFW_DFU_BOOT_SIZE < OPEN_CFW_DFU_BOOT_HEADER_BYTES) return -1;
    open_cfw_dfu_copy(OPEN_CFW_DFU_BOOT_HEADER, OPEN_CFW_DFU_BOOT_BUFFER,
        OPEN_CFW_DFU_BOOT_HEADER_BYTES);
    return open_cfw_dfu_validate_firmware_header(OPEN_CFW_DFU_BOOT_HEADER);
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 12
__attribute__((used, noinline)) int32_t open_cfw_dfu_download_boot_stage1(void)
{
    uint8_t command[5];
    uint8_t wfb[3];
    uint8_t ok[2];
    uint8_t get[3];
    uint32_t transfer_size;
    uint32_t word_count;
    uint32_t offset = 0u;
    const uint32_t baud = OPEN_CFW_DFU_STAGE_BAUD;
    wfb[0]='w'; wfb[1]='f'; wfb[2]='b';
    ok[0]='O'; ok[1]='K';
    get[0]='G'; get[1]='E'; get[2]='T';
    if (OPEN_CFW_DFU_BOOT_BUFFER == NULL ||
        OPEN_CFW_DFU_BOOT_SIZE < OPEN_CFW_DFU_BOOT_HEADER_BYTES) return -1;
    word_count = open_cfw_dfu_u32(OPEN_CFW_DFU_BOOT_HEADER + 8u) / 4u;
    transfer_size = word_count;
    if (OPEN_CFW_DFU_BOOT_HEADER[2] == 1u) transfer_size *= 4u;
    if (transfer_size == 0u || transfer_size >
        OPEN_CFW_DFU_BOOT_SIZE - OPEN_CFW_DFU_BOOT_HEADER_BYTES) return -1;
    command[0] = 0x59u;
    command[1] = (uint8_t)word_count;
    command[2] = (uint8_t)(word_count >> 8);
    command[3] = (uint8_t)(word_count >> 16);
    command[4] = (uint8_t)(word_count >> 24);
    if (open_cfw_dfu_write_all(command, sizeof(command)) != 0) return -1;
    while (offset < transfer_size) {
        uint32_t count = transfer_size - offset;
        if (count > OPEN_CFW_DFU_TRANSFER_CHUNK) count = OPEN_CFW_DFU_TRANSFER_CHUNK;
        if (open_cfw_dfu_write_all(OPEN_CFW_DFU_BOOT_BUFFER +
            OPEN_CFW_DFU_BOOT_HEADER_BYTES + offset, count) != 0) return -1;
        offset += count;
    }
    if (OPEN_CFW_DFU_WAIT_TOKEN(wfb, sizeof(wfb), OPEN_CFW_DFU_TIMEOUT_MS) != 0 ||
        OPEN_CFW_DFU_WAIT_TOKEN(ok, sizeof(ok), OPEN_CFW_DFU_TIMEOUT_MS) != 0 ||
        open_cfw_dfu_write_all(get, sizeof(get)) != 0 ||
        open_cfw_dfu_write_all((const uint8_t *)&baud, sizeof(baud)) != 0 ||
        OPEN_CFW_DFU_WAIT_TOKEN(get, sizeof(get), OPEN_CFW_DFU_TIMEOUT_MS) != 0 ||
        OPEN_CFW_DFU_UART_SET_BAUD(OPEN_CFW_DFU_STAGE_BAUD) != 0 ||
        OPEN_CFW_DFU_WAIT_TOKEN(get, sizeof(get), OPEN_CFW_DFU_TIMEOUT_MS) != 0 ||
        open_cfw_dfu_write_all(ok, sizeof(ok)) != 0) return -1;
    return 0;
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 13
__attribute__((used, noinline)) int32_t open_cfw_dfu_download_boot_stage2(void)
{
    uint8_t command=0x53u;
    uint8_t ready[5];
    uint8_t ok = 'O';
    uint8_t prompt[5];
    uint32_t image_offset = open_cfw_dfu_u32(OPEN_CFW_DFU_BOOT_HEADER + 8u) +
        OPEN_CFW_DFU_BOOT_HEADER_BYTES;
    uint32_t image_size = open_cfw_dfu_u32(OPEN_CFW_DFU_BOOT_HEADER + 16u);
    uint32_t checksum = open_cfw_dfu_u32(OPEN_CFW_DFU_BOOT_HEADER + 20u);
    uint32_t offset=0u;
    ready[0]='r'; ready[1]='e'; ready[2]='a'; ready[3]='d'; ready[4]='y';
    prompt[0]='b'; prompt[1]='o'; prompt[2]='o'; prompt[3]='t'; prompt[4]='>';
    if(OPEN_CFW_DFU_BOOT_BUFFER==NULL || image_size==0u ||
       image_offset > OPEN_CFW_DFU_BOOT_SIZE ||
       image_size > OPEN_CFW_DFU_BOOT_SIZE-image_offset)return -1;
    if(open_cfw_dfu_write_all(&command,1u)!=0 ||
       open_cfw_dfu_write_all((const uint8_t *)&checksum,4u)!=0 ||
       open_cfw_dfu_write_all((const uint8_t *)&image_size,4u)!=0 ||
       OPEN_CFW_DFU_WAIT_TOKEN(ready,sizeof(ready),OPEN_CFW_DFU_TIMEOUT_MS)!=0)return -1;
    while(offset<image_size){uint32_t n=image_size-offset;if(n>256u)n=256u;if(open_cfw_dfu_write_all(OPEN_CFW_DFU_BOOT_BUFFER+image_offset+offset,n)!=0)return -1;offset+=n;}
    if(OPEN_CFW_DFU_WAIT_TOKEN(&ok,1u,OPEN_CFW_DFU_TIMEOUT_MS)!=0 ||
       OPEN_CFW_DFU_WAIT_TOKEN(prompt,sizeof(prompt),OPEN_CFW_DFU_TIMEOUT_MS)!=0)return -1;
    return 0;
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 14
__attribute__((used, noinline)) int32_t open_cfw_dfu_flash_image(void)
{
    uint8_t start[5];uint8_t finish[5];uint8_t result[9];uint8_t success[4];uint32_t offset=0u;uint32_t command_size;uint32_t crc;
    if(OPEN_CFW_DFU_FIRMWARE_BUFFER==NULL||OPEN_CFW_DFU_FIRMWARE_SIZE==0u)return -1;
    open_cfw_dfu_clear(OPEN_CFW_DFU_FLASH_SCRATCH,OPEN_CFW_DFU_FLASH_CHUNK);
    {uint8_t prefix[13]={'s','e','r','i','a','l','d','o','w','n',' ','0',' '};open_cfw_dfu_copy(OPEN_CFW_DFU_FLASH_SCRATCH,prefix,sizeof(prefix));command_size=sizeof(prefix);}
    command_size+=open_cfw_dfu_append_decimal(OPEN_CFW_DFU_FLASH_SCRATCH+command_size,OPEN_CFW_DFU_FIRMWARE_SIZE);
    OPEN_CFW_DFU_FLASH_SCRATCH[command_size++]=' ';
    command_size+=open_cfw_dfu_append_decimal(OPEN_CFW_DFU_FLASH_SCRATCH+command_size,OPEN_CFW_DFU_FLASH_CHUNK);
    crc=OPEN_CFW_DFU_CRC32_SEEDED(0xffffffffu,OPEN_CFW_DFU_FIRMWARE_SIZE,OPEN_CFW_DFU_FIRMWARE_BUFFER);
    if(open_cfw_dfu_write_all(OPEN_CFW_DFU_FLASH_SCRATCH,command_size)!=0||open_cfw_dfu_write_all((const uint8_t *)&crc,4u)!=0)return -1;
    start[0]='~';start[1]='s';start[2]='t';start[3]='a';start[4]='~';
    finish[0]='~';finish[1]='f';finish[2]='i';finish[3]='n';finish[4]='~';
    if(OPEN_CFW_DFU_WAIT_TOKEN(start,5u,OPEN_CFW_DFU_FLASH_START_TIMEOUT)!=0)return -1;
    while(offset<OPEN_CFW_DFU_FIRMWARE_SIZE){uint32_t n=OPEN_CFW_DFU_FIRMWARE_SIZE-offset;if(n>OPEN_CFW_DFU_FLASH_CHUNK)n=OPEN_CFW_DFU_FLASH_CHUNK;if(open_cfw_dfu_write_all(OPEN_CFW_DFU_FIRMWARE_BUFFER+offset,n)!=0)return -1;offset+=n;if(OPEN_CFW_DFU_WAIT_TOKEN(finish,5u,10000u)!=0)return -1;if(offset<OPEN_CFW_DFU_FIRMWARE_SIZE&&OPEN_CFW_DFU_WAIT_TOKEN(start,5u,10000u)!=0)return -1;}
    result[0]='[';result[1]='R';result[2]='e';result[3]='s';result[4]='u';result[5]='l';result[6]='t';result[7]=']';result[8]=':';
    success[0]='S';success[1]='U';success[2]='C';success[3]='C';
    return OPEN_CFW_DFU_WAIT_TOKEN(result,9u,2000u)==0&&OPEN_CFW_DFU_WAIT_TOKEN(success,4u,2000u)==0?0:-1;
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 15
__attribute__((used, noinline)) int32_t open_cfw_svc_codec_dfu(void)
{
    uint8_t sync=0xefu;uint8_t ready='M';int32_t status=-1;
    if(OPEN_CFW_DFU_LOAD_PACKAGE()!=0)return -1;
    if(OPEN_CFW_DFU_UART_INIT()!=0)goto done;
    if(OPEN_CFW_DFU_UART_SET_BAUD(230400u)!=0)goto close;
    OPEN_CFW_DFU_CODEC_REBOOT(true);
    if(open_cfw_dfu_write_all(&sync,1u)!=0||OPEN_CFW_DFU_WAIT_TOKEN(&ready,1u,10000u)!=0)goto close;
    if(OPEN_CFW_DFU_READ_BOOT_HEADER()!=0||OPEN_CFW_DFU_STAGE1()!=0||OPEN_CFW_DFU_STAGE2()!=0||OPEN_CFW_DFU_FLASH()!=0)goto close;
    status=0;
close:
    (void)OPEN_CFW_DFU_UART_CLOSE();OPEN_CFW_DFU_CODEC_REBOOT(false);
done:
    OPEN_CFW_DFU_RELEASE_PACKAGE();return status;
}
#endif

#if OPEN_CFW_SELECTOR == 0 || OPEN_CFW_SELECTOR == 16
__attribute__((used, noinline)) int32_t open_cfw_svc_codec_check_and_upgrade(bool force)
{
    uint32_t package_version;uint32_t running_version=0u;uint8_t version[4];int32_t status;
    if(open_cfw_dfu_get_package_version(&package_version)!=0)return -1;
    if(!force&&OPEN_CFW_DFU_CODEC_VERSION(version,200u)==0&&open_cfw_dfu_parse_version_bytes(version,&running_version)==0&&running_version==package_version)return OPEN_CFW_DFU_NO_UPGRADE;
    status=OPEN_CFW_DFU_RUN();if(status!=0)return status;
    OPEN_CFW_DFU_VERSION_CACHE[0]=(uint8_t)(package_version>>24);OPEN_CFW_DFU_VERSION_CACHE[1]=(uint8_t)(package_version>>16);OPEN_CFW_DFU_VERSION_CACHE[2]=(uint8_t)(package_version>>8);OPEN_CFW_DFU_VERSION_CACHE[3]=(uint8_t)package_version;
    return 0;
}
#endif
