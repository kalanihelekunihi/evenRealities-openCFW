#ifndef OPENR1_R1_KV_STORE_H
#define OPENR1_R1_KV_STORE_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "openr1/r1_storage.h"

#define R1_KV_PARTITION_BYTES 8192u
#define R1_KV_SECTOR_BYTES 4096u
#define R1_KV_SLOT_BYTES 2048u
#define R1_KV_SLOT_COUNT 4u
#define R1_KV_CLASS_BLOCK_BYTES 256u
#define R1_KV_CLASS_HEADER_BYTES 24u
#define R1_KV_CLASS_COUNT 7u
#define R1_KV_CLASS_PAYLOAD_MAX 124u

typedef enum {
    R1_KV_DEV_INFO = 0,
    R1_KV_BLE_MULT,
    R1_KV_HEALTH,
    R1_KV_HSYNC,
    R1_KV_POWER,
    R1_KV_NV_R1,
    R1_KV_RING_SIZE
} r1_kv_class;

typedef struct {
    r1_flash flash;
    uint8_t payloads[R1_KV_CLASS_COUNT][R1_KV_CLASS_PAYLOAD_MAX];
    uint16_t states[R1_KV_CLASS_COUNT];
    uint16_t flags[R1_KV_CLASS_COUNT];
    bool dirty[R1_KV_CLASS_COUNT];
    uint32_t generation;
    uint8_t latest_slot;
    bool has_snapshot;
    bool initialized;
} r1_kv_store;

const char *r1_kv_class_name(r1_kv_class class_id);
size_t r1_kv_class_payload_length(r1_kv_class class_id);
r1_error r1_kv_store_initialize(r1_kv_store *store, r1_flash flash);
r1_error r1_kv_store_get(const r1_kv_store *store, r1_kv_class class_id,
                         uint8_t *output, size_t capacity, size_t *length);
r1_error r1_kv_store_set(r1_kv_store *store, r1_kv_class class_id,
                         const uint8_t *payload, size_t length);
r1_error r1_kv_store_commit(r1_kv_store *store);

#endif
