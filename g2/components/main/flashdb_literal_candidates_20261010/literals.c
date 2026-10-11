#include <stdint.h>

/* The database object and its 256 row initializers are a separate source
 * contract. Only these five diagnostic strings are owned in this unit. */
extern unsigned char g2_flashdb_db_rows[];

static const char module_name[] = "db.api";
static const char source_path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\flashDB\\db_api\\service_db_api.c";
static const char function_name[] = "SVC_FlashDBBlobRead";
static const char error_format[] = "get the %s value fail, len = %d\n";
static const char short_error_format[] = "[db.api]get the %s value fail, len = %d\n";

const uint32_t g2_flashdb_candidate_literals[7] = {
    (uint32_t)(uintptr_t)g2_flashdb_db_rows,
    (uint32_t)(uintptr_t)module_name,
    (uint32_t)(uintptr_t)source_path,
    (uint32_t)(uintptr_t)function_name,
    (uint32_t)(uintptr_t)error_format,
    (uint32_t)(uintptr_t)short_error_format,
    0u,
};
