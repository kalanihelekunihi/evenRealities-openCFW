#ifndef R1_NATIVE_TOUCH_READY_STATE_H
#define R1_NATIVE_TOUCH_READY_STATE_H
#include <stdint.h>
#include <stddef.h>
struct generic_device_registry_device;
/* Native adjacent words 20006804/20006808. Four-byte alignment matches the
 * stock LDRD address; this is instruction grouping, not a C11 atomic object. */
union __attribute__((packed,aligned(4))) r1_touch_ready_store {
    struct {
        struct generic_device_registry_device *input;
        uintptr_t callback;
    } fields;
    uint64_t words;
};
_Static_assert(sizeof(union r1_touch_ready_store)==8 &&
               _Alignof(union r1_touch_ready_store)==4 &&
               offsetof(union r1_touch_ready_store,fields.callback)==4,
               "native ready input/callback pair");
_Static_assert(__BYTE_ORDER__==__ORDER_LITTLE_ENDIAN__,"native word ordering");
extern volatile union r1_touch_ready_store r1_touch_ready_storage;
#define r1_touch_input_device (r1_touch_ready_storage.fields.input)
#define r1_touch_ready_callback_word (r1_touch_ready_storage.fields.callback)
#endif
