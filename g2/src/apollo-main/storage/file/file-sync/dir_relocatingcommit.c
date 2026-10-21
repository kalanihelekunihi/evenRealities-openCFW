/* Pinned LittleFS relocation commit coordinator, stock 0x4ccb80. */
#include <stdint.h>
#include <stddef.h>
typedef struct {uint32_t pair[2],rev,off,etag;uint16_t count;uint8_t erased,split;uint32_t tail[2];} g2_mdir;
struct g2_lfs_attr {uint32_t tag;const void *buffer;};
typedef struct {uint32_t block,off,ptag,crc,begin,end;} g2_commit;
typedef int32_t (*g2_tag_visit)(void *,uint32_t,const void *);
_Static_assert(sizeof(g2_mdir)==32,"stock LittleFS metadata layout");
extern int32_t g2_lfs_fs_pred(void *,const uint32_t *,void *);
extern int32_t g2_lfs_dir_traverse(void *,void *,uint32_t,uint32_t,
             const struct g2_lfs_attr *,uint32_t,uint32_t,uint32_t,
             uint32_t,uint32_t,int32_t,g2_tag_visit,void *);
extern int32_t g2_lfs_dir_commitattr(void *,g2_commit *,uint32_t,const void *);
extern int32_t g2_lfs_dir_commitcrc(void *,g2_commit *);
extern int32_t g2_lfs_dir_getgstate(void *,void *,void *);
extern int32_t g2_lfs_dir_splittingcompact(void *,void *,
                const struct g2_lfs_attr *,uint32_t,void *,uint32_t,uint32_t);
extern int32_t g2_lfs_cache_drop(void *,void *);
extern int32_t g2_lfs_dir_fetch(void *,void *,const uint32_t *);
extern void g2_file_close_error(const char *,const char *,uint32_t);
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\littlefs\\lfs.c";
static const char count_assert[]="dir->count > 0";
static const char pred_assert[]="pdir";
static const char align_assert[]="commit.off % lfs->cfg->prog_size == 0";
static uint32_t *word(void *p,uint32_t off) {return (uint32_t *)((uint8_t *)p+off);}
static int32_t pair_cmp(const uint32_t *a,const uint32_t *b) {
    return !(a[0]==b[0] || a[1]==b[1] || a[0]==b[1] || a[1]==b[0]);
}
static int32_t commit_visit(void *context,uint32_t tag,const void *buffer) {
    void **parts=(void **)context;
    return g2_lfs_dir_commitattr(parts[0],(g2_commit *)parts[1],tag,buffer);
}
int32_t g2_lfs_dir_relocatingcommit(void *filesystem,void *directory,
                                     const uint32_t *pair,
                                     const struct g2_lfs_attr *attrs,
                                     uint32_t count,void *predecessor) {
    uint8_t *fs=(uint8_t *)filesystem;
    g2_mdir *dir=(g2_mdir *)directory,*pdir=(g2_mdir *)predecessor;
    int32_t state=0;
    uint32_t hasdelete=0u;
    for(uint32_t i=0;i<count;i++) {
        uint32_t tag=attrs[i].tag,type=(tag>>20u)&0x7ffu;
        if(type==0x401u) dir->count++;
        else if(type==0x4ffu) {
            if(dir->count==0u) g2_file_close_error(count_assert,path,2248u);
            dir->count--;hasdelete=1u;
        } else if(((tag>>20u)&0x700u)==0x600u) {
            const uint32_t *tail=(const uint32_t *)attrs[i].buffer;
            dir->tail[0]=tail[0];dir->tail[1]=tail[1];
            dir->split=(uint8_t)((tag>>20u)&1u);
        }
    }
    if(hasdelete && dir->count==0u) {
        if(!pdir) g2_file_close_error(pred_assert,path,2261u);
        int32_t err=g2_lfs_fs_pred(fs,dir->pair,pdir);
        if(err && err!=-2) return err;
        if(err!=-2 && pdir->split) {state=2;goto fixmlist;}
    }
    if(dir->erased) {
        uint8_t *cfg=(uint8_t *)(uintptr_t)*word(fs,0x68u);
        uint32_t limit=*word(cfg,0x4cu);
        if(limit==0u) limit=*word(cfg,0x1cu);
        g2_commit commit={dir->pair[0],dir->off,dir->etag,UINT32_MAX,
                           dir->off,limit-8u};
        void *context[2]={fs,&commit};
        int32_t err=g2_lfs_dir_traverse(fs,dir,dir->off,dir->etag,
                     attrs,count,0u,0u,0u,0u,0,commit_visit,context);
        if(err) {
            if(err==-28 || err==-84) goto compact;
            return err;
        }
        uint32_t delta[3];
        for(uint32_t i=0;i<3u;i++)
            delta[i]=*word(fs,0x30u+4u*i)^*word(fs,0x3cu+4u*i)^
                     *word(fs,0x48u+4u*i);
        delta[0]&=~0x3ffu;
        if(delta[0] || delta[1] || delta[2]) {
            err=g2_lfs_dir_getgstate(fs,dir,delta);
            if(err) return err;
            err=g2_lfs_dir_commitattr(fs,&commit,0x7ffffc0cu,delta);
            if(err) {
                if(err==-28 || err==-84) goto compact;
                return err;
            }
        }
        err=g2_lfs_dir_commitcrc(fs,&commit);
        if(err) {
            if(err==-28 || err==-84) goto compact;
            return err;
        }
        uint32_t prog=*word(cfg,0x18u);
        if(commit.off%prog!=0u) g2_file_close_error(align_assert,path,2335u);
        dir->off=commit.off;dir->etag=commit.ptag;
        for(uint32_t i=0;i<3u;i++) {
            *word(fs,0x3cu+4u*i)=*word(fs,0x30u+4u*i);
            *word(fs,0x48u+4u*i)=0u;
        }
        goto fixmlist;
    }
compact:
    g2_lfs_cache_drop(fs,fs+0x10u);
    state=g2_lfs_dir_splittingcompact(fs,dir,attrs,count,dir,0u,dir->count);
    if(state<0) return state;
fixmlist:;
    uint32_t oldpair[2]={pair[0],pair[1]};
    for(uint8_t *m=(uint8_t *)(uintptr_t)*word(fs,0x28u);
        m;m=(uint8_t *)(uintptr_t)*word(m,0u)) {
        g2_mdir *md=(g2_mdir *)(void *)(m+8u);
        if(pair_cmp(md->pair,oldpair)!=0) continue;
        *md=*dir;
        if(md->pair!=pair) {
            uint16_t *id=(uint16_t *)(void *)(m+4u);
            for(uint32_t i=0;i<count;i++) {
                uint32_t tag=attrs[i].tag,type=(tag>>20u)&0x7ffu;
                uint32_t tagid=(tag>>10u)&0x3ffu;
                if(type==0x4ffu && *id==tagid) {
                    md->pair[0]=UINT32_MAX;md->pair[1]=UINT32_MAX;
                } else if(type==0x4ffu && *id>tagid) {
                    (*id)--;
                    if(m[6]==2u) (*word(m,0x28u))--;
                } else if(type==0x401u && *id>=tagid) {
                    (*id)++;
                    if(m[6]==2u) (*word(m,0x28u))++;
                }
            }
        }
        while(*(uint16_t *)(void *)(m+4u)>=md->count && md->split) {
            if(pair_cmp(md->tail,(const uint32_t *)(void *)(fs+0x20u))!=0)
                *(uint16_t *)(void *)(m+4u)-=md->count;
            int32_t err=g2_lfs_dir_fetch(fs,md,md->tail);
            if(err) return err;
        }
    }
    return state;
}
