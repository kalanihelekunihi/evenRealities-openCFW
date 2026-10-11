/* Pinned LittleFS filesystem traversal, stock 0x4cf284. */
#include <stdint.h>
#include <stddef.h>
typedef int32_t (*g2_lfs_visit)(void *,uint32_t);
extern int32_t g2_lfs_dir_fetch(void *,void *,const uint32_t *);
extern int32_t g2_lfs_tortoise_detectcycles(void *,void *);
extern int32_t g2_lfs_dir_getslice(void *,void *,uint32_t,uint32_t,uint32_t,void *,uint32_t);
extern int32_t g2_lfs_ctz_traverse(void *,void *,void *,uint32_t,uint32_t,
                                    g2_lfs_visit,void *);
static uint32_t *word(void *p,uint32_t off) {return (uint32_t *)((uint8_t *)p+off);}
static int32_t pair_null(const uint32_t *pair) {
    return pair[0]==UINT32_MAX || pair[1]==UINT32_MAX;
}
int32_t g2_lfs_fs_traverse(void *filesystem,g2_lfs_visit visit,
                            void *context,uint32_t include_orphans) {
    uint32_t dir[8]={0u,0u,0u,0u,0u,0u,0u,1u};
    uint32_t tortoise[4]={UINT32_MAX,UINT32_MAX,1u,1u};
    while(!pair_null(dir+6)) {
        if(g2_lfs_tortoise_detectcycles(dir,tortoise)<0) return -84;
        for(uint32_t i=0;i<2u;i++) {
            int32_t err=visit(context,dir[6u+i]);
            if(err) return err;
        }
        int32_t err=g2_lfs_dir_fetch(filesystem,dir,dir+6);
        if(err) return err;
        uint16_t count=*(uint16_t *)(void *)((uint8_t *)dir+20u);
        for(uint32_t id=0;id<count;id++) {
            uint32_t ctz[2];
            uint32_t tag=0x20000008u|(id<<10u);
            int32_t result=g2_lfs_dir_getslice(filesystem,dir,0x700ffc00u,
                                                 tag,0u,ctz,8u);
            if(result<0) {
                if(result==-2) continue;
                return result;
            }
            /* Cortex-M target is little endian: lfs_fromle32 is identity. */
            uint32_t type=((uint32_t)result>>20u)&0x7ffu;
            if(type==0x202u) {
                err=g2_lfs_ctz_traverse(filesystem,NULL,filesystem,
                                        ctz[0],ctz[1],visit,context);
                if(err) return err;
            } else if(include_orphans && type==0x200u) {
                for(uint32_t i=0;i<2u;i++) {
                    err=visit(context,ctz[i]);
                    if(err) return err;
                }
            }
        }
    }
    for(uint8_t *file=(uint8_t *)(uintptr_t)*word(filesystem,0x28u);
        file;file=(uint8_t *)(uintptr_t)*word(file,0u)) {
        if(file[6]!=1u) continue;
        uint32_t flags=*word(file,0x30u);
        if((flags&0x110000u)==0x10000u) {
            int32_t err=g2_lfs_ctz_traverse(filesystem,file+0x40u,filesystem,
                                              *word(file,0x28u),*word(file,0x2cu),
                                              visit,context);
            if(err) return err;
        }
        if((flags&0x120000u)==0x20000u) {
            int32_t err=g2_lfs_ctz_traverse(filesystem,file+0x40u,filesystem,
                                              *word(file,0x38u),*word(file,0x34u),
                                              visit,context);
            if(err) return err;
        }
    }
    return 0;
}
