/* Stock LittleFS lfs_mkdir_ at 0x4cd3aa, using the Apollo 32-bit layout. */
#include <stdint.h>

struct lfs_mdir32 {
    uint32_t pair[2], rev, off, etag;
    uint16_t count;
    uint8_t erased, split;
    uint32_t tail[2];
};
struct lfs_mlist32 {
    uint32_t next;
    uint16_t id;
    uint8_t type, pad;
    struct lfs_mdir32 m;
};
struct lfs_attr32 { uint32_t tag; const void *buffer; };

extern int32_t audio_file_lfs_forceconsistency(void *);
extern int32_t audio_file_lfs_dir_find(void *, void *, const char **, uint16_t *);
extern int32_t audio_file_lfs_path_islast(const char *);
extern uint32_t audio_file_lfs_path_namelen(const char *);
extern void g2_lfs_alloc_checkpoint(void *);
extern int32_t g2_lfs_dir_alloc(void *, void *);
extern int32_t g2_lfs_dir_fetch(void *, void *, const uint32_t *);
extern int32_t g2_lfs_dir_commit(void *, void *, const struct lfs_attr32 *, uint32_t);
extern int32_t g2_lfs_fs_preporphans(void *, int8_t);

static uint32_t word(const void *p, uint32_t offset) {
    return *(const uint32_t *)((const uint8_t *)p + offset);
}

int32_t audio_file_lfs_mkdir_core_4cd3aa(void *filesystem,
                                          const char *path,
                                          uint32_t option) {
    (void)option; /* stock public wrapper passes zero */
    int32_t err = audio_file_lfs_forceconsistency(filesystem);
    if (err != 0)
        return err;

    struct lfs_mlist32 cwd;
    cwd.next = word(filesystem, 0x28u);
    uint16_t id;
    err = audio_file_lfs_dir_find(filesystem, &cwd.m, &path, &id);
    if (!(err == -2 && audio_file_lfs_path_islast(path) != 0))
        return err < 0 ? err : -17;

    uint32_t nlen = audio_file_lfs_path_namelen(path);
    if (nlen > word(filesystem, 0x70u))
        return -36;

    g2_lfs_alloc_checkpoint(filesystem);
    struct lfs_mdir32 dir;
    err = g2_lfs_dir_alloc(filesystem, &dir);
    if (err != 0)
        return err;

    struct lfs_mdir32 pred = cwd.m;
    while (pred.split != 0) {
        err = g2_lfs_dir_fetch(filesystem, &pred, pred.tail);
        if (err != 0)
            return err;
    }

    const struct lfs_attr32 old_tail = {0x600ffc08u, pred.tail};
    err = g2_lfs_dir_commit(filesystem, &dir, &old_tail, 1u);
    if (err != 0)
        return err;

    if (cwd.m.split != 0) {
        err = g2_lfs_fs_preporphans(filesystem, 1);
        if (err != 0)
            return err;
        cwd.id = 0;
        cwd.type = 0;
        *(uint32_t *)((uint8_t *)filesystem + 0x28u) = (uint32_t)(uintptr_t)&cwd;
        const struct lfs_attr32 new_tail = {0x600ffc08u, dir.pair};
        err = g2_lfs_dir_commit(filesystem, &pred, &new_tail, 1u);
        *(uint32_t *)((uint8_t *)filesystem + 0x28u) = cwd.next;
        if (err != 0)
            return err;
        err = g2_lfs_fs_preporphans(filesystem, -1);
        if (err != 0)
            return err;
    }

    const struct lfs_attr32 attrs[4] = {
        {0x40100000u | ((uint32_t)id << 10u), 0},
        {0x00200000u | ((uint32_t)id << 10u) | nlen, path},
        {0x20000008u | ((uint32_t)id << 10u), dir.pair},
        {cwd.m.split ? 0u : 0x600ffc08u, dir.pair},
    };
    err = g2_lfs_dir_commit(filesystem, &cwd.m, attrs, 4u);
    return err;
}
