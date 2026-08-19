/*
 * Source-built, power-loss recoverable BLE loader for the R1.
 *
 * The loader is linked into MCUboot, below the application partition.  It
 * only writes image-0, never its own partition or product storage.  MCUboot
 * validates the normal signed-image header and signature after reset; an
 * interrupted or invalid upload therefore returns here instead of executing.
 */

#include <errno.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include <bootutil/mcuboot_status.h>
#include <mcuboot_config/mcuboot_config.h>
#include <hal/nrf_power.h>
#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/bluetooth/gatt.h>
#include <zephyr/bluetooth/uuid.h>
#include <zephyr/drivers/flash.h>
#include <zephyr/kernel.h>
#include <zephyr/storage/flash_map.h>
#include <zephyr/sys/byteorder.h>
#include <zephyr/sys/reboot.h>

#define OPENR1_RECOVERY_REQUEST UINT8_C(0xb1)
#define OPENR1_RECOVERY_BLOCK_BYTES 256u
#define OPENR1_RECOVERY_PAGE_BYTES 4096u
#define OPENR1_RECOVERY_STATUS_BYTES 12u

enum openr1_recovery_state {
    OPENR1_RECOVERY_IDLE = 0,
    OPENR1_RECOVERY_RECEIVING = 1,
    OPENR1_RECOVERY_COMPLETE = 2,
    OPENR1_RECOVERY_FAILED = 3,
};

enum openr1_recovery_operation {
    OPENR1_RECOVERY_START = 1,
    OPENR1_RECOVERY_FINISH = 2,
    OPENR1_RECOVERY_ABORT = 3,
};

static struct bt_uuid_128 recovery_service_uuid = BT_UUID_INIT_128(
    BT_UUID_128_ENCODE(0x8fce0001, 0x4a7d, 0x4f9f, 0xa83d,
                       0x62f359a104d1));
static struct bt_uuid_128 recovery_control_uuid = BT_UUID_INIT_128(
    BT_UUID_128_ENCODE(0x8fce0010, 0x4a7d, 0x4f9f, 0xa83d,
                       0x62f359a104d1));
static struct bt_uuid_128 recovery_data_uuid = BT_UUID_INIT_128(
    BT_UUID_128_ENCODE(0x8fce0011, 0x4a7d, 0x4f9f, 0xa83d,
                       0x62f359a104d1));
static struct bt_uuid_128 recovery_status_uuid = BT_UUID_INIT_128(
    BT_UUID_128_ENCODE(0x8fce0012, 0x4a7d, 0x4f9f, 0xa83d,
                       0x62f359a104d1));

static const struct flash_area *image_area;
static enum openr1_recovery_state recovery_state;
static int32_t recovery_error;
static uint32_t expected_bytes;
static uint32_t received_bytes;
static uint32_t committed_bytes;
static uint8_t block[OPENR1_RECOVERY_BLOCK_BYTES];
static size_t block_length;
static bool application_region_clean;
static bool legacy_region_clean;
static bool settings_region_clean;
static struct k_work restart_advertising_work;
static struct k_work_delayable reboot_work;
K_MUTEX_DEFINE(recovery_mutex);

static const uint8_t recovery_advertising_flags[] = {
    BT_LE_AD_GENERAL | BT_LE_AD_NO_BREDR,
};
static const uint8_t recovery_advertising_uuid[] = {
    BT_UUID_128_ENCODE(0x8fce0001, 0x4a7d, 0x4f9f, 0xa83d,
                       0x62f359a104d1),
};
static const uint8_t recovery_advertising_name[] = "OPENR1-RECOVERY";

static void fail_locked(int error) {
    recovery_error = error == 0 ? -EIO : error;
    recovery_state = OPENR1_RECOVERY_FAILED;
}

