/* Pinned LittleFS reverse metadata lookup, stock 0x4cb23a. */
#include <stdint.h>
extern int32_t g2_lfs_gstate_hasmovehere(void *state,const void *pair);
extern int32_t g2_lfs_bd_read(void *filesystem,const void *program_cache,
                               void *read_cache,uint32_t hint,uint32_t block,
                               uint32_t offset,void *buffer,uint32_t size);
extern void g2_lfs_cache_fill(void *buffer,uint32_t length,uint32_t value);
static uint32_t tag_id(uint32_t tag) {return (tag>>10u)&0x3ffu;}
static uint32_t tag_type1(uint32_t tag) {return (tag&0x70000000u)>>20u;}
static uint32_t tag_size(uint32_t tag) {return tag&0x3ffu;}
static uint32_t tag_isdelete(uint32_t tag) {return tag_size(tag)==0x3ffu;}
static uint32_t tag_dsize(uint32_t tag) {
    return 4u+tag_size(tag+tag_isdelete(tag));
}
static uint32_t min_u32(uint32_t a,uint32_t b) {return a<b?a:b;}
int32_t g2_lfs_dir_getslice(void *filesystem,void *directory,
                             uint32_t mask,uint32_t wanted,uint32_t slice,
                             void *buffer,uint32_t size) {
    uint8_t *fs=(uint8_t *)filesystem,*dir=(uint8_t *)directory;
    uint32_t off=*(uint32_t *)(void *)(dir+12u);
    uint32_t next_tag=*(uint32_t *)(void *)(dir+16u);
    uint32_t adjustment=0;
    if(g2_lfs_gstate_hasmovehere(fs+0x3cu,dir)!=0 && tag_id(mask)!=0u) {
        uint32_t state_tag=*(uint32_t *)(void *)(fs+0x3cu);
        if(tag_id(state_tag)==tag_id(wanted)) return -2;
        if(tag_id(state_tag)<tag_id(wanted)) adjustment-=0x400u;
    }
    while(off>=4u+tag_dsize(next_tag)) {
        off-=tag_dsize(next_tag);
        uint32_t tag=next_tag;
        int32_t err=g2_lfs_bd_read(filesystem,0,filesystem,4u,
                      *(uint32_t *)(void *)dir,off,&next_tag,4u);
        if(err) return err;
        next_tag=(__builtin_bswap32(next_tag)^tag)&0x7fffffffu;
        if(tag_id(mask)!=0u && tag_type1(tag)==0x400u &&
           tag_id(tag)<=tag_id(wanted-adjustment)) {
            if(tag==(0x40100000u|((wanted-adjustment)&0xffc00u)))
                return -2;
            adjustment+=(uint32_t)((int32_t)(int8_t)((tag>>20u)&0xffu)<<10u);
        }
        if((mask&tag)==(mask&(wanted-adjustment))) {
            if(tag_isdelete(tag)) return -2;
            uint32_t diff=min_u32(tag_size(tag),size);
            err=g2_lfs_bd_read(filesystem,0,filesystem,diff,
                                *(uint32_t *)(void *)dir,off+4u+slice,
                                buffer,diff);
            if(err) return err;
            g2_lfs_cache_fill((uint8_t *)buffer+diff,size-diff,0u);
            return (int32_t)(tag+adjustment);
        }
    }
    return -2;
}
