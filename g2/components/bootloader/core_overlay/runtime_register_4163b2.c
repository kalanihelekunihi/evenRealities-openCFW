/* SPDX-License-Identifier: MIT */

typedef __UINTPTR_TYPE__ open_cfw_bootloader_word;
typedef unsigned char open_cfw_bootloader_u8;

typedef struct {
    open_cfw_bootloader_word handle;
    open_cfw_bootloader_word reserved;
    open_cfw_bootloader_word storage;
    open_cfw_bootloader_word storage_size;
} open_cfw_bootloader_registration_config;

typedef struct {
    open_cfw_bootloader_word owner;
    open_cfw_bootloader_word argument;
} open_cfw_bootloader_callback_record;

#ifndef OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT
extern open_cfw_bootloader_word open_cfw_bootloader_critical_context(void);
#define OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() \
    open_cfw_bootloader_critical_context()
#endif

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_ALLOC_419730
extern open_cfw_bootloader_word open_cfw_bootloader_runtime_alloc_419730(
    open_cfw_bootloader_word size
);
#define OPEN_CFW_BOOTLOADER_RUNTIME_ALLOC_419730(size) \
    open_cfw_bootloader_runtime_alloc_419730(size)
#endif

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_FREE_419830
extern void open_cfw_bootloader_runtime_free_419830(
    open_cfw_bootloader_word address
);
#define OPEN_CFW_BOOTLOADER_RUNTIME_FREE_419830(address) \
    open_cfw_bootloader_runtime_free_419830(address)
#endif

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_REGISTER_STATIC_4192DE
extern open_cfw_bootloader_word
open_cfw_bootloader_runtime_register_static_4192de(
    open_cfw_bootloader_word handle,
    open_cfw_bootloader_word count,
    open_cfw_bootloader_word option,
    open_cfw_bootloader_word tagged_record,
    open_cfw_bootloader_word callback,
    open_cfw_bootloader_word storage
);
#define OPEN_CFW_BOOTLOADER_RUNTIME_REGISTER_STATIC_4192DE( \
    handle, count, option, tagged_record, callback, storage) \
    open_cfw_bootloader_runtime_register_static_4192de( \
        handle, count, option, tagged_record, callback, storage)
#endif

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_REGISTER_DYNAMIC_4192A8
extern open_cfw_bootloader_word
open_cfw_bootloader_runtime_register_dynamic_4192a8(
    open_cfw_bootloader_word handle,
    open_cfw_bootloader_word count,
    open_cfw_bootloader_word option,
    open_cfw_bootloader_word tagged_record,
    open_cfw_bootloader_word callback
);
#define OPEN_CFW_BOOTLOADER_RUNTIME_REGISTER_DYNAMIC_4192A8( \
    handle, count, option, tagged_record, callback) \
    open_cfw_bootloader_runtime_register_dynamic_4192a8( \
        handle, count, option, tagged_record, callback)
#endif

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_CALLBACK_41639B
#define OPEN_CFW_BOOTLOADER_RUNTIME_CALLBACK_41639B \
    ((open_cfw_bootloader_word)0x0041639BU)
#endif

__attribute__((used, noinline))
open_cfw_bootloader_word open_cfw_bootloader_runtime_register_4163b2(
    open_cfw_bootloader_word owner,
    open_cfw_bootloader_word option,
    open_cfw_bootloader_word argument,
    const open_cfw_bootloader_registration_config *config
)
{
    open_cfw_bootloader_callback_record *record =
        (open_cfw_bootloader_callback_record *)0;
    open_cfw_bootloader_word allocated = 0U;
    open_cfw_bootloader_word handle = 0U;
    open_cfw_bootloader_word mode = ~(open_cfw_bootloader_word)0U;
    open_cfw_bootloader_word result = 0U;
    open_cfw_bootloader_word tagged_record;

    if (OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() != 0U || owner == 0U) {
        return 0U;
    }

    if (config != (const open_cfw_bootloader_registration_config *)0
        && config->storage != 0U
        && config->storage_size >= 52U) {
        record = (open_cfw_bootloader_callback_record *)(config->storage + 44U);
    }
    if (record == (open_cfw_bootloader_callback_record *)0) {
        open_cfw_bootloader_word address =
            OPEN_CFW_BOOTLOADER_RUNTIME_ALLOC_419730(8U);
        if (address != 0U) {
            record = (open_cfw_bootloader_callback_record *)address;
            allocated = 1U;
        }
    }
    if (record == (open_cfw_bootloader_callback_record *)0) {
        return 0U;
    }

    record->owner = owner;
    record->argument = argument;
    if (config == (const open_cfw_bootloader_registration_config *)0) {
        mode = 0U;
    } else {
        handle = config->handle;
        if (config->storage != 0U && config->storage_size >= 44U) {
            mode = 1U;
        } else if (config->storage == 0U && config->storage_size == 0U) {
            mode = 0U;
        }
    }

    tagged_record = (open_cfw_bootloader_word)record | allocated;
    if (mode == 1U) {
        result = OPEN_CFW_BOOTLOADER_RUNTIME_REGISTER_STATIC_4192DE(
            handle,
            1U,
            (open_cfw_bootloader_word)((open_cfw_bootloader_u8)option != 0U),
            tagged_record,
            OPEN_CFW_BOOTLOADER_RUNTIME_CALLBACK_41639B,
            config->storage
        );
    } else if (mode == 0U) {
        result = OPEN_CFW_BOOTLOADER_RUNTIME_REGISTER_DYNAMIC_4192A8(
            handle,
            1U,
            (open_cfw_bootloader_word)((open_cfw_bootloader_u8)option != 0U),
            tagged_record,
            OPEN_CFW_BOOTLOADER_RUNTIME_CALLBACK_41639B
        );
    }

    if (result == 0U && allocated != 0U) {
        OPEN_CFW_BOOTLOADER_RUNTIME_FREE_419830(
            tagged_record & ~(open_cfw_bootloader_word)1U
        );
    }
    return result;
}
