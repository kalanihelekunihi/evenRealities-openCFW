/* Pinned LittleFS path lookup, native 0x4cc04a and callback. */
#include <stdint.h>
typedef struct {uint32_t pair[2],rev,off,etag;uint16_t count;uint8_t erased,split;uint32_t tail[2];} mdir;
typedef struct {void *filesystem;const char *name;uint32_t size;} match_data;
extern int32_t g2_lfs_dir_fetchmatch(void *,void *,const uint32_t *,uint32_t,
        uint32_t,uint16_t *,int32_t (*)(void *,uint32_t,const void *),void *);
extern int32_t g2_lfs_bd_cmp(void *,void *,void *,uint32_t,uint32_t,uint32_t,const void *,uint32_t);
extern int32_t audio_file_lfs_dir_get(void *,void *,uint32_t,uint32_t,void *);
extern void audio_file_lfs_ctz_fromle32(void *);
static uint32_t namelen(const char *s) {uint32_t n=0;while(s[n]&&s[n]!='/')n++;return n;}
static uint32_t slashes(const char *s) {uint32_t n=0;while(s[n]=='/')n++;return n;}
static int32_t eq(const char *p,const char *lit,uint32_t n) {
    for(uint32_t i=0;i<n;i++) if(p[i]!=lit[i]) return 0;
    return 1;
}
int32_t audio_file_lfs_dir_find_match(void *data,uint32_t tag,const void *buffer) {
    const match_data *m=(const match_data *)data;
    const uint32_t *disk=(const uint32_t *)buffer;
    uint32_t sz=tag&0x3ffu,diff=m->size<sz?m->size:sz;
    int32_t cmp=g2_lfs_bd_cmp(m->filesystem,0,m->filesystem,diff,
                              disk[0],disk[1],m->name,diff);
    if(cmp!=0) return cmp;
    return m->size==sz?0:(m->size<sz?1:2);
}
int32_t audio_file_lfs_dir_find(void *filesystem,void *directory,
                                 const char **path,uint16_t *id) {
    uint8_t *fs=(uint8_t *)filesystem;
    mdir *dir=(mdir *)directory;
    const char *name=*path;
    uint32_t tag=0x002ffc00u; /* LFS_TYPE_DIR, id 0x3ff */
    dir->tail[0]=*(uint32_t *)(void *)(fs+0x20u);
    dir->tail[1]=*(uint32_t *)(void *)(fs+0x24u);
    if(*name==0) return -22;
    for(;;) {
nextname:
        if(((tag>>20u)&0x7ffu)==2u) name+=slashes(name);
        uint32_t n=namelen(name);
        if(n==1u && eq(name,".",1u)) {name+=n;goto nextname;}
        if(n==2u && eq(name,"..",2u)) return -22;
        const char *suffix=name+n;
        uint32_t depth=1u;
        for(;;) {
            suffix+=slashes(suffix);
            uint32_t sn=namelen(suffix);
            if(sn==0u) break;
            if(sn==1u && eq(suffix,".",1u)) {
            } else if(sn==2u && eq(suffix,"..",2u)) {
                if(--depth==0u) {name=suffix+sn;goto nextname;}
            } else depth++;
            suffix+=sn;
        }
        if(*name==0) return (int32_t)tag;
        *path=name;
        if(((tag>>20u)&0x7ffu)!=2u) return -20;
        uint32_t entry=(tag>>10u)&0x3ffu;
        if(entry!=0x3ffu) {
            int32_t res=audio_file_lfs_dir_get(filesystem,dir,0x700ffc00u,
                                                0x20000008u|(entry<<10u),dir->tail);
            if(res<0) return res;
            audio_file_lfs_ctz_fromle32(dir->tail);
        }
        for(;;) {
            match_data match={filesystem,name,n};
            int32_t result=g2_lfs_dir_fetchmatch(filesystem,dir,dir->tail,
                    0x78000000u,0x00100000u|n,id,
                    audio_file_lfs_dir_find_match,&match);
            if(result<0) return result;
            tag=(uint32_t)result;
            if(tag!=0u) break;
            if(dir->split==0u) return -2;
        }
        name+=n;
    }
}
