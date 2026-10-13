
/* Public Cordio comparator binding. Nine authenticated SMP call sites invoke
 * canonical4751c8; Bda callers require standard memcmp equality/sign contract. */
#include <stddef.h>
int memcmp(const void *first,const void *second,size_t size) {
    return (int)g2_lfs_memcmp(first,second,(uint32_t)size);
}
