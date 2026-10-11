/* LittleFS lfs_file_opencfg native 0x4cda36. Control flow follows the
 * pinned upstream lfs_file_opencfg_ while offsets and tags are checked
 * against the original Apollo image. All filesystem operations remain
 * actual typed descendants. */
#include <stdint.h>

struct lfs_attr {uint32_t tag;const void *buffer;};
extern int32_t audio_file_lfs_forceconsistency(void *); /* 0x4cf9e0 */
extern int32_t audio_file_lfs_dir_find(void *,void *,const char **,uint16_t *); /* 0x4cc04a */
extern int32_t audio_file_lfs_path_islast(const char *); /* 0x4cad80 */
extern int32_t audio_file_lfs_path_isdir(const char *); /* 0x4cadac */
extern uint32_t audio_file_lfs_path_namelen(const char *); /* 0x4cad76 */
extern void audio_file_lfs_mlist_append(void *,void *); /* 0x4cb0bc */
extern int32_t g2_lfs_dir_commit(void *,void *,const struct lfs_attr *,uint32_t); /* selected 0x4cd388 */
extern int32_t audio_file_lfs_dir_get(void *,void *,uint32_t,uint32_t,void *); /* 0x4cb3c8 */
extern void audio_file_lfs_ctz_fromle32(void *); /* 0x4cafea */
extern void *audio_file_lfs_malloc(uint32_t); /* 0x4ca80a */
extern void g2_lfs_cache_zero(void *,void *); /* selected 0x4ca822 */
extern int32_t g2_lfs_file_close(void *,void *); /* selected 0x4cdce4 */

static uint32_t get(const void *p,uint32_t offset) {
    return *(const uint32_t *)(const void *)((const uint8_t *)p+offset);
}
static void set(void *p,uint32_t offset,uint32_t value) {
    *(uint32_t *)(void *)((uint8_t *)p+offset)=value;
}
static uint32_t tag(uint32_t type,uint32_t id,uint32_t size) {
    return (type<<20u)|(id<<10u)|size;
}
static uint32_t type3(uint32_t value) {return (value>>20u)&0x7ffu;}
static uint32_t cfgword(const void *file,uint32_t offset) {
    return get((void *)(uintptr_t)get(file,0x50u),offset);
}
int32_t audio_file_lfs_opencfg(void *filesystem,void *file,const char *path,
                                uint32_t flags,const void *configuration) {
    uint8_t *f=(uint8_t *)file;
    if((flags&2u)!=0u) {
        int32_t err=audio_file_lfs_forceconsistency(filesystem);
        if(err!=0) return err;
    }
    set(file,0x50u,(uint32_t)(uintptr_t)configuration);
    set(file,0x30u,flags);
    set(file,0x34u,0u);
    set(file,0x3cu,0u);
    set(file,0x4cu,0u);
    uint16_t *id=(uint16_t *)(void *)(f+4u);
    int32_t found=audio_file_lfs_dir_find(filesystem,f+8u,&path,id);
    int32_t err=found;
    if(found<0 && !(found==-2 && audio_file_lfs_path_islast(path)!=0)) goto cleanup;
    f[6u]=1u;
    audio_file_lfs_mlist_append(filesystem,file);
    if(found==-2) {
        if((flags&0x100u)==0u) {err=-2;goto cleanup;}
        if(audio_file_lfs_path_isdir(path)!=0) {err=-20;goto cleanup;}
        uint32_t name_size=audio_file_lfs_path_namelen(path);
        if(name_size>get(filesystem,0x70u)) {err=-36;goto cleanup;}
        struct lfs_attr attrs[3]={
            {tag(0x401u,*id,0u),0},
            {tag(0x001u,*id,name_size),path},
            {tag(0x201u,*id,0u),0}
        };
        err=g2_lfs_dir_commit(filesystem,f+8u,attrs,3u);
        if(err==-28) err=-36;
        if(err!=0) goto cleanup;
        found=(int32_t)tag(0x201u,0u,0u);
    } else if((flags&0x200u)!=0u) {
        err=-17;goto cleanup;
    } else if(type3((uint32_t)found)!=0x001u) {
        err=-21;goto cleanup;
    } else if((flags&0x400u)!=0u) {
        found=(int32_t)tag(0x201u,*id,0u);
        set(file,0x30u,get(file,0x30u)|0x10000u);
    } else {
        found=audio_file_lfs_dir_get(filesystem,f+8u,0x700ffc00u,
                tag(0x200u,*id,8u),f+0x28u);
        if(found<0) {err=found;goto cleanup;}
        audio_file_lfs_ctz_fromle32(f+0x28u);
    }
    uint32_t attrs_count=cfgword(file,8u);
    uint8_t *attrs=(uint8_t *)(uintptr_t)cfgword(file,4u);
    for(uint32_t i=0u;i<attrs_count;i++) {
        uint8_t *a=attrs+12u*i;
        uint32_t size=get(a,8u);
        if((get(file,0x30u)&1u)!=0u) {
            int32_t result=audio_file_lfs_dir_get(filesystem,f+8u,0x7ffffc00u,
                tag(0x300u+a[0],*id,size),(void *)(uintptr_t)get(a,4u));
            if(result<0 && result!=-2) {err=result;goto cleanup;}
        }
        if((get(file,0x30u)&2u)!=0u) {
            if(size>get(filesystem,0x78u)) {err=-28;goto cleanup;}
            set(file,0x30u,get(file,0x30u)|0x10000u);
        }
    }
    uint32_t buffer=cfgword(file,0u);
    if(buffer==0u) {
        uint8_t *cfg=(uint8_t *)(uintptr_t)get(filesystem,0x68u);
        buffer=(uint32_t)(uintptr_t)audio_file_lfs_malloc(get(cfg,0x28u));
        if(buffer==0u) {err=-12;goto cleanup;}
    }
    set(file,0x4cu,buffer);
    g2_lfs_cache_zero(filesystem,f+0x40u);
    if(type3((uint32_t)found)==0x201u) {
        set(file,0x28u,UINT32_MAX-1u);
        set(file,0x2cu,(uint32_t)found&0x3ffu);
        set(file,0x30u,get(file,0x30u)|0x100000u);
        set(file,0x40u,UINT32_MAX-1u);
        set(file,0x44u,0u);
        uint8_t *cfg=(uint8_t *)(uintptr_t)get(filesystem,0x68u);
        set(file,0x48u,get(cfg,0x28u));
        if(get(file,0x2cu)>0u) {
            uint32_t n=get(file,0x48u);
            if(n>0x3feu) n=0x3feu;
            int32_t result=audio_file_lfs_dir_get(filesystem,f+8u,0x700ffc00u,
                tag(0x200u,*id,n),(void *)(uintptr_t)buffer);
            if(result<0) {err=result;goto cleanup;}
        }
    }
    return 0;
cleanup:
    set(file,0x30u,get(file,0x30u)|0x80000u);
    (void)g2_lfs_file_close(filesystem,file);
    return err;
}
