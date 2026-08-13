/*
 * Host oracle which compiles the authenticated upstream FAL 0.5.99
 * fal_partition.c used by FlashDB 2.1.1.  Only the recovered read-only device
 * seam is supplied; write and erase are permanently failing test stubs.
 */

#include <stddef.h>
#include <stdint.h>
#include <string.h>

#define _FAL_H_
#define _FAL_DEF_H_
#define FAL_DEV_NAME_MAX 24
#define FAL_PART_HAS_TABLE_CFG
#define assert(expression) ((void)(expression))
#define log_i(...) ((void)0)
#define log_e(...) ((void)0)
#define log_d(...) ((void)0)

struct fal_flash_dev {
    char name[FAL_DEV_NAME_MAX];
    uint32_t addr;
    size_t len;
    size_t blk_size;
    struct {
        int (*init)(void);
        int (*read)(long offset, uint8_t *buf, size_t size);
        int (*write)(long offset, const uint8_t *buf, size_t size);
        int (*erase)(long offset, size_t size);
    } ops;
    size_t write_gran;
};

struct fal_partition {
    uint32_t magic_word;
    char name[FAL_DEV_NAME_MAX];
    char flash_name[FAL_DEV_NAME_MAX];
    long offset;
    size_t len;
    uint32_t reserved;
};

typedef struct fal_partition *fal_partition_t;

static int open_cfw_test_flashdb_oracle_init(void);
static int open_cfw_test_flashdb_oracle_read(
    long offset,
    uint8_t *buffer,
    size_t size
);
static int open_cfw_test_flashdb_oracle_write(
    long offset,
    const uint8_t *buffer,
    size_t size
);
static int open_cfw_test_flashdb_oracle_erase(long offset, size_t size);

static const struct fal_flash_dev open_cfw_test_flashdb_oracle_device = {
    "norflash",
    0x01FC0000U,
    0x02000000U,
    0x00001000U,
    {
        open_cfw_test_flashdb_oracle_init,
        open_cfw_test_flashdb_oracle_read,
        open_cfw_test_flashdb_oracle_write,
        open_cfw_test_flashdb_oracle_erase
    },
    1U
};

const struct fal_flash_dev *fal_flash_device_find(const char *name)
{
    return strcmp(name, "norflash") == 0
        ? &open_cfw_test_flashdb_oracle_device
        : (const struct fal_flash_dev *)0;
}

#define FAL_PART_TABLE { \
    { 0x45503130U, "kvdb", "norflash", \
        0x01FC0000L, 0x00038000U, 0U }, \
    { 0x45503130U, "NVdb", "norflash", \
        0x01FF8000L, 0x00008000U, 0U } \
}

#include "../../third_party/flashdb/port/fal/src/fal_partition.c"

static int open_cfw_test_flashdb_oracle_status;
static unsigned int open_cfw_test_flashdb_oracle_calls;
static unsigned int open_cfw_test_flashdb_oracle_last_offset;
static unsigned int open_cfw_test_flashdb_oracle_last_size;

static int open_cfw_test_flashdb_oracle_init(void)
{
    return 0;
}

static int open_cfw_test_flashdb_oracle_read(
    long offset,
    uint8_t *buffer,
    size_t size
)
{
    size_t index;

    open_cfw_test_flashdb_oracle_calls += 1U;
    open_cfw_test_flashdb_oracle_last_offset = (unsigned int)offset;
    open_cfw_test_flashdb_oracle_last_size = (unsigned int)size;
    if (open_cfw_test_flashdb_oracle_status != 0) {
        return -1;
    }
    for (index = 0U; index < size; index++) {
        buffer[index] = (uint8_t)(((uint32_t)offset + (uint32_t)index) ^ 0xA5U);
    }
    return (int)size;
}

static int open_cfw_test_flashdb_oracle_write(
    long offset,
    const uint8_t *buffer,
    size_t size
)
{
    (void)offset;
    (void)buffer;
    (void)size;
    return -1;
}

static int open_cfw_test_flashdb_oracle_erase(long offset, size_t size)
{
    (void)offset;
    (void)size;
    return -1;
}

void open_cfw_test_flashdb_oracle_reset(int status)
{
    open_cfw_test_flashdb_oracle_status = status;
    open_cfw_test_flashdb_oracle_calls = 0U;
    open_cfw_test_flashdb_oracle_last_offset = 0U;
    open_cfw_test_flashdb_oracle_last_size = 0U;
    (void)fal_partition_init();
}

int open_cfw_test_flashdb_oracle_partition_read(
    unsigned int partition,
    unsigned int address,
    unsigned char *buffer,
    unsigned int size
)
{
    const struct fal_partition *part;

    if (partition > 1U) {
        return -1;
    }
    part = fal_partition_find(partition == 0U ? "kvdb" : "NVdb");
    if (part == (const struct fal_partition *)0) {
        return -1;
    }
    return fal_partition_read(part, address, buffer, size);
}

unsigned int open_cfw_test_flashdb_oracle_counter(unsigned int index)
{
    switch (index) {
    case 0U:
        return open_cfw_test_flashdb_oracle_calls;
    case 1U:
        return open_cfw_test_flashdb_oracle_last_offset;
    case 2U:
        return open_cfw_test_flashdb_oracle_last_size;
    default:
        return 0U;
    }
}
