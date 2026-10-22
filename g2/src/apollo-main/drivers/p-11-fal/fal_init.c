/* FlashDB port FAL (fal.c, fal_flash.c, fal_partition.c) entry points,
 * native 0x597cde..0x597d0f, 0x597dec..0x597e17 and 0x597e1c..0x597e53
 * (firmware 2.2.6.10). Compared with the pinned FlashDB
 * (third-party/upstream/flashdb/port/fal/src, 714d615): the bodies are the
 * upstream ones with assert() and log_d/log_i/log_e compiled out.
 *
 * The rest of the FAL code already has C under other names:
 *   check_and_update_part_cache 0x597c6c, fal_partition_init 0x597cae
 *   (drivers/flash/fal/fal-partition-state.c), flash_device_find_by_part
 *   0x597d10 (fal-device-selector.c), fal_partition_read/write 0x597d34/0x597d72
 *   (storage/flashdb/flashdb-partition-*.c), fal_partition_erase 0x597db0
 *   (app/settings-fal), fal_flash_device_find 0x597e54 (fal-device-find.c). */
#include <stdint.h>

/* Same layout as struct fal_flash_dev with FAL_DEV_NAME_MAX 24 (see
 * drivers/flash/fal/fal-product-config/product_tables.h). */
struct p11_fal_flash_dev {
    char name[24];          /* +0x00 */
    uint32_t addr;          /* +0x18 */
    uint32_t len;           /* +0x1c */
    uint32_t blk_size;      /* +0x20 */
    int (*init)(void);      /* +0x24 */
    int (*read)(int32_t offset, uint8_t *buf, uint32_t size);        /* +0x28 */
    int (*write)(int32_t offset, const uint8_t *buf, uint32_t size); /* +0x2c */
    int (*erase)(int32_t offset, uint32_t size);                     /* +0x30 */
    uint32_t write_gran;    /* +0x34 */
};
_Static_assert(sizeof(struct p11_fal_flash_dev) == 0x38u, "fal_flash_dev size");

/* ROM 0x78f0a4: device table (one entry, "norflash"); ROM 0x78f0a8: its length. */
extern const struct p11_fal_flash_dev *const g2_fal_flash_device_table[];
extern const uint32_t g2_fal_flash_device_count;

extern uint32_t g2_fal_partition_table_base;   /* RAM 0x200745dc, partition_table */
extern uint32_t g2_fal_partition_table_length; /* RAM 0x200745e0, partition_table_len */
extern uint8_t g2_fal_flash_init_ok;           /* RAM 0x20074fc6, fal_flash.c init_ok */
extern uint8_t g2_fal_init_ok;                 /* RAM 0x20074fc5, fal.c init_ok */

extern uint32_t g2_fal_partition_init(void);                               /* 0x597cae */
extern int32_t audio_uart_font_path_compare(const char *a, const char *b); /* 0x46cacc, strcmp */

/* fal_partition_find: the 64-byte partition rows have their name at +4. */
uint32_t fal_partition_find_597cde(const char *name)
{
    uint32_t i;

    for (i = 0; i < g2_fal_partition_table_length; i++) {
        if (audio_uart_font_path_compare(name,
                (const char *)(uintptr_t)(g2_fal_partition_table_base + i * 64u + 4u)) == 0)
            return g2_fal_partition_table_base + i * 64u;
    }
    return 0u;
}

/* fal_flash_init: run each device's optional init hook once. */
int32_t fal_flash_init_597e1c(void)
{
    uint32_t i;

    if (g2_fal_flash_init_ok != 0u)
        return 0;
    for (i = 0; i < g2_fal_flash_device_count; i++) {
        if (g2_fal_flash_device_table[i]->init != 0)
            g2_fal_flash_device_table[i]->init();
    }
    g2_fal_flash_init_ok = 1u;
    return 0;
}

/* fal_init: returns the partition count (2 on this product) or a negative
 * error; the success/failure log lines are compiled out. */
int32_t fal_init_597dec(void)
{
    int32_t result = fal_flash_init_597e1c();

    if (result >= 0)
        result = (int32_t)g2_fal_partition_init();
    if (result > 0 && g2_fal_init_ok == 0u)
        g2_fal_init_ok = 1u;
    else if (result <= 0)
        g2_fal_init_ok = 0u;
    return result;
}
