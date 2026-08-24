#include <stdint.h>
#include <string.h>

typedef struct { const char *key; const void *value; uint32_t value_length; }
    open_cfw_nvdb_default_node;
typedef struct { const open_cfw_nvdb_default_node *nodes; uint32_t count; }
    open_cfw_nvdb_defaults;
#define OPEN_CFW_NVDB_TYPES_DEFINED 1

static uint8_t values[9][192];
static open_cfw_nvdb_default_node nodes[9];
static uint32_t magic;
static int init_result;
static int read_magic_result;
static int defaults_calls;
static int controls;
static int reads;
static int legacy_scans;
static int otp_result;
static uint8_t system_data[172];

static int host_read(uint32_t index, const char *key, void *value,
    uint16_t length)
{
    ++reads;
    if (index != 1u) return 0;
    if (strcmp(key, "nvMagic") == 0) {
        if (read_magic_result != 0) memcpy(value, &magic, length);
        return read_magic_result;
    }
    return 1;
}
static int host_write(uint32_t index, const char *key, const void *value,
    uint16_t length)
{ (void)index; (void)key; (void)value; (void)length; return 1; }
static void *host_get(uint32_t index) { return index == 1u ? values : 0; }
static int host_control(void *db, uint32_t command, void *argument)
{ (void)db; (void)command; (void)argument; ++controls; return 0; }
static int host_init(void *db, const char *name, const char *partition,
    const open_cfw_nvdb_defaults *defaults, void *user)
{ (void)db; (void)name; (void)partition; (void)defaults; (void)user;
  return init_result; }
static __attribute__((used)) int host_set_default(void *db)
{ (void)db; ++defaults_calls; magic = 0x55550022u; read_magic_result = 1; return 0; }
static void host_legacy_scan(void) { ++legacy_scans; }
static int host_otp_read(char *destination, uint32_t flags)
{ (void)flags; memcpy(destination, "ABCDEFGHIJKLMN", 14); return otp_result; }

#define OPEN_CFW_NVDB_DEFAULT_TABLE_ADDRESS ((uintptr_t)nodes)
#define OPEN_CFW_NVDB_SYSTEM_DATA_ADDRESS ((uintptr_t)system_data)
#define OPEN_CFW_NVDB_MAGIC_KEY "nvMagic"
#define OPEN_CFW_NVDB_SYSTEM_KEY "nvSysDt"
#define OPEN_CFW_NVDB_FACTORY_NAME "factory"
#define OPEN_CFW_NVDB_PARTITION_NAME "NVdb"
#define OPEN_CFW_NVDB_DB_READ host_read
#define OPEN_CFW_NVDB_DB_WRITE host_write
#define OPEN_CFW_NVDB_DB_GET host_get
#define OPEN_CFW_NVDB_DB_CONTROL host_control
#define OPEN_CFW_NVDB_DB_INIT host_init
#define OPEN_CFW_NVDB_DB_SET_DEFAULT host_set_default
#define OPEN_CFW_NVDB_LEGACY_PSN_SCAN host_legacy_scan
#define OPEN_CFW_NVDB_OTP_PSN_READ host_otp_read
#define OPEN_CFW_NVDB_ALLOW_FACTORY_RESET 0

#define OPEN_CFW_SELECTOR 0
#include "../../components/apollo_main/core_overlay/service_nvdb.c"

void host_reset(void)
{
    uint32_t i;
    memset(values, 0, sizeof(values)); memset(nodes, 0, sizeof(nodes));
    memset(system_data, 0, sizeof(system_data));
    nodes[0].key = "nvMagic"; nodes[0].value = values[0]; nodes[0].value_length = 4;
    nodes[1].key = "nvSysDt"; nodes[1].value = values[1]; nodes[1].value_length = 172;
    for (i = 2; i < 9; ++i) { nodes[i].key = "x"; nodes[i].value = values[i]; nodes[i].value_length = 1; }
    magic = 0x55550022u; init_result = 0; read_magic_result = 1;
    defaults_calls = controls = reads = legacy_scans = otp_result = 0;
}
void host_set_magic(uint32_t value, int read_result) { magic = value; read_magic_result = read_result; }
void host_set_init_result(int value) { init_result = value; }
int host_defaults_calls(void) { return defaults_calls; }
int host_controls(void) { return controls; }
int host_reads(void) { return reads; }
int host_legacy_scans(void) { return legacy_scans; }
const uint8_t *host_system_data(void) { return system_data; }