static int clean_partition(int partition_id, bool *clean) {
    const struct flash_area *area = NULL;
    int error = flash_area_open(partition_id, &area);
    if (error != 0) {
        return error;
    }
    uint8_t probe[OPENR1_RECOVERY_BLOCK_BYTES];
    bool erased = true;
    for (uint32_t offset = 0u; erased && offset < area->fa_size;
         offset += (uint32_t)sizeof probe) {
        size_t length = area->fa_size - offset;
        if (length > sizeof probe) {
            length = sizeof probe;
        }
        error = flash_area_read(area, offset, probe, length);
        if (error != 0) {
            break;
        }
        for (size_t index = 0u; index < length; ++index) {
            if (probe[index] != UINT8_C(0xff)) {
                erased = false;
                break;
            }
        }
    }
    if (error == 0 && !erased) {
        error = flash_area_erase(area, 0u, area->fa_size);
    }
    flash_area_close(area);
    *clean = error == 0;
    return error;
}

static int clean_opaque_regions(void) {
    int error = application_region_clean ? 0 : clean_partition(
        FIXED_PARTITION_ID(slot0_partition),
        &application_region_clean);
    if (error == 0 && !legacy_region_clean) {
        error = clean_partition(
        FIXED_PARTITION_ID(migration_reserve_partition),
        &legacy_region_clean);
    }
    if (error == 0 && !settings_region_clean) {
        error = clean_partition(
            FIXED_PARTITION_ID(settings_partition),
            &settings_region_clean);
    }
    return error;
}

static int erase_for_range(uint32_t offset, size_t length) {
    const size_t page_size = OPENR1_RECOVERY_PAGE_BYTES;
    const uint32_t first = offset - offset % page_size;
    const uint32_t end = (uint32_t)(offset + length);
    for (uint32_t page = first; page < end; page += (uint32_t)page_size) {
        if (page < committed_bytes || page >= image_area->fa_size) {
            continue;
        }
        const int error = flash_area_erase(image_area, page, page_size);
        if (error != 0) {
            return error;
        }
    }
    return 0;
}

static int flush_block_locked(bool final) {
    if (block_length == 0u) {
        return 0;
    }
    size_t write_length = block_length;
    if (final) {
        write_length = (write_length + 3u) & ~(size_t)3u;
        memset(block + block_length, 0xff, write_length - block_length);
    } else if (write_length != sizeof block) {
        return -EINVAL;
    }
    if (committed_bytes > image_area->fa_size ||
        write_length > image_area->fa_size - committed_bytes) {
        return -EFBIG;
    }
    int error = erase_for_range(committed_bytes, write_length);
    if (error == 0) {
        error = flash_area_write(
            image_area, committed_bytes, block, write_length);
    }
    if (error == 0) {
        application_region_clean = false;
        committed_bytes += (uint32_t)write_length;
        block_length = 0u;
    }
    return error;
}

static ssize_t read_status(
    struct bt_conn *connection, const struct bt_gatt_attr *attribute,
    void *buffer, uint16_t length, uint16_t offset) {
    uint8_t status[OPENR1_RECOVERY_STATUS_BYTES];
    if (k_mutex_lock(&recovery_mutex, K_FOREVER) != 0) {
        return BT_GATT_ERR(BT_ATT_ERR_UNLIKELY);
    }
    status[0] = (uint8_t)recovery_state;
    status[1] = recovery_error == 0 ? 0u : (uint8_t)(-recovery_error);
    status[2] = 0u;
    status[3] = 0u;
    sys_put_le32(received_bytes, &status[4]);
    sys_put_le32(expected_bytes, &status[8]);
    (void)k_mutex_unlock(&recovery_mutex);
    return bt_gatt_attr_read(
        connection, attribute, buffer, length, offset,
        status, sizeof status);
}

