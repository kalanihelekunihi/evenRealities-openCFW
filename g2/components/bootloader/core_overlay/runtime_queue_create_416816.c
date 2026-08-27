/* SPDX-License-Identifier: GPL-3.0-or-later */
typedef __UINTPTR_TYPE__ open_cfw_bootloader_word;
typedef struct {
    open_cfw_bootloader_word name;
    open_cfw_bootloader_word attributes;
    open_cfw_bootloader_word control_storage;
    open_cfw_bootloader_word control_storage_size;
    open_cfw_bootloader_word message_storage;
    open_cfw_bootloader_word message_storage_size;
} open_cfw_bootloader_queue_create_config;
#ifndef OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT
extern open_cfw_bootloader_word open_cfw_bootloader_critical_context(void);
#define OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() open_cfw_bootloader_critical_context()
#endif
#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_QUEUE_STATIC_419C9C
extern open_cfw_bootloader_word open_cfw_bootloader_runtime_queue_static_419c9c(open_cfw_bootloader_word,open_cfw_bootloader_word,open_cfw_bootloader_word,open_cfw_bootloader_word,open_cfw_bootloader_word);
#define OPEN_CFW_BOOTLOADER_RUNTIME_QUEUE_STATIC_419C9C(count,size,messages,control,kind) open_cfw_bootloader_runtime_queue_static_419c9c((count),(size),(messages),(control),(kind))
#endif
#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_QUEUE_DYNAMIC_419D08
extern open_cfw_bootloader_word open_cfw_bootloader_runtime_queue_dynamic_419d08(open_cfw_bootloader_word,open_cfw_bootloader_word,open_cfw_bootloader_word);
#define OPEN_CFW_BOOTLOADER_RUNTIME_QUEUE_DYNAMIC_419D08(count,size,kind) open_cfw_bootloader_runtime_queue_dynamic_419d08((count),(size),(kind))
#endif
__attribute__((used,noinline))
open_cfw_bootloader_word open_cfw_bootloader_runtime_queue_create_416816(open_cfw_bootloader_word count,open_cfw_bootloader_word size,const open_cfw_bootloader_queue_create_config *config)
{
    open_cfw_bootloader_word mode;
    if (OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT()!=0U || count==0U || size==0U) return 0U;
    if (config==(const open_cfw_bootloader_queue_create_config *)0) mode=0U;
    else if (config->control_storage!=0U && config->control_storage_size>=80U && config->message_storage!=0U && config->message_storage_size>=count*size) mode=1U;
    else if (config->control_storage==0U && config->control_storage_size==0U && config->message_storage==0U && config->message_storage_size==0U) mode=0U;
    else return 0U;
    return mode!=0U
        ? OPEN_CFW_BOOTLOADER_RUNTIME_QUEUE_STATIC_419C9C(count,size,config->message_storage,config->control_storage,0U)
        : OPEN_CFW_BOOTLOADER_RUNTIME_QUEUE_DYNAMIC_419D08(count,size,0U);
}
