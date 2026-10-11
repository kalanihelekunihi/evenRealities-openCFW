/* Pinned LittleFS orphan/relocation commit state machine, stock 0x4ccf7c. */
#include <stdint.h>
#include <stddef.h>
typedef struct {uint32_t pair[2],rev,off,etag;uint16_t count;uint8_t erased,split;uint32_t tail[2];} g2_mdir;
struct g2_lfs_attr {uint32_t tag;const void *buffer;};
_Static_assert(sizeof(g2_mdir)==32,"stock LittleFS metadata layout");
extern int32_t g2_lfs_file_outline(void *,void *);
extern int32_t g2_lfs_file_flush(void *,void *);
extern int32_t g2_lfs_dir_relocatingcommit(void *,void *,const uint32_t *,
                                           const struct g2_lfs_attr *,uint32_t,void *);
extern int32_t g2_lfs_dir_getgstate(void *,const void *,void *);
extern int32_t g2_lfs_fs_parent(void *,const uint32_t *,void *);
extern int32_t g2_lfs_fs_pred(void *,const uint32_t *,void *);
extern int32_t g2_lfs_fs_preporphans(void *,int8_t);
extern int32_t g2_lfs_gstate_hasmovehere(void *,const void *);
extern void g2_lfs_fs_prepmove(void *,uint32_t,const uint32_t *);
extern int32_t g2_log_transport_queue_failure(const char *,...);
extern void g2_file_close_error(const char *,const char *,uint32_t);
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\littlefs\\lfs.c";
static const char relocating_log[]="%s:%d:debug: Relocating {0x%x, 0x%x} -> {0x%x, 0x%x}%s\n";
static const char fixing_move_log[]="%s:%d:debug: Fixing move while relocating {0x%x, 0x%x} 0x%hx\n%s\n";
static const char pred_assert[]="!(hasparent && err == LFS_ERR_NOENT)";
static uint32_t *word(void *p,uint32_t off) {return (uint32_t *)((uint8_t *)p+off);}
static int32_t pair_cmp(const uint32_t *a,const uint32_t *b) {
    return !(a[0]==b[0] || a[1]==b[1] || a[0]==b[1] || a[1]==b[0]);
}
int32_t g2_lfs_dir_orphaningcommit(void *filesystem,void *directory,
                                    const struct g2_lfs_attr *attrs,uint32_t count) {
    uint8_t *fs=(uint8_t *)filesystem;
    g2_mdir *dir=(g2_mdir *)directory;
    uint8_t *cfg=(uint8_t *)(uintptr_t)*word(fs,0x68u);
    for(uint8_t *f=(uint8_t *)(uintptr_t)*word(fs,0x28u);
        f;f=(uint8_t *)(uintptr_t)*word(f,0u)) {
        if(dir!=(g2_mdir *)(f+8u) && pair_cmp((uint32_t *)(void *)(f+8u),dir->pair)==0 &&
           f[6]==1u && (*word(f,0x30u)&0x100000u) &&
           *word(f,0x2cu)>*word(cfg,0x28u)) {
            int32_t err=g2_lfs_file_outline(fs,f);
            if(err) return err;
            err=g2_lfs_file_flush(fs,f);
            if(err) return err;
        }
    }
    uint32_t lpair[2]={dir->pair[0],dir->pair[1]};
    g2_mdir ldir=*dir,pdir;
    int32_t state=g2_lfs_dir_relocatingcommit(fs,&ldir,dir->pair,attrs,count,&pdir);
    if(state<0) return state;
    if(pair_cmp(dir->pair,lpair)==0) *dir=ldir;
    if(state==2) {
        int32_t err=g2_lfs_dir_getgstate(fs,dir,fs+0x48u);
        if(err) return err;
        lpair[0]=pdir.pair[0];lpair[1]=pdir.pair[1];
        struct g2_lfs_attr tail={
            ((0x600u+dir->split)<<20u)|(0x3ffu<<10u)|8u,dir->tail};
        state=g2_lfs_dir_relocatingcommit(fs,&pdir,lpair,&tail,1u,NULL);
        if(state<0) return state;
        ldir=pdir;
    }
    uint32_t orphans=0u;
    while(state==1) {
        g2_log_transport_queue_failure(relocating_log,path,2477,
              lpair[0],lpair[1],ldir.pair[0],ldir.pair[1],"");
        state=0;
        if(pair_cmp(lpair,(uint32_t *)(void *)(fs+0x20u))==0) {
            *word(fs,0x20u)=ldir.pair[0];*word(fs,0x24u)=ldir.pair[1];
        }
        for(uint8_t *m=(uint8_t *)(uintptr_t)*word(fs,0x28u);
            m;m=(uint8_t *)(uintptr_t)*word(m,0u)) {
            if(pair_cmp(lpair,(uint32_t *)(void *)(m+8u))==0) {
                *word(m,8u)=ldir.pair[0];*word(m,12u)=ldir.pair[1];
            }
            if(m[6]==2u && pair_cmp(lpair,(uint32_t *)(void *)(m+0x2cu))==0) {
                *word(m,0x2cu)=ldir.pair[0];*word(m,0x30u)=ldir.pair[1];
            }
        }
        int32_t tag=g2_lfs_fs_parent(fs,lpair,&pdir);
        if(tag<0 && tag!=-2) return tag;
        uint32_t hasparent=tag!=-2;
        if(hasparent) {
            int32_t err=g2_lfs_fs_preporphans(fs,1);
            if(err) return err;
            uint32_t moveid=0x3ffu;
            uint32_t *gstate=word(fs,0x30u);
            if(g2_lfs_gstate_hasmovehere(gstate,pdir.pair)) {
                moveid=(gstate[0]>>10u)&0x3ffu;
                g2_log_transport_queue_failure(fixing_move_log,path,2522,
                      pdir.pair[0],pdir.pair[1],moveid,"");
                g2_lfs_fs_prepmove(fs,0x3ffu,NULL);
                if(moveid<(((uint32_t)tag>>10u)&0x3ffu)) tag-=0x400;
            }
            uint32_t ppair[2]={pdir.pair[0],pdir.pair[1]};
            struct g2_lfs_attr parent_attrs[2]={
                {moveid==0x3ffu ? 0u : (0x4ffu<<20u)|(moveid<<10u),NULL},
                {(uint32_t)tag,ldir.pair}
            };
            state=g2_lfs_dir_relocatingcommit(fs,&pdir,ppair,parent_attrs,2u,NULL);
            if(state<0) return state;
            if(state==1) {
                lpair[0]=ppair[0];lpair[1]=ppair[1];
                ldir=pdir;orphans=1u;continue;
            }
        }
        int32_t err=g2_lfs_fs_pred(fs,lpair,&pdir);
        if(err && err!=-2) return err;
        if(hasparent && err==-2) g2_file_close_error(pred_assert,path,2555u);
        if(err!=-2) {
            if((*word(fs,0x30u)&0x3ffu)!=0u) {
                err=g2_lfs_fs_preporphans(fs,(int8_t)-(int32_t)hasparent);
                if(err) return err;
            }
            uint32_t moveid=0x3ffu;
            uint32_t *gstate=word(fs,0x30u);
            if(g2_lfs_gstate_hasmovehere(gstate,pdir.pair)) {
                moveid=(gstate[0]>>10u)&0x3ffu;
                g2_log_transport_queue_failure(fixing_move_log,path,2574,
                      pdir.pair[0],pdir.pair[1],moveid,"");
                g2_lfs_fs_prepmove(fs,0x3ffu,NULL);
            }
            lpair[0]=pdir.pair[0];lpair[1]=pdir.pair[1];
            struct g2_lfs_attr pred_attrs[2]={
                {moveid==0x3ffu ? 0u : (0x4ffu<<20u)|(moveid<<10u),NULL},
                {((0x600u+pdir.split)<<20u)|(0x3ffu<<10u)|8u,ldir.pair}
            };
            state=g2_lfs_dir_relocatingcommit(fs,&pdir,lpair,pred_attrs,2u,NULL);
            if(state<0) return state;
            ldir=pdir;
        }
    }
    return orphans ? 3 : 0;
}
