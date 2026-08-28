/* SPDX-License-Identifier: MIT */

typedef __UINTPTR_TYPE__ open_cfw_bootloader_word;

typedef struct {
    open_cfw_bootloader_word name;
    open_cfw_bootloader_word attributes;
    open_cfw_bootloader_word storage;
    open_cfw_bootloader_word storage_size;
} open_cfw_bootloader_flags_create_config;

#ifndef OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT
extern open_cfw_bootloader_word open_cfw_bootloader_critical_context(void);
#define OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() \
    open_cfw_bootloader_critical_context()
#endif

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_FLAGS_CREATE_STATIC_419DC2
extern open_cfw_bootloader_word open_cfw_bootloader_runtime_flags_create_static_419dc2(
    open_cfw_bootloader_word kind,
    open_cfw_bootloader_word storage
);
#define OPEN_CFW_BOOTLOADER_RUNTIME_FLAGS_CREATE_STATIC_419DC2(kind, storage) \
    open_cfw_bootloader_runtime_flags_create_static_419dc2(kind, storage)
#endif

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_FLAGS_CREATE_DYNAMIC_419DA8
extern open_cfw_bootloader_word open_cfw_bootloader_runtime_flags_create_dynamic_419da8(
    open_cfw_bootloader_word kind
);
#define OPEN_CFW_BOOTLOADER_RUNTIME_FLAGS_CREATE_DYNAMIC_419DA8(kind) \
    open_cfw_bootloader_runtime_flags_create_dynamic_419da8(kind)
#endif

__attribute__((used, noinline))
open_cfw_bootloader_word open_cfw_bootloader_runtime_flags_create_416610(
    const open_cfw_bootloader_flags_create_config *config
)
{
    open_cfw_bootloader_word attributes = 0U;
    open_cfw_bootloader_word tagged = 0U;
    open_cfw_bootloader_word mode = ~(open_cfw_bootloader_word)0U;
    open_cfw_bootloader_word result = 0U;
    open_cfw_bootloader_word kind;

    if (OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() != 0U) {
        return 0U;
    }
    if (config != (const open_cfw_bootloader_flags_create_config *)0) {
        attributes = config->attributes;
    }
    tagged = attributes & 1U;
    if ((attributes & 8U) != 0U) {
        return 0U;
    }

    if (config == (const open_cfw_bootloader_flags_create_config *)0) {
        mode = 0U;
    } else if (config->storage != 0U && config->storage_size >= 80U) {
        mode = 1U;
    } else if (config->storage == 0U && config->storage_size == 0U) {
        mode = 0U;
    }

    kind = tagged != 0U ? 4U : 1U;
    if (mode == 1U) {
        result = OPEN_CFW_BOOTLOADER_RUNTIME_FLAGS_CREATE_STATIC_419DC2(
            kind, config->storage
        );
    } else if (mode == 0U) {
        result = OPEN_CFW_BOOTLOADER_RUNTIME_FLAGS_CREATE_DYNAMIC_419DA8(kind);
    }
    if (result != 0U && tagged != 0U) {
        result |= 1U;
    }
    return result;
}
