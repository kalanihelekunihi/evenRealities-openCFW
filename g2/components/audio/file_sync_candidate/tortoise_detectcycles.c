/* Pinned LittleFS tortoise cycle detector, stock 0x4cef18. */
#include <stdint.h>
extern int32_t g2_log_transport_queue_failure(const char *format,...);
static const char cycle_format[]="%s:%d:warn: Cycle detected in tail list%s\n";
static const char source_path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\littlefs\\lfs.c";
int32_t g2_lfs_tortoise_detectcycles(void *directory,void *state) {
    uint32_t *pair=(uint32_t *)((uint8_t *)directory+0x18u);
    uint32_t *t=(uint32_t *)state;
    if((pair[0]==t[0] && pair[1]==t[1]) ||
       (pair[0]==t[1] && pair[1]==t[0])) {
        g2_log_transport_queue_failure(cycle_format,source_path,4465,"");
        return -84;
    }
    if(t[2]==t[3]) {
        t[0]=pair[0];t[1]=pair[1];t[2]=0;t[3]<<=1u;
    }
    t[2]++;
    return 0;
}
