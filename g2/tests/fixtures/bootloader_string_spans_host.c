#include "../../components/bootloader/core_overlay/runtime_strcspn.c"
#include "../../components/bootloader/core_overlay/runtime_strspn.c"

open_cfw_bootloader_span_size open_cfw_bootloader_strcspn_fixture(
    const char *string,
    const char *reject
)
{
    return open_cfw_bootloader_strcspn(string, reject);
}

open_cfw_bootloader_span_size open_cfw_bootloader_strspn_fixture(
    const char *string,
    const char *accept
)
{
    return open_cfw_bootloader_strspn(string, accept);
}
