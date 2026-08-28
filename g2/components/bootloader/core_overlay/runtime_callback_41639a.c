/* SPDX-License-Identifier: MIT */

typedef __UINTPTR_TYPE__ open_cfw_bootloader_word;

typedef void (*open_cfw_bootloader_callback)(open_cfw_bootloader_word);

typedef struct {
    open_cfw_bootloader_callback callback;
    open_cfw_bootloader_word argument;
} open_cfw_bootloader_callback_record;

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_CALLBACK_RECORD_4196C2
extern open_cfw_bootloader_word
open_cfw_bootloader_runtime_callback_record_4196c2(
    open_cfw_bootloader_word owner
);
#define OPEN_CFW_BOOTLOADER_RUNTIME_CALLBACK_RECORD_4196C2(owner) \
    open_cfw_bootloader_runtime_callback_record_4196c2(owner)
#endif

__attribute__((used, noinline))
void open_cfw_bootloader_runtime_callback_41639a(
    open_cfw_bootloader_word owner
)
{
    open_cfw_bootloader_word address =
        OPEN_CFW_BOOTLOADER_RUNTIME_CALLBACK_RECORD_4196C2(owner);
    const open_cfw_bootloader_callback_record *record;

    address &= ~(open_cfw_bootloader_word)1U;
    if (address == 0U) {
        return;
    }

    record = (const open_cfw_bootloader_callback_record *)address;
    record->callback(record->argument);
}
