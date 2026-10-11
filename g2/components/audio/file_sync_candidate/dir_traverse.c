/* Pinned LittleFS bounded metadata traversal, stock 0x4cb5ac. */
#include <stdint.h>
#include <stddef.h>
typedef struct {uint32_t pair[2],rev,off,etag;uint16_t count;uint8_t erased,split;uint32_t tail[2];} g2_mdir;
struct g2_lfs_attr {uint32_t tag;const void *buffer;};
struct g2_diskoff {uint32_t block,off;};
struct g2_user_attr {uint8_t type;void *buffer;uint32_t size;};
typedef int32_t (*g2_tag_visit)(void *,uint32_t,const void *);
typedef struct {
    const g2_mdir *dir;uint32_t off,ptag;
    const struct g2_lfs_attr *attrs;int32_t attrcount;
    uint32_t tmask,ttag,begin,end;int32_t diff;
    g2_tag_visit visit;void *context;
    uint32_t tag;const void *buffer;struct g2_diskoff disk;
} g2_frame;
extern int32_t g2_lfs_bd_read(void *,const void *,void *,uint32_t,uint32_t,
                               uint32_t,void *,uint32_t);
extern void g2_file_close_error(const char *,const char *,uint32_t);
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\littlefs\\lfs.c";
static const char depth_assert[]="sp < LFS_DIR_TRAVERSE_DEPTH";
static uint32_t tag_id(uint32_t tag) {return (tag>>10u)&0x3ffu;}
static uint32_t tag_type1(uint32_t tag) {return (tag>>20u)&0x700u;}
static uint32_t tag_type3(uint32_t tag) {return (tag>>20u)&0x7ffu;}
static uint32_t tag_size(uint32_t tag) {return tag&0x3ffu;}
static uint32_t tag_dsize(uint32_t tag) {
    return 4u+(tag_size(tag)==0x3ffu ? 0u : tag_size(tag));
}
static int32_t filter(void *context,uint32_t tag,const void *buffer) {
    (void)buffer;
    uint32_t *filtertag=(uint32_t *)context;
    uint32_t mask=(tag&0x10000000u) ? 0x7ffffc00u : 0x700ffc00u;
    if((mask&tag)==(mask&*filtertag) || tag_size(*filtertag)==0x3ffu ||
       (tag&0x7ffffc00u)==(0x4ff00000u|(*filtertag&0xffc00u))) {
        *filtertag=0u;return 1;
    }
    if(tag_type1(tag)==0x400u && tag_id(tag)<=tag_id(*filtertag))
        *filtertag+=(uint32_t)((int32_t)(int8_t)((tag>>20u)&0xffu)*1024);
    return 0;
}
int32_t g2_lfs_dir_traverse(void *filesystem,void *directory,
             uint32_t off,uint32_t ptag,const struct g2_lfs_attr *attrs,
             uint32_t attrcount,uint32_t tmask,uint32_t ttag,
             uint32_t begin,uint32_t end,int32_t diff,
             g2_tag_visit visit,void *context) {
    const g2_mdir *dir=(const g2_mdir *)directory;
    g2_frame stack[3];uint32_t sp=0u;
    uint32_t tag;const void *buffer;struct g2_diskoff disk={0u,0u};
    int32_t result;
    for(;;) {
        for(;;) {
            if(off+tag_dsize(ptag)<dir->off) {
                off+=tag_dsize(ptag);
                int32_t err=g2_lfs_bd_read(filesystem,NULL,filesystem,4u,
                                             dir->pair[0],off,&tag,4u);
                if(err) return err;
                tag=(__builtin_bswap32(tag)^ptag)|0x80000000u;
                disk.block=dir->pair[0];disk.off=off+4u;
                buffer=&disk;ptag=tag;
            } else if(attrcount>0u) {
                tag=attrs[0].tag;buffer=attrs[0].buffer;
                attrs++;attrcount--;
            } else {
                result=0;break;
            }
            if((0x7ff00000u&tmask&tag)!=(0x7ff00000u&tmask&ttag)) continue;
            if(tag_id(tmask)!=0u) {
                if(sp>=3u) g2_file_close_error(depth_assert,path,957u);
                stack[sp]=(g2_frame){dir,off,ptag,attrs,(int32_t)attrcount,
                      tmask,ttag,begin,end,diff,visit,context,tag,buffer,disk};
                sp++;
                tmask=0u;ttag=0u;begin=0u;end=0u;diff=0;
                visit=filter;context=&stack[sp-1u].tag;
                continue;
            }
popped:
            if(tag_id(tmask)!=0u &&
               !(tag_id(tag)>=begin && tag_id(tag)<end)) continue;
            if(tag_type3(tag)==0u) {
                /* LFS_FROM_NOOP */
            } else if(tag_type3(tag)==0x101u) {
                if(visit==filter) continue;
                if(sp>=3u) g2_file_close_error(depth_assert,path,1007u);
                stack[sp]=(g2_frame){dir,off,ptag,attrs,(int32_t)attrcount,
                    tmask,ttag,begin,end,diff,visit,context,0u,NULL,disk};
                sp++;
                uint32_t fromid=tag_size(tag),toid=tag_id(tag);
                dir=(const g2_mdir *)buffer;off=0u;ptag=UINT32_MAX;
                attrs=NULL;attrcount=0u;tmask=0x600ffc00u;ttag=0x20000000u;
                begin=fromid;end=fromid+1u;
                diff+=(int32_t)toid-(int32_t)fromid;
            } else if(tag_type3(tag)==0x102u) {
                const struct g2_user_attr *a=(const struct g2_user_attr *)buffer;
                for(uint32_t i=0;i<tag_size(tag);i++) {
                    result=visit(context,((0x300u+a[i].type)<<20u)|
                       ((tag_id(tag)+(uint32_t)diff)<<10u)|a[i].size,
                       a[i].buffer);
                    if(result<0) return result;
                    if(result) break;
                }
            } else {
                result=visit(context,tag+(uint32_t)(diff*1024),buffer);
                if(result<0) return result;
                if(result) break;
            }
        }
        if(sp==0u) return result;
        sp--;
        g2_frame *frame=&stack[sp];
        dir=frame->dir;off=frame->off;ptag=frame->ptag;
        attrs=frame->attrs;attrcount=(uint32_t)frame->attrcount;
        tmask=frame->tmask;ttag=frame->ttag;begin=frame->begin;end=frame->end;
        diff=frame->diff;visit=frame->visit;context=frame->context;
        tag=frame->tag;buffer=frame->buffer;disk=frame->disk;
        goto popped;
    }
}
