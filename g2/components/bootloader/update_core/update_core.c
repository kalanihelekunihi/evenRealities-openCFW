/* SPDX-License-Identifier: MIT
 * Portable reconstruction of locked s200_v2.2.6.10 bootloader update core.
 * Raw stock behavior is retained. Input hardening must be a separate policy.
 */
#include "update_core.h"
#define WORD(at) (*(volatile uint32_t *)(uintptr_t)(at))
#define STORAGE (*(opencfw_boot_storage * volatile *)(uintptr_t)0x200004f0u)
#define CRC_BUFFER ((void *)(uintptr_t)0x2001fdf0u)
#define PROGRAM_BUFFER ((void *)(uintptr_t)0x2001ede0u)
#define PATH 0x4336e4u
#define TAG 0x433fe0u
#define FILE_NAME 0x4310c4u
#define LOG(fn,line,format,...) opencfw_boot_log(4,TAG,FILE_NAME,fn,line,format,##__VA_ARGS__)
#define ERROR(fn,line,format,...) opencfw_boot_log(1,TAG,FILE_NAME,fn,line,format,##__VA_ARGS__)
_Static_assert(sizeof(opencfw_boot_image_header)==32,"header layout");
#if UINTPTR_MAX == UINT32_MAX
_Static_assert(offsetof(opencfw_boot_storage,read)==0x18,"read callback");
_Static_assert(offsetof(opencfw_boot_storage,program)==0x1c,"program callback");
_Static_assert(offsetof(opencfw_boot_storage,erase)==0x20,"erase callback");
#endif
uint32_t opencfw_boot_crc32(const void *data, uint32_t size, const uint32_t *previous) {
    const uint8_t *bytes=data;
    uint32_t crc=previous ? ~*previous : UINT32_MAX;
    for(uint32_t n=0;n<size;n++) {
        crc^=bytes[n];
        for(unsigned bit=0;bit<8;bit++) crc=(crc>>1)^(0xedb88320u & (0u-(crc&1u)));
    }
    return ~crc;
}
uintptr_t opencfw_boot_stream_mode(uint32_t flags) {
    if(flags&3u) return (flags&0x100u) ? ((flags&0x400u)?0x42dad0u:0x42dad4u):0x42dad8u;
    if(!(flags&2u)) return 0x42dae4u;
    if(flags&0x800u) return 0x42dadcu;
    return (flags&0x100u) ? ((flags&0x400u)?0x42dae0u:0x42dadcu):0x42dae0u;
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
int32_t opencfw_boot_compare(uint32_t address,const void *source,uint32_t size,
                            const opencfw_boot_storage *descriptor) {
    uint32_t offset=0,remaining=size;
    opencfw_boot_runtime_call(0,1);
    while(remaining) {
        uint32_t chunk=remaining>0x1000u?0x1000u:remaining;
        descriptor->read(CRC_BUFFER,address+offset,chunk);
        int32_t result=opencfw_boot_memcmp(CRC_BUFFER,(const uint8_t *)source+offset,chunk);
        if(result) { ERROR(0x433c04u,0x10bu,0x4320acu,address,size); return result; }
        LOG(0x433c04u,0x10eu,0x43184cu,address,size,remaining);
        offset+=chunk;remaining-=chunk;
    }
    return 0;
}
uint32_t opencfw_boot_verify(uint32_t *handle,const opencfw_boot_image_header *header) {
    uint32_t length=(header->encoded_size&0xffffffu)-8u,crc=0;
    *handle=opencfw_boot_file_open(PATH,opencfw_boot_stream_mode(1));
    if(!*handle) { ERROR(0x4339acu,0xcfu,0x433bdcu,PATH);return 0; }
    opencfw_boot_file_prepare(*handle,8,0);
    for(uint32_t i=0;i<length/STORAGE->chunk_size;i++) {
        uint32_t amount=STORAGE->chunk_size;
        uint32_t got=opencfw_boot_file_read(CRC_BUFFER,1,amount,*handle);
        if(got!=STORAGE->chunk_size) ERROR(0x4339acu,0xd7u,0x433e78u,got);
        crc=opencfw_boot_crc32(CRC_BUFFER,STORAGE->chunk_size,&crc);
    }
    uint32_t tail=length-STORAGE->chunk_size*(length/STORAGE->chunk_size);
    if(tail) {
        uint32_t got=opencfw_boot_file_read(CRC_BUFFER,1,tail,*handle);
        if(got!=tail) ERROR(0x4339acu,0xdfu,0x433bf0u,got,tail);
        crc=opencfw_boot_crc32(CRC_BUFFER,tail,&crc);
    }
    if(*handle) { opencfw_boot_file_close(*handle);*handle=0; }
    LOG(0x4339acu,0xe4u,0x4339c4u,crc,WORD(0x20026efcu));
    return crc==header->expected_crc;
}
void opencfw_boot_program(uint32_t *handle,const opencfw_boot_image_header *header) {
    uint32_t remaining=(header->encoded_size&0xffffffu)-32u,address=header->destination;
    opencfw_boot_erase_visit(address,remaining);
    LOG(0x4339dcu,0x120u,0x433700u,remaining,address);
    *handle=opencfw_boot_file_open(PATH,opencfw_boot_stream_mode(1));
    if(!*handle) { ERROR(0x4339dcu,0x123u,0x433bdcu,PATH);return; }
    opencfw_boot_file_prepare(*handle,32,0);
    LOG(0x4339dcu,0x128u,0x433e88u,remaining,address);
    while(remaining) {
        uint32_t percent=100u-(remaining*100u)/(header->encoded_size&0xffffffu);
        LOG(0x4339dcu,0x12cu,0x433c18u,remaining,percent);
        uint32_t chunk=remaining<STORAGE->chunk_size?remaining:STORAGE->chunk_size;
        uint32_t got=opencfw_boot_file_read(PROGRAM_BUFFER,1,chunk,*handle);
        if(got!=chunk) ERROR(0x4339dcu,0x131u,0x433bf0u,got,chunk);
        STORAGE->program(address,PROGRAM_BUFFER,STORAGE->chunk_size);
        if(opencfw_boot_compare(address,PROGRAM_BUFFER,chunk,STORAGE))
            ERROR(0x4339dcu,0x136u,0x4320acu,address,chunk);
        address+=chunk;remaining-=chunk;
    }
    if(*handle) { opencfw_boot_file_close(*handle);*handle=0; }
    /* R13/R8 are incidental saved values in the final variadic stock log;
     * only its fixed semantic payload and line are reconstructed here. */
    LOG(0x4339dcu,0x13cu,0x433c2cu);
}
