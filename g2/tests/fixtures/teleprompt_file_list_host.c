/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

static void *host_record;
static unsigned host_copy_calls;
static unsigned host_clear_calls;

static void *host_copy(void *destination, const void *source, uint32_t size)
{
    ++host_copy_calls;
    return memcpy(destination, source, size);
}

static void *host_clear(void *destination, int value, uint32_t size)
{
    ++host_clear_calls;
    return memset(destination, value, size);
}

#define OPEN_CFW_TELEPROMPT_FILE_LIST_RECORD \
    (*(open_cfw_teleprompt_file_list *)host_record)
#define OPEN_CFW_TELEPROMPT_FILE_LIST_MEMCPY(destination, source, size) \
    host_copy((destination), (source), (size))
#define OPEN_CFW_TELEPROMPT_FILE_LIST_MEMSET(destination, value, size) \
    host_clear((destination), (value), (size))
#include "../../components/apollo_main/core_overlay/teleprompt_file_list.c"

static void require(int condition)
{
    if (!condition) {
        abort();
    }
}

int main(void)
{
    open_cfw_teleprompt_file_list live;
    open_cfw_teleprompt_file_list incoming;
    uint32_t index;

    host_record = &live;
    memset(&live, 0xA5, sizeof(live));
    open_cfw_teleprompt_file_list_update(
        (const open_cfw_teleprompt_file_list *)0
    );
    require(host_copy_calls == 0U && live.file_count == 0xA5A5U);

    incoming.file_count = 20U;
    for (index = 0U; index < OPEN_CFW_TELEPROMPT_FILE_PAYLOAD_BYTES; ++index) {
        incoming.payload[index] = (uint8_t)(index * 37U + 11U);
    }
    open_cfw_teleprompt_file_list_update(&incoming);
    require(host_copy_calls == 1U);
    require(memcmp(&live, &incoming, sizeof(live)) == 0);
    require(open_cfw_teleprompt_file_list_get() == &live);

    open_cfw_teleprompt_file_list_reset();
    require(host_clear_calls == 1U);
    for (index = 0U; index < sizeof(live); ++index) {
        require(((const uint8_t *)&live)[index] == 0U);
    }
    return 0;
}
