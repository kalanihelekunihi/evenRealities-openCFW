/* Authenticated LittleFS no-space diagnostic, stock 0x4cb222 caller. */
#include <stdint.h>
extern int32_t g2_log_transport_queue_failure(const char *format,...);
static const char format[]="%s:%d:error: No more free space 0x%x%s\n";
static const char source_file[]=
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\littlefs\\lfs.c";
static const char empty_suffix[]="";
void g2_lfs_no_space_log(uint32_t block) {
    (void)g2_log_transport_queue_failure(format,source_file,706u,block,
                                          empty_suffix);
}
