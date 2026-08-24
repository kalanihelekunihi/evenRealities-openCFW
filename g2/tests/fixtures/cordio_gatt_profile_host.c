#include <stdint.h>

struct open_cfw_gatt_control {
    uint8_t service_changed_index_set;
    uint8_t service_changed_index;
};
struct open_cfw_gatt_event;

struct open_cfw_gatt_control open_cfw_test_gatt_control;
const uint8_t open_cfw_test_gatt_service_uuid[2] = {0x01u, 0x18u};
const void *open_cfw_test_gatt_discovery_list = (const void *)(uintptr_t)0x12345678u;
static uint32_t words[32];
static uint8_t bytes[32];
static uint8_t ccc[4];
static uint8_t features;
static uint8_t write_result;

void open_cfw_test_gatt_reset(void)
{
    uint32_t i;
    open_cfw_test_gatt_control.service_changed_index_set = 0u;
    open_cfw_test_gatt_control.service_changed_index = 0u;
    features = 0u;
    write_result = 0u;
    for (i = 0u; i < 32u; ++i) { words[i] = 0u; bytes[i] = 0u; }
    for (i = 0u; i < 4u; ++i) { ccc[i] = 0u; }
}
uint32_t open_cfw_test_gatt_word(uint32_t index) { return words[index]; }
const uint8_t *open_cfw_test_gatt_bytes(void) { return bytes; }
void open_cfw_test_gatt_set_ccc(uint8_t id,uint8_t enabled) { if (id < 4u) ccc[id] = enabled; }
void open_cfw_test_gatt_set_features(uint8_t value) { features = value; }
void open_cfw_test_gatt_set_write_result(uint8_t result) { write_result = result; }

void open_cfw_test_gatt_discover_service(uint8_t id,uint8_t uuid_len,const uint8_t *uuid,uint8_t count,const void *list,uint16_t *handles)
{
    words[0]=id;words[1]=uuid_len;words[2]=count;words[3]=(uint32_t)(uintptr_t)uuid;words[4]=(uint32_t)(uintptr_t)list;words[5]=(uint32_t)(uintptr_t)handles;
}
void open_cfw_test_gatt_service_changed(struct open_cfw_gatt_event *event) { words[6]++;words[7]=(uint32_t)(uintptr_t)event; }
uint8_t open_cfw_test_gatt_ccc_enabled(uint8_t id,uint8_t index) { words[8]++;words[9]=index;return id<4u?ccc[id]:0u; }
void open_cfw_test_gatt_handle_value_indication(uint8_t id,uint16_t handle,uint16_t length,const uint8_t *value)
{
    uint32_t slot=words[10]++;words[11+slot]=id;words[15+slot]=handle;words[19+slot]=length;
    if (slot < 3u) { bytes[slot*4u]=value[0];bytes[slot*4u+1u]=value[1];bytes[slot*4u+2u]=value[2];bytes[slot*4u+3u]=value[3]; }
}
void open_cfw_test_gatt_get_client_features(uint8_t id,uint8_t *out,uint8_t length) { words[22]++;words[23]=id;words[24]=length;out[0]=features; }
uint8_t open_cfw_test_gatt_write_client_features(uint8_t id,uint16_t offset,uint16_t length,const uint8_t *value) { words[25]++;words[26]=id;words[27]=offset;words[28]=length;words[29]=value[0];return write_result; }
