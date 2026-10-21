/* Littlefs open-list membership, stock 0x4cb082; pinned upstream lfs.c. */
#include <stdint.h>
struct g2_lfs_mlist { struct g2_lfs_mlist *next; };
int32_t g2_lfs_mlist_isopen(void *head,void *node) {
    struct g2_lfs_mlist *p=(struct g2_lfs_mlist *)head;
    while(p) {
        if(p==node) return 1;
        p=p->next;
    }
    return 0;
}