static ssize_t write_control(
    struct bt_conn *connection, const struct bt_gatt_attr *attribute,
    const void *buffer, uint16_t length, uint16_t offset, uint8_t flags) {
    (void)connection;
    (void)attribute;
    (void)flags;
    if (offset != 0u || buffer == NULL || length == 0u) {
        return BT_GATT_ERR(BT_ATT_ERR_INVALID_OFFSET);
    }
    const uint8_t *bytes = buffer;
    if (k_mutex_lock(&recovery_mutex, K_FOREVER) != 0) {
        return BT_GATT_ERR(BT_ATT_ERR_UNLIKELY);
    }
    int error = 0;
    switch (bytes[0]) {
        case OPENR1_RECOVERY_START:
            if (length != 5u) {
                error = -EMSGSIZE;
                break;
            }
            expected_bytes = sys_get_le32(&bytes[1]);
            if (expected_bytes == 0u || image_area == NULL ||
                expected_bytes > image_area->fa_size) {
                error = -EFBIG;
                break;
            }
            error = clean_opaque_regions();
            if (error != 0) {
                break;
            }
            recovery_state = OPENR1_RECOVERY_RECEIVING;
            recovery_error = 0;
            received_bytes = 0u;
            committed_bytes = 0u;
            block_length = 0u;
            memset(block, 0xff, sizeof block);
            break;
        case OPENR1_RECOVERY_FINISH:
            if (length != 1u || received_bytes != expected_bytes ||
                (recovery_state != OPENR1_RECOVERY_RECEIVING &&
                 recovery_state != OPENR1_RECOVERY_COMPLETE)) {
                error = -EINVAL;
                break;
            }
            error = recovery_state == OPENR1_RECOVERY_COMPLETE ? 0 :
                flush_block_locked(true);
            if (error == 0) {
                recovery_state = OPENR1_RECOVERY_COMPLETE;
            }
            break;
        case OPENR1_RECOVERY_ABORT:
            if (length != 1u) {
                error = -EMSGSIZE;
                break;
            }
            recovery_state = OPENR1_RECOVERY_IDLE;
            recovery_error = 0;
            expected_bytes = 0u;
            received_bytes = 0u;
            committed_bytes = 0u;
            block_length = 0u;
            break;
        default:
            error = -ENOTSUP;
            break;
    }
    if (error != 0) {
        fail_locked(error);
    }
    const bool reboot = error == 0 && bytes[0] == OPENR1_RECOVERY_FINISH;
    (void)k_mutex_unlock(&recovery_mutex);
    if (reboot) {
        (void)k_work_reschedule(&reboot_work, K_MSEC(250));
    }
    return error == 0 ? (ssize_t)length : BT_GATT_ERR(BT_ATT_ERR_VALUE_NOT_ALLOWED);
}

static ssize_t write_data(
    struct bt_conn *connection, const struct bt_gatt_attr *attribute,
    const void *buffer, uint16_t length, uint16_t offset, uint8_t flags) {
    (void)connection;
    (void)attribute;
    (void)flags;
    if (offset != 0u || buffer == NULL || length <= 4u) {
        return BT_GATT_ERR(BT_ATT_ERR_INVALID_ATTRIBUTE_LEN);
    }
    const uint8_t *bytes = buffer;
    const uint32_t packet_offset = sys_get_le32(bytes);
    const size_t payload_length = (size_t)length - 4u;
    if (k_mutex_lock(&recovery_mutex, K_FOREVER) != 0) {
        return BT_GATT_ERR(BT_ATT_ERR_UNLIKELY);
    }
    int error = 0;
    if (recovery_state != OPENR1_RECOVERY_RECEIVING ||
        packet_offset != received_bytes ||
        payload_length > expected_bytes - received_bytes) {
        error = -EINVAL;
    }
    size_t consumed = 0u;
    while (error == 0 && consumed < payload_length) {
        const size_t space = sizeof block - block_length;
        const size_t remaining = payload_length - consumed;
        const size_t copy = remaining < space ? remaining : space;
        memcpy(block + block_length, bytes + 4u + consumed, copy);
        block_length += copy;
        received_bytes += (uint32_t)copy;
        consumed += copy;
        if (block_length == sizeof block) {
            error = flush_block_locked(false);
        }
    }
    if (error != 0) {
        fail_locked(error);
    }
    (void)k_mutex_unlock(&recovery_mutex);
    return error == 0 ? (ssize_t)length : BT_GATT_ERR(BT_ATT_ERR_VALUE_NOT_ALLOWED);
}

