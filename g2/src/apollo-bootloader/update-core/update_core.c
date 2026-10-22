/* SPDX-License-Identifier: MIT
 * Portable reconstruction of locked s200_v2.2.6.10 bootloader update core.
 * Raw stock behavior is retained. Input hardening must be a separate policy.
 */
#include "update_core.h"
#define WORD(at) (*(volatile uint32_t *)(uintptr_t)(at))
#define STORAGE (*(opencfw_boot_storage * volatile *)(uintptr_t)0x200004f0u)
#define CRC_BUFFER ((void *)(uintptr_t)0x2001fdf0u)
#define PROGRAM_BUFFER ((void *)(uintptr_t)0x2001ede0u)
extern const char opencfw_update_path_4336e4[];
extern const char opencfw_update_log_literal_4310c4[];
extern const char opencfw_update_log_literal_43184c[];
extern const char opencfw_update_log_literal_4320ac[];
extern const char opencfw_update_log_literal_433700[];
extern const char opencfw_update_log_literal_4339ac[];
extern const char opencfw_update_log_literal_4339c4[];
extern const char opencfw_update_log_literal_4339dc[];
extern const char opencfw_update_log_literal_433bdc[];
extern const char opencfw_update_log_literal_433bf0[];
extern const char opencfw_update_log_literal_433c04[];
extern const char opencfw_update_log_literal_433c18[];
extern const char opencfw_update_log_literal_433c2c[];
extern const char opencfw_update_log_literal_433e78[];
extern const char opencfw_update_log_literal_433e88[];
extern const char opencfw_update_log_literal_433fe0[];
#define PATH ((uintptr_t)opencfw_update_path_4336e4)
#define TAG ((uintptr_t)opencfw_update_log_literal_433fe0)
#define FILE_NAME ((uintptr_t)opencfw_update_log_literal_4310c4)
#define LOG(fn,line,format,...) opencfw_boot_log(4,TAG,FILE_NAME,fn,line,format,##__VA_ARGS__)
#define ERROR(fn,line,format,...) opencfw_boot_log(1,TAG,FILE_NAME,fn,line,format,##__VA_ARGS__)
_Static_assert(sizeof(opencfw_boot_image_header)==32,"header layout");
#if UINTPTR_MAX == UINT32_MAX
_Static_assert(offsetof(opencfw_boot_storage,read)==0x18,"read callback");
_Static_assert(offsetof(opencfw_boot_storage,program)==0x1c,"program callback");
_Static_assert(offsetof(opencfw_boot_storage,erase)==0x20,"erase callback");
#endif
/* Stock 0x42e1ec (crc32_table_42e1ec) */
uint32_t opencfw_boot_crc32(const void *data, uint32_t size, const uint32_t *previous) {
    const uint8_t *bytes=data;
    uint32_t crc=previous ? ~*previous : UINT32_MAX;
    for(uint32_t n=0;n<size;n++) {
        crc^=bytes[n];
        for(unsigned bit=0;bit<8;bit++) crc=(crc>>1)^(0xedb88320u & (0u-(crc&1u)));
    }
    return ~crc;
}
/* Stock 0x42d84c (stream_mode_42d84c) */
uintptr_t opencfw_boot_stream_mode(uint32_t flags) {
    static const char mode_write_plus[] = "w+";
    static const char mode_append_plus[] = "a+";
    static const char mode_read_plus[] = "r+";
    static const char mode_append[] = "a";
    static const char mode_write[] = "w";
    static const char mode_read[] = "r";
    if(flags&3u) return (uintptr_t)((flags&0x100u) ?
        ((flags&0x400u)?mode_write_plus:mode_append_plus):mode_read_plus);
    if(!(flags&2u)) return (uintptr_t)mode_read;
    if(flags&0x800u) return (uintptr_t)mode_append;
    return (uintptr_t)((flags&0x100u) ?
        ((flags&0x400u)?mode_write:mode_append):mode_write);
}
int32_t opencfw_boot_memcmp(const void *a,const void *b,uint32_t size) {
    const uint8_t *left=a,*right=b;
    while(((uintptr_t)left&3u) && size) {
        int32_t diff=(int32_t)*left++-(int32_t)*right++;
        --size; if(diff) return diff;
    }
    if(!((uintptr_t)right&3u)) {
        while(size>=4) {
            uint32_t x=*(const uint32_t *)left,y=*(const uint32_t *)right;
            if(x!=y) {
                x=__builtin_bswap32(x); y=__builtin_bswap32(y);
                return x<y?-1:1;
            }
            left+=4;right+=4;size-=4;
        }
    }
    while(size--) { int32_t diff=(int32_t)*left++-(int32_t)*right++; if(diff)return diff; }
    return 0;
}
/* Stock 0x42d9f0 (chunked_indirect_visit_42d9f0) */
void opencfw_boot_erase_visit(uint32_t address,uint32_t size) {
    while(size) {
        opencfw_boot_storage *descriptor=STORAGE;
        descriptor->erase(address);
        uint32_t chunk=STORAGE->chunk_size;
        if(chunk>=size) return;
        size-=STORAGE->chunk_size;
        address+=STORAGE->chunk_size;
    }
}
/* Stock 0x42da1e (chunked_source_compare_42da1e) */
int32_t opencfw_boot_compare(uint32_t address,const void *source,uint32_t size,
                            const opencfw_boot_storage *descriptor) {
    uint32_t offset=0,remaining=size;
    opencfw_boot_runtime_call(0,1);
    while(remaining) {
        uint32_t chunk=remaining>0x1000u?0x1000u:remaining;
        descriptor->read(CRC_BUFFER,address+offset,chunk);
        int32_t result=opencfw_boot_memcmp(CRC_BUFFER,(const uint8_t *)source+offset,chunk);
        if(result) { ERROR(((uintptr_t)opencfw_update_log_literal_433c04),0x10bu,((uintptr_t)opencfw_update_log_literal_4320ac),address,size); return result; }
        LOG(((uintptr_t)opencfw_update_log_literal_433c04),0x10eu,((uintptr_t)opencfw_update_log_literal_43184c),address,size,remaining);
        offset+=chunk;remaining-=chunk;
    }
    return 0;
}
/* Stock 0x42d890 (dfu_image_crc_check_42d890) */
uint32_t opencfw_boot_verify(uint32_t *handle,const opencfw_boot_image_header *header) {
    uint32_t length=(header->encoded_size&0xffffffu)-8u,crc=0;
    *handle=opencfw_boot_file_open(PATH,opencfw_boot_stream_mode(1));
    if(!*handle) { ERROR(((uintptr_t)opencfw_update_log_literal_4339ac),0xcfu,((uintptr_t)opencfw_update_log_literal_433bdc),PATH);return 0; }
    opencfw_boot_file_prepare(*handle,8,0);
    for(uint32_t i=0;i<length/STORAGE->chunk_size;i++) {
        uint32_t amount=STORAGE->chunk_size;
        uint32_t got=opencfw_boot_file_read(CRC_BUFFER,1,amount,*handle);
        if(got!=STORAGE->chunk_size) ERROR(((uintptr_t)opencfw_update_log_literal_4339ac),0xd7u,((uintptr_t)opencfw_update_log_literal_433e78),got);
        crc=opencfw_boot_crc32(CRC_BUFFER,STORAGE->chunk_size,&crc);
    }
    uint32_t tail=length-STORAGE->chunk_size*(length/STORAGE->chunk_size);
    if(tail) {
        uint32_t got=opencfw_boot_file_read(CRC_BUFFER,1,tail,*handle);
        if(got!=tail) ERROR(((uintptr_t)opencfw_update_log_literal_4339ac),0xdfu,((uintptr_t)opencfw_update_log_literal_433bf0),got,tail);
        crc=opencfw_boot_crc32(CRC_BUFFER,tail,&crc);
    }
    if(*handle) { opencfw_boot_file_close(*handle);*handle=0; }
    LOG(((uintptr_t)opencfw_update_log_literal_4339ac),0xe4u,((uintptr_t)opencfw_update_log_literal_4339c4),crc,WORD(0x20026efcu));
    return crc==header->expected_crc;
}
/* Stock 0x42dae8 (dfu_payload_program_42dae8) */
void opencfw_boot_program(uint32_t *handle,const opencfw_boot_image_header *header) {
    uint32_t remaining=(header->encoded_size&0xffffffu)-32u,address=header->destination;
    opencfw_boot_erase_visit(address,remaining);
    LOG(((uintptr_t)opencfw_update_log_literal_4339dc),0x120u,((uintptr_t)opencfw_update_log_literal_433700),remaining,address);
    *handle=opencfw_boot_file_open(PATH,opencfw_boot_stream_mode(1));
    if(!*handle) { ERROR(((uintptr_t)opencfw_update_log_literal_4339dc),0x123u,((uintptr_t)opencfw_update_log_literal_433bdc),PATH);return; }
    opencfw_boot_file_prepare(*handle,32,0);
    LOG(((uintptr_t)opencfw_update_log_literal_4339dc),0x128u,((uintptr_t)opencfw_update_log_literal_433e88),remaining,address);
    while(remaining) {
        uint32_t percent=100u-(remaining*100u)/(header->encoded_size&0xffffffu);
        LOG(((uintptr_t)opencfw_update_log_literal_4339dc),0x12cu,((uintptr_t)opencfw_update_log_literal_433c18),remaining,percent);
        uint32_t chunk=remaining<STORAGE->chunk_size?remaining:STORAGE->chunk_size;
        uint32_t got=opencfw_boot_file_read(PROGRAM_BUFFER,1,chunk,*handle);
        if(got!=chunk) ERROR(((uintptr_t)opencfw_update_log_literal_4339dc),0x131u,((uintptr_t)opencfw_update_log_literal_433bf0),got,chunk);
        STORAGE->program(address,PROGRAM_BUFFER,STORAGE->chunk_size);
        if(opencfw_boot_compare(address,PROGRAM_BUFFER,chunk,STORAGE))
            ERROR(((uintptr_t)opencfw_update_log_literal_4339dc),0x136u,((uintptr_t)opencfw_update_log_literal_4320ac),address,chunk);
        address+=chunk;remaining-=chunk;
    }
    if(*handle) { opencfw_boot_file_close(*handle);*handle=0; }
    /* R13/R8 are incidental saved values in the final variadic stock log;
     * only its fixed semantic payload and line are reconstructed here. */
    LOG(((uintptr_t)opencfw_update_log_literal_4339dc),0x13cu,((uintptr_t)opencfw_update_log_literal_433c2c));
}
