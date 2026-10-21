/* ARM library memcmp source equivalent, stock 0x4751c8. */
#include <stdint.h>
int32_t g2_lfs_memcmp(const void *first,const void *second,uint32_t size) {
    const uint8_t *a=(const uint8_t *)first,*b=(const uint8_t *)second;
    while(size && ((uintptr_t)a&3u)) {
        int32_t difference=(int32_t)*a++-(int32_t)*b++;
        if(difference) return difference;
        --size;
    }
    if(((uintptr_t)b&3u)==0u) {
        while(size>=4u) {
            uint32_t left=*(const uint32_t *)(const void *)a;
            uint32_t right=*(const uint32_t *)(const void *)b;
            if(left!=right) {
                /* Little-endian word order is opposite byte significance. */
                left=__builtin_bswap32(left);
                right=__builtin_bswap32(right);
                return left<right ? -1 : 1;
            }
            a+=4;b+=4;size-=4;
        }
    }
    while(size) {
        int32_t difference=(int32_t)*a++-(int32_t)*b++;
        if(difference) return difference;
        --size;
    }
    return 0;
}

/* Public Cordio comparator binding. Nine authenticated SMP call sites invoke
 * canonical4751c8; Bda callers require standard memcmp equality/sign contract. */
#include <stddef.h>
int memcmp(const void *first,const void *second,size_t size) {
    return (int)g2_lfs_memcmp(first,second,(uint32_t)size);
}
