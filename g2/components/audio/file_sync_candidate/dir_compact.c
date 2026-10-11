/* Pinned LittleFS metadata compaction and bad-block relocation, stock 0x4cc6ca. */
#include <stdint.h>
#include <stddef.h>
typedef struct {uint32_t pair[2],rev,off,etag;uint16_t count;uint8_t erased,split;uint32_t tail[2];} g2_mdir;
struct g2_lfs_attr {uint32_t tag;const void *buffer;};
typedef struct {uint32_t block,off,ptag,crc,begin,end;} g2_commit;
typedef int32_t (*g2_tag_visit)(void *,uint32_t,const void *);
extern int32_t g2_lfs_bd_erase(void *,uint32_t);
extern int32_t g2_lfs_dir_commitprog(void *,g2_commit *,const void *,uint32_t);
extern int32_t g2_lfs_dir_traverse(void *,void *,uint32_t,uint32_t,
             const struct g2_lfs_attr *,uint32_t,uint32_t,uint32_t,
             uint32_t,uint32_t,int32_t,g2_tag_visit,void *);
extern int32_t g2_lfs_dir_commitattr(void *,g2_commit *,uint32_t,const void *);
extern int32_t g2_lfs_dir_getgstate(void *,void *,void *);
extern int32_t g2_lfs_dir_commitcrc(void *,g2_commit *);
extern int32_t g2_lfs_cache_drop(void *,void *);
extern int32_t g2_lfs_alloc(void *,uint32_t *);
extern int32_t g2_log_transport_queue_failure(const char *,...);
extern void g2_file_close_error(const char *,const char *,uint32_t);
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\littlefs\\lfs.c";
static const char bad_block_log[]="%s:%d:debug: Bad block at 0x%x%s\n";
static const char superblock_warn[]="%s:%d:warn: Superblock 0x%x has become unwritable%s\n";
static const char align_assert[]="commit.off % lfs->cfg->prog_size == 0";
static uint32_t *word(void *p,uint32_t off) {return (uint32_t *)((uint8_t *)p+off);}
static int32_t pair_cmp(const uint32_t *a,const uint32_t *b) {
    return !(a[0]==b[0] || a[1]==b[1] || a[0]==b[1] || a[1]==b[0]);
}
static int32_t commit_visit(void *context,uint32_t tag,const void *buffer) {
    void **parts=(void **)context;
    return g2_lfs_dir_commitattr(parts[0],(g2_commit *)parts[1],tag,buffer);
}
int32_t g2_lfs_dir_compact(void *filesystem,void *directory,
                             const struct g2_lfs_attr *attrs,uint32_t count,
                             void *source,uint32_t begin,uint32_t end) {
    uint8_t *fs=(uint8_t *)filesystem;
    g2_mdir *dir=(g2_mdir *)directory;
    uint8_t *cfg=(uint8_t *)(uintptr_t)*word(fs,0x68u);
    int32_t cycles=(int32_t)*word(cfg,0x24u);
    uint32_t tired=cycles>0 &&
        (dir->rev+1u)%(((uint32_t)cycles+1u)|1u)==0u;
    uint32_t relocated=0u;
    dir->rev++;
    if(tired && pair_cmp(dir->pair,(const uint32_t[2]){0u,1u})!=0)
        goto relocate;
    for(;;) {
        uint32_t limit=*word(cfg,0x4cu);
        if(limit==0u) limit=*word(cfg,0x1cu);
        g2_commit commit={dir->pair[1],0u,UINT32_MAX,UINT32_MAX,0u,limit-8u};
        int32_t err=g2_lfs_bd_erase(fs,dir->pair[1]);
        if(err) {if(err==-84) goto relocate;return err;}
        err=g2_lfs_dir_commitprog(fs,&commit,&dir->rev,4u);
        if(err) {if(err==-84) goto relocate;return err;}
        void *context[2]={fs,&commit};
        err=g2_lfs_dir_traverse(fs,source,0u,UINT32_MAX,attrs,count,
               0x400ffc00u,0u,begin,end,-(int32_t)begin,commit_visit,context);
        if(err) {if(err==-84) goto relocate;return err;}
        if(dir->tail[0]!=UINT32_MAX && dir->tail[1]!=UINT32_MAX) {
            uint32_t tag=((0x600u+dir->split)<<20u)|(0x3ffu<<10u)|8u;
            err=g2_lfs_dir_commitattr(fs,&commit,tag,dir->tail);
            if(err) {if(err==-84) goto relocate;return err;}
        }
        uint32_t delta[3]={0u,0u,0u};
        for(uint32_t i=0;i<3u;i++) {
            if(!relocated)
                delta[i]^=*word(fs,0x3cu+4u*i)^*word(fs,0x30u+4u*i);
            delta[i]^=*word(fs,0x48u+4u*i);
        }
        delta[0]&=~0x3ffu;
        err=g2_lfs_dir_getgstate(fs,dir,delta);
        if(err) return err;
        if(delta[0] || delta[1] || delta[2]) {
            err=g2_lfs_dir_commitattr(fs,&commit,0x7ffffc0cu,delta);
            if(err) {if(err==-84) goto relocate;return err;}
        }
        err=g2_lfs_dir_commitcrc(fs,&commit);
        if(err) {if(err==-84) goto relocate;return err;}
        uint32_t prog=*word(cfg,0x18u);
        if(commit.off%prog!=0u) g2_file_close_error(align_assert,path,2084u);
        uint32_t tmp=dir->pair[0];dir->pair[0]=dir->pair[1];dir->pair[1]=tmp;
        dir->count=(uint16_t)(end-begin);
        dir->off=commit.off;dir->etag=commit.ptag;
        for(uint32_t i=0;i<3u;i++) {
            *word(fs,0x48u+4u*i)=0u;
            if(!relocated) *word(fs,0x3cu+4u*i)=*word(fs,0x30u+4u*i);
        }
        return relocated ? 1 : 0;
relocate:
        relocated=1u;
        g2_lfs_cache_drop(fs,fs+0x10u);
        if(!tired) g2_log_transport_queue_failure(bad_block_log,path,2102u,
                                                    dir->pair[1],"");
        if(pair_cmp(dir->pair,(const uint32_t[2]){0u,1u})==0) {
            g2_log_transport_queue_failure(superblock_warn,path,2108u,
                                            dir->pair[1],"");
            return -28;
        }
        int32_t allocerr=g2_lfs_alloc(fs,&dir->pair[1]);
        if(allocerr && (allocerr!=-28 || !tired)) return allocerr;
        tired=0u;
    }
}
