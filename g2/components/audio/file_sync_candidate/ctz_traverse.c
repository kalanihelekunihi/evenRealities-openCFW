/* Pinned LittleFS CTZ block visitor, stock 0x4cd974. */
#include <stdint.h>
typedef int32_t (*g2_lfs_visit)(void *,uint32_t);
extern uint32_t g2_lfs_ctz_index(void *,uint32_t *);
extern int32_t g2_lfs_bd_read(void *,const void *,void *,uint32_t,uint32_t,
                               uint32_t,void *,uint32_t);
int32_t g2_lfs_ctz_traverse(void *filesystem,const void *program_cache,
                             void *read_cache,uint32_t head,uint32_t size,
                             g2_lfs_visit visit,void *context) {
    if(size==0u) return 0;
    uint32_t end=size-1u;
    uint32_t index=g2_lfs_ctz_index(filesystem,&end);
    for(;;) {
        int32_t err=visit(context,head);
        if(err) return err;
        if(index==0u) return 0;
        uint32_t heads[2];
        uint32_t count=2u-(index&1u);
        err=g2_lfs_bd_read(filesystem,program_cache,read_cache,
                            count*4u,head,0u,heads,count*4u);
        if(err) return err;
        for(uint32_t i=0;i<count-1u;i++) {
            err=visit(context,heads[i]);
            if(err) return err;
        }
        head=heads[count-1u];
        index-=count;
    }
}
