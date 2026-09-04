/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room implementation of the G2 teleprompt file-list storage object.
 * Schema decoding belongs to its caller; this object only owns an exact-size
 * record and provides copy, live-address, and reset operations.
 */
#include "teleprompt_file_list.h"

#define OPEN_CFW_STATIC_ASSERT(name, condition) \
    typedef char open_cfw_static_assert_##name[(condition) ? 1 : -1]

OPEN_CFW_STATIC_ASSERT(
    teleprompt_file_list_size,
    sizeof(open_cfw_teleprompt_file_list) ==
        OPEN_CFW_TELEPROMPT_FILE_LIST_BYTES
);

#ifndef OPEN_CFW_TELEPROMPT_FILE_LIST_RECORD
#define OPEN_CFW_TELEPROMPT_FILE_LIST_RECORD \
    (*(open_cfw_teleprompt_file_list *)0x201093D4U)
#endif

#ifndef OPEN_CFW_TELEPROMPT_FILE_LIST_MEMCPY
void *open_cfw_teleprompt_file_list_memcpy(
    void *destination, const void *source, uint32_t size
);
#define OPEN_CFW_TELEPROMPT_FILE_LIST_MEMCPY(destination, source, size) \
    open_cfw_teleprompt_file_list_memcpy((destination), (source), (size))
#endif

#ifndef OPEN_CFW_TELEPROMPT_FILE_LIST_MEMSET
void *open_cfw_teleprompt_file_list_memset(
    void *destination, int value, uint32_t size
);
#define OPEN_CFW_TELEPROMPT_FILE_LIST_MEMSET(destination, value, size) \
    open_cfw_teleprompt_file_list_memset((destination), (value), (size))
#endif

#if defined(OPEN_CFW_TELEPROMPT_FILE_LIST_UPDATE_ONLY) || \
    (!defined(OPEN_CFW_TELEPROMPT_FILE_LIST_GET_ONLY) && \
     !defined(OPEN_CFW_TELEPROMPT_FILE_LIST_RESET_ONLY))
void open_cfw_teleprompt_file_list_update(
    const open_cfw_teleprompt_file_list *file_list
)
{
    if (file_list == (const open_cfw_teleprompt_file_list *)0) {
        return;
    }
    (void)OPEN_CFW_TELEPROMPT_FILE_LIST_MEMCPY(
        &OPEN_CFW_TELEPROMPT_FILE_LIST_RECORD,
        file_list,
        OPEN_CFW_TELEPROMPT_FILE_LIST_BYTES
    );
}
#endif

#if defined(OPEN_CFW_TELEPROMPT_FILE_LIST_GET_ONLY) || \
    (!defined(OPEN_CFW_TELEPROMPT_FILE_LIST_UPDATE_ONLY) && \
     !defined(OPEN_CFW_TELEPROMPT_FILE_LIST_RESET_ONLY))
open_cfw_teleprompt_file_list *open_cfw_teleprompt_file_list_get(void)
{
    return &OPEN_CFW_TELEPROMPT_FILE_LIST_RECORD;
}
#endif

#if defined(OPEN_CFW_TELEPROMPT_FILE_LIST_RESET_ONLY) || \
    (!defined(OPEN_CFW_TELEPROMPT_FILE_LIST_UPDATE_ONLY) && \
     !defined(OPEN_CFW_TELEPROMPT_FILE_LIST_GET_ONLY))
void open_cfw_teleprompt_file_list_reset(void)
{
    (void)OPEN_CFW_TELEPROMPT_FILE_LIST_MEMSET(
        &OPEN_CFW_TELEPROMPT_FILE_LIST_RECORD,
        0,
        OPEN_CFW_TELEPROMPT_FILE_LIST_BYTES
    );
}
#endif
