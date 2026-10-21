/* Stock LittleFS public sync wrapper at 0x4cfb08. */
#include <stdint.h>

extern int32_t g2_lfs_mlist_isopen(void *, void *);
extern void g2_file_close_error(const char *, const char *, uint32_t);
extern int32_t g2_lfs_file_sync(void *, void *);

static const char source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\littlefs\\lfs.c";
static const char must_be_open[] =
    "lfs_mlist_isopen(lfs->mlist, (struct lfs_mlist*)file)";

int32_t audio_file_lfs_sync_4cfb08(void *filesystem, void *file) {
    void *list = (void *)(uintptr_t)*(uint32_t *)((uint8_t *)filesystem + 0x28u);
    if (g2_lfs_mlist_isopen(list, file) == 0)
        g2_file_close_error(must_be_open, source, 0x181bu);
    return g2_lfs_file_sync(filesystem, file);
}
