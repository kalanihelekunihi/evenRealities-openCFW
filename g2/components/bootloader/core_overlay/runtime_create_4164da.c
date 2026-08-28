/* SPDX-License-Identifier: MIT */

typedef __UINTPTR_TYPE__ open_cfw_bootloader_word;

typedef struct {
    open_cfw_bootloader_word handle;
    open_cfw_bootloader_word reserved;
    open_cfw_bootloader_word storage;
    open_cfw_bootloader_word storage_size;
} open_cfw_bootloader_create_config;

#ifndef OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT
extern open_cfw_bootloader_word open_cfw_bootloader_critical_context(void);
#define OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() \
    open_cfw_bootloader_critical_context()
#endif

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_CREATE_STATIC_419978
extern open_cfw_bootloader_word open_cfw_bootloader_runtime_create_static_419978(
    open_cfw_bootloader_word storage
);
#define OPEN_CFW_BOOTLOADER_RUNTIME_CREATE_STATIC_419978(storage) \
    open_cfw_bootloader_runtime_create_static_419978(storage)
#endif

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_CREATE_DYNAMIC_4199BC
extern open_cfw_bootloader_word open_cfw_bootloader_runtime_create_dynamic_4199bc(
    void
);
#define OPEN_CFW_BOOTLOADER_RUNTIME_CREATE_DYNAMIC_4199BC() \
    open_cfw_bootloader_runtime_create_dynamic_4199bc()
#endif

__attribute__((used, noinline))
open_cfw_bootloader_word open_cfw_bootloader_runtime_create_4164da(
    const open_cfw_bootloader_create_config *config
)
{
    if (OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() != 0U) {
        return 0U;
    }

    if (config == (const open_cfw_bootloader_create_config *)0) {
        return OPEN_CFW_BOOTLOADER_RUNTIME_CREATE_DYNAMIC_4199BC();
    }
    if (config->storage != 0U && config->storage_size >= 32U) {
        return OPEN_CFW_BOOTLOADER_RUNTIME_CREATE_STATIC_419978(config->storage);
    }
    if (config->storage == 0U && config->storage_size == 0U) {
        return OPEN_CFW_BOOTLOADER_RUNTIME_CREATE_DYNAMIC_4199BC();
    }
    return 0U;
}
