/* Pinned LittleFS two-pass orphan repair, stock 0x4cf7ac. */
#include <stdint.h>
#include <stddef.h>
typedef struct {
    uint32_t pair[2],rev,off,etag;
    uint16_t count;
    uint8_t erased,split;
    uint32_t tail[2];
} g2_mdir;
struct g2_lfs_attr {uint32_t tag;const void *buffer;};
_Static_assert(sizeof(g2_mdir)==32,"stock LittleFS metadata layout");
extern int32_t g2_lfs_dir_fetch(void *,void *,const uint32_t *);
extern int32_t g2_lfs_fs_parent(void *,const uint32_t *,void *);
extern int32_t g2_lfs_dir_getslice(void *,void *,uint32_t,uint32_t,
                                    uint32_t,void *,uint32_t);
extern int32_t g2_lfs_gstate_hasmovehere(void *,const void *);
extern void g2_lfs_fs_prepmove(void *,uint32_t,const uint32_t *);
extern int32_t g2_lfs_dir_orphaningcommit(void *,void *,
                                          const struct g2_lfs_attr *,uint32_t);
extern int32_t g2_lfs_dir_getgstate(void *,const void *,void *);
extern int32_t g2_lfs_fs_preporphans(void *,int8_t);
extern int32_t g2_log_transport_queue_failure(const char *,...);
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\littlefs\\lfs.c";
static const char half_orphan_log[]="%s:%d:debug: Fixing half-orphan {0x%x, 0x%x} -> {0x%x, 0x%x}%s\n";
static const char move_log[]="%s:%d:debug: Fixing move while fixing orphans {0x%x, 0x%x} 0x%hx\n%s\n";
static const char orphan_log[]="%s:%d:debug: Fixing orphan {0x%x, 0x%x}%s\n";
static int32_t pair_null(const uint32_t *p) {return p[0]==UINT32_MAX || p[1]==UINT32_MAX;}
static int32_t pair_sync(const uint32_t *a,const uint32_t *b) {
    return (a[0]==b[0] && a[1]==b[1]) || (a[0]==b[1] && a[1]==b[0]);
}
static uint32_t *word(void *p,uint32_t off) {return (uint32_t *)((uint8_t *)p+off);}
int32_t g2_lfs_fs_deorphan(void *filesystem,uint32_t powerloss) {
    uint8_t *fs=(uint8_t *)filesystem;
    uint32_t *state=word(fs,0x30u);
    if((state[0]&0x3ffu)==0u) return 0;
    uint32_t pass=0u;
    while(pass<2u) {
        g2_mdir pdir={0};pdir.split=1u;pdir.tail[0]=0u;pdir.tail[1]=1u;
        g2_mdir dir;
        uint32_t more=0u;
        while(!pair_null(pdir.tail)) {
            int32_t err=g2_lfs_dir_fetch(fs,&dir,pdir.tail);
            if(err) return err;
            if(!pdir.split) {
                g2_mdir parent;
                int32_t tag=g2_lfs_fs_parent(fs,pdir.tail,&parent);
                if(tag<0 && tag!=-2) return tag;
                if(pass==0u && tag!=-2) {
                    uint32_t pair[2];
                    int32_t found=g2_lfs_dir_getslice(fs,&parent,0x7ffffc00u,
                                      (uint32_t)tag,0u,pair,8u);
                    if(found<0) return found;
                    if(!pair_sync(pair,pdir.tail)) {
                        g2_log_transport_queue_failure(half_orphan_log,path,5038,
                            pdir.tail[0],pdir.tail[1],pair[0],pair[1],"");
                        uint32_t moveid=0x3ffu;
                        if(g2_lfs_gstate_hasmovehere(state,pdir.pair)) {
                            moveid=(state[0]>>10u)&0x3ffu;
                            g2_log_transport_queue_failure(move_log,path,5048,
                                pdir.pair[0],pdir.pair[1],moveid,"");
                            g2_lfs_fs_prepmove(fs,0x3ffu,NULL);
                        }
                        struct g2_lfs_attr attrs[2]={
                            {moveid==0x3ffu ? 0u : (0x4ffu<<20u)|(moveid<<10u),NULL},
                            {(0x600u<<20u)|(0x3ffu<<10u)|8u,pair}
                        };
                        int32_t committed=g2_lfs_dir_orphaningcommit(fs,&pdir,attrs,2u);
                        if(committed<0) return committed;
                        if(committed==3) more=1u;
                        continue;
                    }
                }
                if(pass==1u && tag==-2 && powerloss) {
                    g2_log_transport_queue_failure(orphan_log,path,5079,
                        pdir.tail[0],pdir.tail[1],"");
                    err=g2_lfs_dir_getgstate(fs,&dir,fs+0x48u);
                    if(err) return err;
                    struct g2_lfs_attr attr={
                        ((0x600u+dir.split)<<20u)|(0x3ffu<<10u)|8u,dir.tail};
                    int32_t committed=g2_lfs_dir_orphaningcommit(fs,&pdir,&attr,1u);
                    if(committed<0) return committed;
                    if(committed==3) more=1u;
                    continue;
                }
            }
            pdir=dir;
        }
        pass=more ? 0u : pass+1u;
    }
    return g2_lfs_fs_preporphans(fs,(int8_t)-(int32_t)(state[0]&0x3ffu));
}
