/* SPDX-License-Identifier: MIT */

typedef __UINTPTR_TYPE__ open_cfw_bootloader_word;

typedef struct {
    open_cfw_bootloader_word name;
    open_cfw_bootloader_word attributes;
    open_cfw_bootloader_word storage;
    open_cfw_bootloader_word storage_size;
} open_cfw_bootloader_semaphore_create_config;

#ifndef OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT
extern open_cfw_bootloader_word open_cfw_bootloader_critical_context(void);
#define OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() open_cfw_bootloader_critical_context()
#endif

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_BINARY_STATIC_419C9C
extern open_cfw_bootloader_word open_cfw_bootloader_runtime_binary_static_419c9c(
    open_cfw_bootloader_word length, open_cfw_bootloader_word item_size,
    open_cfw_bootloader_word buffer, open_cfw_bootloader_word storage,
    open_cfw_bootloader_word kind);
#define OPEN_CFW_BOOTLOADER_RUNTIME_BINARY_STATIC_419C9C(length, item_size, buffer, storage, kind) \
    open_cfw_bootloader_runtime_binary_static_419c9c(length, item_size, buffer, storage, kind)
#endif

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_BINARY_DYNAMIC_419D08
extern open_cfw_bootloader_word open_cfw_bootloader_runtime_binary_dynamic_419d08(
    open_cfw_bootloader_word length, open_cfw_bootloader_word item_size,
    open_cfw_bootloader_word kind);
#define OPEN_CFW_BOOTLOADER_RUNTIME_BINARY_DYNAMIC_419D08(length, item_size, kind) \
    open_cfw_bootloader_runtime_binary_dynamic_419d08(length, item_size, kind)
#endif

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_SEMAPHORE_STATIC_419E62
extern open_cfw_bootloader_word open_cfw_bootloader_runtime_semaphore_static_419e62(
    open_cfw_bootloader_word maximum, open_cfw_bootloader_word initial,
    open_cfw_bootloader_word storage);
#define OPEN_CFW_BOOTLOADER_RUNTIME_SEMAPHORE_STATIC_419E62(maximum, initial, storage) \
    open_cfw_bootloader_runtime_semaphore_static_419e62(maximum, initial, storage)
#endif

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_SEMAPHORE_DYNAMIC_419E94
extern open_cfw_bootloader_word open_cfw_bootloader_runtime_semaphore_dynamic_419e94(
    open_cfw_bootloader_word maximum, open_cfw_bootloader_word initial);
#define OPEN_CFW_BOOTLOADER_RUNTIME_SEMAPHORE_DYNAMIC_419E94(maximum, initial) \
    open_cfw_bootloader_runtime_semaphore_dynamic_419e94(maximum, initial)
#endif

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_HANDLE_RELEASE_PLAIN_419EC0
extern open_cfw_bootloader_word open_cfw_bootloader_runtime_handle_release_plain_419ec0(
    open_cfw_bootloader_word object, open_cfw_bootloader_word first,
    open_cfw_bootloader_word second, open_cfw_bootloader_word third);
#define OPEN_CFW_BOOTLOADER_RUNTIME_HANDLE_RELEASE_PLAIN_419EC0(object, first, second, third) \
    open_cfw_bootloader_runtime_handle_release_plain_419ec0(object, first, second, third)
#endif

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_SEMAPHORE_DELETE_41A470
extern void open_cfw_bootloader_runtime_semaphore_delete_41a470(open_cfw_bootloader_word object);
#define OPEN_CFW_BOOTLOADER_RUNTIME_SEMAPHORE_DELETE_41A470(object) \
    open_cfw_bootloader_runtime_semaphore_delete_41a470(object)
#endif

__attribute__((used, noinline))
open_cfw_bootloader_word open_cfw_bootloader_runtime_semaphore_create_416762(
    open_cfw_bootloader_word maximum,
    open_cfw_bootloader_word initial,
    const open_cfw_bootloader_semaphore_create_config *config)
{
    open_cfw_bootloader_word mode;
    open_cfw_bootloader_word result = 0U;

    if (OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() != 0U || maximum == 0U || maximum < initial) {
        return 0U;
    }
    if (config == (const open_cfw_bootloader_semaphore_create_config *)0) {
        mode = 0U;
    } else if (config->storage != 0U && config->storage_size >= 80U) {
        mode = 1U;
    } else if (config->storage == 0U && config->storage_size == 0U) {
        mode = 0U;
    } else {
        return 0U;
    }

    if (maximum == 1U) {
        result = mode != 0U
            ? OPEN_CFW_BOOTLOADER_RUNTIME_BINARY_STATIC_419C9C(1U, 0U, 0U, config->storage, 3U)
            : OPEN_CFW_BOOTLOADER_RUNTIME_BINARY_DYNAMIC_419D08(1U, 0U, 3U);
        if (result != 0U && initial != 0U &&
            OPEN_CFW_BOOTLOADER_RUNTIME_HANDLE_RELEASE_PLAIN_419EC0(result, 0U, 0U, 0U) != 1U) {
            OPEN_CFW_BOOTLOADER_RUNTIME_SEMAPHORE_DELETE_41A470(result);
            result = 0U;
        }
    } else {
        result = mode != 0U
            ? OPEN_CFW_BOOTLOADER_RUNTIME_SEMAPHORE_STATIC_419E62(maximum, initial, config->storage)
            : OPEN_CFW_BOOTLOADER_RUNTIME_SEMAPHORE_DYNAMIC_419E94(maximum, initial);
    }
    return result;
}
