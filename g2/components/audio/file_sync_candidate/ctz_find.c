/* Pinned LittleFS CTZ block finder, stock 0x4cd728. */
#include <stdint.h>
extern uint32_t g2_lfs_ctz_index(void *filesystem,uint32_t *offset);
extern int32_t g2_lfs_bd_read(void *filesystem,const void *program_cache,
                               void *read_cache,uint32_t hint,uint32_t block,
                               uint32_t offset,void *buffer,uint32_t size);
static uint32_t ceil_log2(uint32_t value) {
    uint32_t exponent=0,remaining=value-1u;
    while(remaining) {++exponent;remaining>>=1u;}
    return exponent;
}
static uint32_t trailing_zeroes(uint32_t value) {
    uint32_t count=0;
    while((value&1u)==0u) {++count;value>>=1u;}
    return count;
}
int32_t g2_lfs_ctz_find(void *filesystem,const void *program_cache,
                         void *read_cache,uint32_t head,uint32_t size,
                         uint32_t position,uint32_t *block,uint32_t *offset) {
    if(size==0u) {*block=UINT32_MAX;*offset=0;return 0;}
    uint32_t last=size-1u;
    uint32_t current=g2_lfs_ctz_index(filesystem,&last);
    uint32_t target=g2_lfs_ctz_index(filesystem,&position);
    while(current>target) {
        uint32_t skip=ceil_log2(current-target+1u)-1u;
        uint32_t ctz=trailing_zeroes(current);
        if(skip>ctz) skip=ctz;
        int32_t err=g2_lfs_bd_read(filesystem,program_cache,read_cache,
                                    4u,head,4u*skip,&head,4u);
        if(err) return err;
        current-=1u<<skip;
    }
    *block=head;
    *offset=position;
    return 0;
}
