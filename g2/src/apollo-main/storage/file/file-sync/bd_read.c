/* Pinned LittleFS block-device read/cache worker, stock 0x4ca83c. */
#include <stdint.h>
extern uint32_t g2_lfs_aligndown(uint32_t value,uint32_t align);
extern uint32_t g2_lfs_alignup(uint32_t value,uint32_t align);
extern void g2_lfs_memcpy(void *destination,const void *source,uint32_t count);
extern void g2_file_close_error(const char *message,const char *file,uint32_t line);
static uint32_t read_word(const void *base,uint32_t offset) {
    return *(const uint32_t *)((const uint8_t *)base+offset);
}
static void write_word(void *base,uint32_t offset,uint32_t value) {
    *(uint32_t *)((uint8_t *)base+offset)=value;
}
static uint32_t min_u32(uint32_t a,uint32_t b) {return a<b?a:b;}
int32_t g2_lfs_bd_read(void *filesystem,const void *program_cache,
                        void *read_cache,uint32_t hint,uint32_t block,
                        uint32_t offset,void *buffer,uint32_t size) {
    uint8_t *lfs=(uint8_t *)filesystem,*data=(uint8_t *)buffer;
    uint8_t *cfg=*(uint8_t **)(void *)(lfs+0x68u);
    uint32_t block_count=read_word(lfs,0x6cu);
    if(offset+size>read_word(cfg,0x1cu) ||
       (block_count && block>=block_count)) return -84;
    while(size) {
        uint32_t diff=size;
        if(program_cache && block==read_word(program_cache,0u) &&
           offset<read_word(program_cache,4u)+read_word(program_cache,8u)) {
            if(offset>=read_word(program_cache,4u)) {
                uint32_t displacement=offset-read_word(program_cache,4u);
                diff=min_u32(diff,read_word(program_cache,8u)-displacement);
                g2_lfs_memcpy(data,
                     (const uint8_t *)(uintptr_t)read_word(program_cache,12u)+displacement,diff);
                data+=diff;offset+=diff;size-=diff;continue;
            }
            diff=min_u32(diff,read_word(program_cache,4u)-offset);
        }
        if(block==read_word(read_cache,0u) &&
           offset<read_word(read_cache,4u)+read_word(read_cache,8u)) {
            if(offset>=read_word(read_cache,4u)) {
                uint32_t displacement=offset-read_word(read_cache,4u);
                diff=min_u32(diff,read_word(read_cache,8u)-displacement);
                g2_lfs_memcpy(data,
                     (const uint8_t *)(uintptr_t)read_word(read_cache,12u)+displacement,diff);
                data+=diff;offset+=diff;size-=diff;continue;
            }
            diff=min_u32(diff,read_word(read_cache,4u)-offset);
        }
        uint32_t read_size=read_word(cfg,0x14u);
        int32_t (*read_callback)(void *,uint32_t,uint32_t,void *,uint32_t)=
            *(int32_t (**)(void *,uint32_t,uint32_t,void *,uint32_t))(void *)(cfg+4u);
        if(size>=hint && offset%read_size==0u && size>=read_size) {
            diff=g2_lfs_aligndown(diff,read_size);
            int32_t err=read_callback(cfg,block,offset,data,diff);
            if(err) return err;
            data+=diff;offset+=diff;size-=diff;continue;
        }
        if(block_count && block>=block_count)
            g2_file_close_error((const char *)(uintptr_t)0x734874u,
                                (const char *)(uintptr_t)0x70c264u,107u);
        write_word(read_cache,0u,block);
        write_word(read_cache,4u,g2_lfs_aligndown(offset,read_size));
        uint32_t cache_off=read_word(read_cache,4u);
        uint32_t length=min_u32(g2_lfs_alignup(offset+hint,read_size),
                                read_word(cfg,0x1cu))-cache_off;
        write_word(read_cache,8u,min_u32(length,read_word(cfg,0x28u)));
        int32_t err=read_callback(cfg,block,cache_off,
                   (void *)(uintptr_t)read_word(read_cache,12u),
                   read_word(read_cache,8u));
        if(err>=1)
            g2_file_close_error((const char *)(uintptr_t)0x78ab74u,
                                (const char *)(uintptr_t)0x70c264u,118u);
        if(err) return err;
    }
    return 0;
}
