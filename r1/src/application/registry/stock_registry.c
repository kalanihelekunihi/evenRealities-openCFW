/* Native entry contracts: 0x85CE0 lookup and 0x85D58 registration.
 * Typed records come from the existing recovered-layout header. This module
 * preserves fixed-head storage and stock validation order; it does not add
 * fault-path hardening. String comparison remains an attributed runtime seam. */
#include <stddef.h>
#include "stock_registry.h"
extern int strcmp(const char *left, const char *right);

generic_device_registry_device *r1_stock_registry_head
    __attribute__((section(".r1.registry.head"), aligned(4)));

_Static_assert(offsetof(generic_device_registry_device, ops) == 4, "stock ops offset");
_Static_assert(offsetof(generic_device_registry_device, next) == 20, "stock next offset");
_Static_assert(sizeof(generic_device_registry_device) == 24, "stock record extent");

generic_device_registry_device *r1_stock_registry_find(const char *name) {
    for (generic_device_registry_device *record = r1_stock_registry_head;
         record != NULL; record = record->next) {
        if (strcmp(record->name, name) == 0)
            return record;
    }
    return NULL;
}

uint32_t r1_stock_registry_register(generic_device_registry_device *record) {
    if (record == NULL)
        return 0;
    /* Stock checks duplicates before validating the new record's name/ops. */
    for (generic_device_registry_device *item = r1_stock_registry_head;
         item != NULL; item = item->next) {
        if (strcmp(item->name, record->name) == 0)
            return 0;
    }
    if (record->name == NULL || record->ops == NULL)
        return 0;
    if (r1_stock_registry_head == NULL) {
        r1_stock_registry_head = record;
    } else {
        generic_device_registry_device *tail = r1_stock_registry_head;
        while (tail->next != NULL)
            tail = tail->next;
        tail->next = record;
    }
    record->next = NULL;
    return 1;
}

/* Do not add a NULL-table fallback: the native image dereferences the table.
 * Narrow prototypes reflect which argument registers stock actually preserves. */
typedef uint32_t (*device_op)(generic_device_registry_device *);
typedef uint32_t (*device_words_op)(generic_device_registry_device *, uintptr_t, uintptr_t);
typedef struct {
    device_op slot_00;
    uintptr_t reserved_04;
    device_op slot_08, slot_0c;
    generic_device_registry_operation slot_10, slot_14;
    device_words_op slot_18;
    uintptr_t reserved_1c;
    device_words_op slot_20;
} native_ops;
_Static_assert(sizeof(native_ops) == 36, "native nine-word operations");
#define DEVICE_DISPATCH(suffix, index, missing) \
uint32_t r1_stock_dispatch_##suffix(generic_device_registry_device *device) { \
    if (device == NULL) return 1; \
    device_op operation = ((const native_ops *)device->ops)->slot_##suffix; \
    return operation != NULL ? operation(device) : missing; \
}
DEVICE_DISPATCH(00, 0, 5)
DEVICE_DISPATCH(08, 2, 5)
DEVICE_DISPATCH(0c, 3, 6)
#define WORDS_DISPATCH(suffix, index, missing) \
uint32_t r1_stock_dispatch_##suffix(generic_device_registry_device *device, uintptr_t a, uintptr_t b) { \
    if (device == NULL) return 1; \
    device_words_op operation = ((const native_ops *)device->ops)->slot_##suffix; \
    return operation != NULL ? operation(device, a, b) : missing; \
}
WORDS_DISPATCH(18, 6, 7)
WORDS_DISPATCH(20, 8, 9)
#define REQUEST_DISPATCH(suffix, index, missing) \
uint32_t r1_stock_dispatch_##suffix(generic_device_registry_device *device, uintptr_t a, uintptr_t b, uintptr_t c) { \
    if (device == NULL) return 1; \
    generic_device_registry_operation operation = device->ops->slot[index]; \
    return operation != NULL ? operation(device, a, b, c) : missing; \
}
REQUEST_DISPATCH(10, 4, 2)
REQUEST_DISPATCH(14, 5, 3)
