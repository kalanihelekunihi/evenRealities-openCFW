/* Pinned LittleFS split sizing/compaction, stock 0x4cc9a0. */
#include <stdint.h>
#include <stddef.h>
typedef struct {uint32_t pair[2],rev,off,etag;uint16_t count;uint8_t erased,split;uint32_t tail[2];} g2_mdir;
struct g2_lfs_attr {uint32_t tag;const void *buffer;};
typedef int32_t (*g2_tag_visit)(void *,uint32_t,const void *);
extern int32_t g2_lfs_dir_traverse(void *,void *,uint32_t,uint32_t,
             const struct g2_lfs_attr *,uint32_t,uint32_t,uint32_t,
             uint32_t,uint32_t,int32_t,g2_tag_visit,void *);
extern int32_t g2_lfs_dir_split(void *,void *,const struct g2_lfs_attr *,
                                 uint32_t,void *,uint32_t,uint32_t);
extern int32_t g2_lfs_fs_size(void *);
extern int32_t g2_lfs_dir_compact(void *,void *,const struct g2_lfs_attr *,
                                   uint32_t,void *,uint32_t,uint32_t);
extern int32_t g2_log_transport_queue_failure(const char *,...);
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\littlefs\\lfs.c";
static const char split_warn[]="%s:%d:warn: Unable to split {0x%x, 0x%x}%s\n";
static const char expand_log[]="%s:%d:debug: Expanding superblock at rev %u%s\n";
static const char expand_warn[]="%s:%d:warn: Unable to expand superblock%s\n";
static uint32_t rd32(const void *p,uint32_t off) {
    return *(const uint32_t *)((const uint8_t *)p+off);
}
static uint32_t min(uint32_t a,uint32_t b) {return a<b?a:b;}
static int32_t count_size(void *context,uint32_t tag,const void *buffer) {
    (void)buffer;
    uint32_t size=tag&0x3ffu;
    *(uint32_t *)context+=4u+(size==0x3ffu ? 0u : size);
    return 0;
}
int32_t g2_lfs_dir_splittingcompact(void *filesystem,void *directory,
               const struct g2_lfs_attr *attrs,uint32_t count,
               void *source,uint32_t begin,uint32_t end) {
    uint8_t *fs=(uint8_t *)filesystem;
    g2_mdir *dir=(g2_mdir *)directory;
    uint8_t *cfg=(uint8_t *)(uintptr_t)rd32(fs,0x68u);
    for(;;) {
        uint32_t split=begin;
        while(end-split>1u) {
            uint32_t size=0u;
            int32_t err=g2_lfs_dir_traverse(fs,source,0u,UINT32_MAX,
                attrs,count,0x400ffc00u,0u,split,end,-(int32_t)split,
                count_size,&size);
            if(err) return err;
            uint32_t max=rd32(cfg,0x4cu);
            if(max==0u) max=rd32(cfg,0x1cu);
            uint32_t prog=rd32(cfg,0x18u);
            uint32_t half=(max/2u+prog-1u)/prog*prog;
            if(end-split<0xffu && size<=min(max-40u,half)) break;
            split+=(end-split)/2u;
        }
        if(split==begin) break;
        int32_t err=g2_lfs_dir_split(fs,dir,attrs,count,source,split,end);
        if(err && err!=-28) return err;
        if(err) {
            g2_log_transport_queue_failure(split_warn,path,2192u,
                dir->pair[0],dir->pair[1],"");
            break;
        }
        end=split;
    }
    int32_t cycles=(int32_t)rd32(cfg,0x24u);
    if(cycles>0 && (dir->rev+1u)%(((uint32_t)cycles+1u)|1u)==0u &&
       (dir->pair[0]==0u || dir->pair[1]==0u ||
        dir->pair[0]==1u || dir->pair[1]==1u)) {
        int32_t size=g2_lfs_fs_size(fs);
        if(size<0) return size;
        uint32_t blocks=rd32(fs,0x6cu);
        if(blocks-(uint32_t)size>blocks/8u) {
            g2_log_transport_queue_failure(expand_log,path,2213u,dir->rev,"");
            int32_t err=g2_lfs_dir_split(fs,dir,attrs,count,source,begin,end);
            if(err && err!=-28) return err;
            if(err) g2_log_transport_queue_failure(expand_warn,path,2223u,"");
            else end=1u;
        }
    }
    return g2_lfs_dir_compact(fs,dir,attrs,count,source,begin,end);
}