BT_GATT_SERVICE_DEFINE(openr1_recovery_service,
    BT_GATT_PRIMARY_SERVICE(&recovery_service_uuid.uuid),
    BT_GATT_CHARACTERISTIC(&recovery_control_uuid.uuid,
        BT_GATT_CHRC_WRITE, BT_GATT_PERM_WRITE,
        NULL, write_control, NULL),
    BT_GATT_CHARACTERISTIC(&recovery_data_uuid.uuid,
        BT_GATT_CHRC_WRITE | BT_GATT_CHRC_WRITE_WITHOUT_RESP,
        BT_GATT_PERM_WRITE, NULL, write_data, NULL),
    BT_GATT_CHARACTERISTIC(&recovery_status_uuid.uuid,
        BT_GATT_CHRC_READ, BT_GATT_PERM_READ,
        read_status, NULL, NULL));

static int start_recovery_advertising(void) {
    const struct bt_data advertising[] = {
        BT_DATA(BT_DATA_FLAGS, recovery_advertising_flags,
                sizeof recovery_advertising_flags),
        BT_DATA(BT_DATA_UUID128_ALL, recovery_advertising_uuid,
                sizeof recovery_advertising_uuid),
    };
    const struct bt_data scan_response[] = {
        BT_DATA(BT_DATA_NAME_COMPLETE, recovery_advertising_name,
                sizeof recovery_advertising_name - 1u),
    };
    return bt_le_adv_start(
        BT_LE_ADV_PARAM(BT_LE_ADV_OPT_CONNECTABLE,
                        BT_GAP_ADV_FAST_INT_MIN_1,
                        BT_GAP_ADV_FAST_INT_MAX_1, NULL),
        advertising, ARRAY_SIZE(advertising),
        scan_response, ARRAY_SIZE(scan_response));
}

static void restart_advertising(struct k_work *work) {
    (void)work;
    (void)start_recovery_advertising();
}

static void reboot_after_finish(struct k_work *work) {
    (void)work;
    sys_reboot(SYS_REBOOT_COLD);
}

static void recovery_disconnected(
    struct bt_conn *connection, uint8_t reason) {
    (void)connection;
    (void)reason;
    (void)k_work_submit(&restart_advertising_work);
}

BT_CONN_CB_DEFINE(openr1_recovery_connection_callbacks) = {
    .disconnected = recovery_disconnected,
};

static void recovery_run(void) {
    recovery_state = OPENR1_RECOVERY_IDLE;
    recovery_error = flash_area_open(
        FIXED_PARTITION_ID(slot0_partition), &image_area);
    if (recovery_error != 0) {
        recovery_state = OPENR1_RECOVERY_FAILED;
    }
    if (recovery_error == 0) {
        recovery_error = clean_opaque_regions();
        if (recovery_error != 0) {
            recovery_state = OPENR1_RECOVERY_FAILED;
        }
    }
    k_work_init_delayable(&reboot_work, reboot_after_finish);
    int error = bt_enable(NULL);
    if (error != 0) {
        fail_locked(error);
    } else {
        k_work_init(&restart_advertising_work, restart_advertising);
        error = start_recovery_advertising();
        if (error != 0) {
            fail_locked(error);
        }
    }
    while (true) {
        MCUBOOT_WATCHDOG_FEED();
        k_sleep(K_SECONDS(1));
    }
}

void mcuboot_status_change(mcuboot_status_type_t status) {
    if (status == MCUBOOT_STATUS_STARTUP &&
        nrf_power_gpregret_get(NRF_POWER, 0u) == OPENR1_RECOVERY_REQUEST) {
        nrf_power_gpregret_set(NRF_POWER, 0u, 0u);
        recovery_run();
    }
    if (status == MCUBOOT_STATUS_NO_BOOTABLE_IMAGE_FOUND ||
        status == MCUBOOT_STATUS_BOOT_FAILED) {
        recovery_run();
    }
}
