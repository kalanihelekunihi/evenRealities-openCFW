/* Pinned LittleFS CTZ extension and corrupt-block retry, stock 0x4cd7d2. */
#include <stdint.h>
extern int32_t g2_lfs_alloc(void *filesystem,uint32_t *block);
extern int32_t g2_lfs_bd_erase(void *filesystem,uint32_t block);
extern uint32_t g2_lfs_ctz_index(void *filesystem,uint32_t *offset);
extern int32_t g2_lfs_bd_read(void *filesystem,const void *program_cache,
                               void *read_cache,uint32_t hint,uint32_t block,
                               uint32_t offset,void *buffer,uint32_t size);
extern int32_t g2_lfs_bd_program(void *filesystem,void *program_cache,
                                  void *read_cache,uint32_t validate,
                                  uint32_t block,uint32_t offset,
                                  const void *buffer,uint32_t size);
extern int32_t g2_lfs_cache_drop(void *filesystem,void *cache);
extern void g2_lfs_debug_bad_block(uint32_t block,uint32_t line);
static uint32_t trailing_zeroes(uint32_t value) {
    uint32_t count=0;
    while((value&1u)==0u) {++count;value>>=1u;}
    return count;
}
int32_t g2_lfs_ctz_extend(void *filesystem,void *program_cache,
                           void *read_cache,uint32_t head,uint32_t size,
                           uint32_t *block,uint32_t *offset) {
    uint8_t *cfg=*(uint8_t **)((uint8_t *)filesystem+0x68u);
    uint32_t block_size=*(uint32_t *)(void *)(cfg+0x1cu);
    for(;;) {
        uint32_t new_block;
        int32_t err=g2_lfs_alloc(filesystem,&new_block);
        if(err) return err;
        err=g2_lfs_bd_erase(filesystem,new_block);
        if(err) {
            if(err==-84) goto relocate;
            return err;
        }
        if(size==0u) {*block=new_block;*offset=0;return 0;}
        uint32_t noff=size-1u;
        uint32_t index=g2_lfs_ctz_index(filesystem,&noff);
        ++noff;
        if(noff!=block_size) {
            for(uint32_t i=0;i<noff;i++) {
                uint8_t data;
                err=g2_lfs_bd_read(filesystem,0,read_cache,noff-i,
                                    head,i,&data,1u);
                if(err) return err;
                err=g2_lfs_bd_program(filesystem,program_cache,read_cache,
                                       1u,new_block,i,&data,1u);
                if(err) {
                    if(err==-84) goto relocate;
                    return err;
                }
            }
            *block=new_block;*offset=noff;return 0;
        }
        ++index;
        uint32_t skips=trailing_zeroes(index)+1u;
        uint32_t next_head=head;
        for(uint32_t i=0;i<skips;i++) {
            err=g2_lfs_bd_program(filesystem,program_cache,read_cache,
                                   1u,new_block,4u*i,&next_head,4u);
            if(err) {
                if(err==-84) goto relocate;
                return err;
            }
            if(i!=skips-1u) {
                err=g2_lfs_bd_read(filesystem,0,read_cache,4u,
                                    next_head,4u*i,&next_head,4u);
                if(err) return err;
            }
        }
        *block=new_block;*offset=4u*skips;return 0;
relocate:
        g2_lfs_debug_bad_block(new_block,3013u);
        (void)g2_lfs_cache_drop(filesystem,program_cache);
    }
}
