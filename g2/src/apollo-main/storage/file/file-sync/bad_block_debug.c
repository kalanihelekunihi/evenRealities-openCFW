/* Source-defined LittleFS debug call used by stock 0x4cdd0e/0x4cde54. */
#include <stdint.h>
extern int32_t g2_log_transport_queue_failure(const char *format,...);
static const char format[]="%s:%d:debug: Bad block at 0x%x%s\n";
static const char source_file[]=
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\littlefs\\lfs.c";
static const char empty_suffix[]="";
void g2_lfs_debug_bad_block(uint32_t block,uint32_t line) {
    (void)g2_log_transport_queue_failure(format,source_file,line,block,
                                          empty_suffix);
}
