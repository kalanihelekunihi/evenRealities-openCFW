#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include "service_codec_dfu_host.h"

uint8_t *codec_dfu_boot_buffer;
uint32_t codec_dfu_boot_size;
uint8_t *codec_dfu_firmware_buffer;
uint32_t codec_dfu_firmware_size;
uint8_t codec_dfu_version_cache[4];
uint8_t codec_dfu_boot_header[32];
uint8_t codec_dfu_flash_scratch[8192];
static uint8_t package_data[1024];
static uint32_t package_size, file_position;
static uint8_t uart_rx[32768], uart_tx[32768], codec_version[4];
static uint32_t uart_rx_size, uart_rx_position, uart_tx_size;
static uint64_t clock_ms;
static int fail_alloc, fail_uart_init, fail_uart_baud;
static uint32_t close_count, reboot_true_count, reboot_false_count;

static void put32(uint8_t *p,uint32_t v){p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);p[2]=(uint8_t)(v>>16);p[3]=(uint8_t)(v>>24);}
static void putbe32(uint8_t *p,uint32_t v){p[0]=(uint8_t)(v>>24);p[1]=(uint8_t)(v>>16);p[2]=(uint8_t)(v>>8);p[3]=(uint8_t)v;}
uint32_t open_cfw_dfu_crc32(const void *pointer,uint32_t size){const uint8_t *p=pointer;uint32_t c=0xffffffffu,i,b;for(i=0;i<size;i++){c^=p[i];for(b=0;b<8;b++)c=(c>>1)^((0u-(c&1u))&0xedb88320u);}return ~c;}
uint32_t open_cfw_dfu_crc32_seeded(uint32_t seed,uint32_t size,const void *pointer){const uint8_t *p=pointer;uint32_t c=seed,i,b;for(i=0;i<size;i++){c^=p[i];for(b=0;b<8;b++)c=(c>>1)^((0u-(c&1u))&0xedb88320u);}return c^0xffffffffu;}
void host_dfu_reset(void){free(codec_dfu_boot_buffer);free(codec_dfu_firmware_buffer);codec_dfu_boot_buffer=0;codec_dfu_firmware_buffer=0;codec_dfu_boot_size=codec_dfu_firmware_size=0;memset(codec_dfu_version_cache,0,4);memset(codec_dfu_boot_header,0,32);memset(codec_dfu_flash_scratch,0xa5,8192);package_size=file_position=uart_rx_size=uart_rx_position=uart_tx_size=0;clock_ms=0;fail_alloc=fail_uart_init=fail_uart_baud=0;close_count=reboot_true_count=reboot_false_count=0;codec_version[0]=1;codec_version[1]=2;codec_version[2]=3;codec_version[3]=4;}
void host_dfu_make_package(int corrupt_crc,int omit_firmware){uint32_t i,boot_off=48,boot_size=96,fw_off=144,fw_size=96;memset(package_data,0,sizeof(package_data));put32(package_data,0x4b505746u);put32(package_data+4,0x01020304u);put32(package_data+8,omit_firmware?1u:2u);put32(package_data+16,1);put32(package_data+20,boot_size);put32(package_data+24,boot_off);for(i=0;i<boot_size;i++)package_data[boot_off+i]=(uint8_t)(i+1);package_data[boot_off+2]=1;putbe32(package_data+boot_off+8,32u);putbe32(package_data+boot_off+16,32u);putbe32(package_data+boot_off+20,0x11223344u);put32(package_data+28,open_cfw_dfu_crc32(package_data+boot_off,boot_size)+(uint32_t)corrupt_crc);if(!omit_firmware){put32(package_data+32,2);put32(package_data+36,fw_size);put32(package_data+40,fw_off);for(i=0;i<fw_size;i++)package_data[fw_off+i]=(uint8_t)(0x80u+i);put32(package_data+44,open_cfw_dfu_crc32(package_data+fw_off,fw_size));}package_size=fw_off+fw_size;}
void host_dfu_set_rx(const uint8_t *data,uint32_t size){if(size>sizeof(uart_rx))size=sizeof(uart_rx);memcpy(uart_rx,data,size);uart_rx_size=size;uart_rx_position=0;}
void host_dfu_set_codec_version(uint32_t v){codec_version[0]=(uint8_t)(v>>24);codec_version[1]=(uint8_t)(v>>16);codec_version[2]=(uint8_t)(v>>8);codec_version[3]=(uint8_t)v;}
void host_dfu_set_failures(int alloc_fail,int init_fail,int baud_fail){fail_alloc=alloc_fail;fail_uart_init=init_fail;fail_uart_baud=baud_fail;}
uint32_t host_dfu_tx_size(void){return uart_tx_size;} uint32_t host_dfu_close_count(void){return close_count;} uint32_t host_dfu_reboot_true_count(void){return reboot_true_count;} uint32_t host_dfu_reboot_false_count(void){return reboot_false_count;}
void host_dfu_clear_tx(void){uart_tx_size=0;} uint32_t host_dfu_copy_tx(uint8_t *destination,uint32_t capacity){uint32_t n=uart_tx_size;if(n>capacity)n=capacity;memcpy(destination,uart_tx,n);return n;}
uintptr_t open_cfw_dfu_file_open(const char *path,const char *mode){file_position=0;return path&&mode&&strcmp(mode,"rb")==0&&strcmp(path,"/firmware/codec.bin")==0&&package_size?1u:0u;}
uint32_t open_cfw_dfu_file_read(void *data,uint32_t element_size,uint32_t element_count,uintptr_t file){uint32_t wanted=element_size*element_count,n;if(file!=1u||element_size==0u)return 0;n=package_size-file_position;if(n>wanted)n=wanted;memcpy(data,package_data+file_position,n);file_position+=n;return n/element_size;}
int32_t open_cfw_dfu_file_seek(uintptr_t file,int32_t offset,uint32_t origin){if(file!=1u||origin!=0u||offset<0||(uint32_t)offset>package_size)return -1;file_position=(uint32_t)offset;return 0;} void open_cfw_dfu_file_close(uintptr_t file){(void)file;close_count++;}
void *open_cfw_dfu_allocate(uint32_t size){return fail_alloc?0:malloc(size);} void open_cfw_dfu_free(void *p){free(p);}
int32_t open_cfw_dfu_uart_init(void){return fail_uart_init?-1:0;} int32_t open_cfw_dfu_uart_close(void){return 0;} int32_t open_cfw_dfu_uart_set_baud(uint32_t baud){return fail_uart_baud||(baud!=230400u&&baud!=1000000u)?-1:0;}
int32_t open_cfw_dfu_uart_write(const uint8_t *data,uint32_t size){if(uart_tx_size+size>sizeof(uart_tx))return -1;memcpy(uart_tx+uart_tx_size,data,size);uart_tx_size+=size;return (int32_t)size;}
int32_t open_cfw_dfu_uart_read(uint8_t *data,uint32_t size){uint32_t n=uart_rx_size-uart_rx_position;if(n>size)n=size;if(n==0)return 0;memcpy(data,uart_rx+uart_rx_position,n);uart_rx_position+=n;return (int32_t)n;}
uint64_t open_cfw_dfu_time_ms(void){return clock_ms++;} void open_cfw_dfu_delay(uint32_t ticks){clock_ms+=ticks;}
void open_cfw_dfu_codec_reboot(_Bool skip){if(skip)reboot_true_count++;else reboot_false_count++;}
int32_t open_cfw_dfu_codec_version(uint8_t *version,uint32_t timeout){(void)timeout;memcpy(version,codec_version,4);return 0;}
