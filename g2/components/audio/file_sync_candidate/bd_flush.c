/* Pinned LittleFS block-device flush, stock 0x4caafa. */
#include <stdint.h>
extern uint32_t g2_lfs_alignup(uint32_t size,uint32_t align); /* 0x4ca714 */
extern int32_t g2_lfs_bd_cmp(void *filesystem,void *pcache,void *rcache,
                             uint32_t size,uint32_t block,uint32_t off,
                             const void *buffer,uint32_t diff); /* 0x4caa04 */
extern int32_t g2_lfs_cache_drop(void *filesystem,void *cache); /* 0x4ca81a */
extern void g2_lfs_cache_zero(void *filesystem,void *cache); /* 0x4ca822 */
extern void g2_file_close_error(const char *message,const char *file,
                                 uint32_t line);

int32_t g2_lfs_bd_flush(void *filesystem,void *program_cache,
                        void *read_cache,uint32_t validate) {
    uint8_t *lfs=(uint8_t *)filesystem,*pc=(uint8_t *)program_cache;
    uint32_t block=*(uint32_t *)(void *)pc;
    if(block==UINT32_MAX || block==UINT32_MAX-1u) return 0;
    uint8_t *cfg=*(uint8_t **)(void *)(lfs+0x68u);
    if(block>=*(uint32_t *)(void *)(lfs+0x6cu))
        g2_file_close_error((const char *)(uintptr_t)0x754de8u,
                            (const char *)(uintptr_t)0x70c264u,179u);
    uint32_t diff=g2_lfs_alignup(*(uint32_t *)(void *)(pc+8u),
                                  *(uint32_t *)(void *)(cfg+0x18u));
    int32_t (*prog)(void *,uint32_t,uint32_t,const void *,uint32_t)=
        *(int32_t (**)(void *,uint32_t,uint32_t,const void *,uint32_t))
          (void *)(cfg+8u);
    int32_t err=prog(cfg,block,*(uint32_t *)(void *)(pc+4u),
                     *(const void **)(void *)(pc+12u),diff);
    if(err>=1)
        g2_file_close_error((const char *)(uintptr_t)0x78ab74u,
                            (const char *)(uintptr_t)0x70c264u,183u);
    if(err) return err;
    if((uint8_t)validate) {
        (void)g2_lfs_cache_drop(filesystem,read_cache);
        err=g2_lfs_bd_cmp(filesystem,0,read_cache,diff,block,
                           *(uint32_t *)(void *)(pc+4u),
                           *(const void **)(void *)(pc+12u),diff);
        if(err<0) return err;
        if(err!=0) return -84;
    }
    g2_lfs_cache_zero(filesystem,program_cache);
    return 0;
}
