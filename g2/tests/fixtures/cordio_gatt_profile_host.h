#ifndef OPEN_CFW_CORDIO_GATT_PROFILE_HOST_H
#define OPEN_CFW_CORDIO_GATT_PROFILE_HOST_H

#include <stdint.h>

struct open_cfw_gatt_control;
struct open_cfw_gatt_event;
extern struct open_cfw_gatt_control open_cfw_test_gatt_control;
extern const uint8_t open_cfw_test_gatt_service_uuid[2];
extern const void *open_cfw_test_gatt_discovery_list;

#define OPEN_CFW_GATT_CONTROL (&open_cfw_test_gatt_control)
#define OPEN_CFW_GATT_SERVICE_UUID open_cfw_test_gatt_service_uuid
#define OPEN_CFW_GATT_DISCOVERY_LIST open_cfw_test_gatt_discovery_list
#define OPEN_CFW_GATT_DISCOVER_SERVICE(...) open_cfw_test_gatt_discover_service(__VA_ARGS__)
#define OPEN_CFW_GATT_SERVICE_CHANGED(event) open_cfw_test_gatt_service_changed(event)
#define OPEN_CFW_GATT_CCC_ENABLED(connection_id,index) open_cfw_test_gatt_ccc_enabled((connection_id),(index))
#define OPEN_CFW_GATT_HANDLE_VALUE_INDICATION(...) open_cfw_test_gatt_handle_value_indication(__VA_ARGS__)
#define OPEN_CFW_GATT_GET_CLIENT_FEATURES(...) open_cfw_test_gatt_get_client_features(__VA_ARGS__)
#define OPEN_CFW_GATT_WRITE_CLIENT_FEATURES(...) open_cfw_test_gatt_write_client_features(__VA_ARGS__)

void open_cfw_test_gatt_discover_service(uint8_t,uint8_t,const uint8_t*,uint8_t,const void*,uint16_t*);
void open_cfw_test_gatt_service_changed(struct open_cfw_gatt_event *);
uint8_t open_cfw_test_gatt_ccc_enabled(uint8_t,uint8_t);
void open_cfw_test_gatt_handle_value_indication(uint8_t,uint16_t,uint16_t,const uint8_t*);
void open_cfw_test_gatt_get_client_features(uint8_t,uint8_t*,uint8_t);
uint8_t open_cfw_test_gatt_write_client_features(uint8_t,uint16_t,uint16_t,const uint8_t*);

void open_cfw_test_gatt_reset(void);
uint32_t open_cfw_test_gatt_word(uint32_t index);
const uint8_t *open_cfw_test_gatt_bytes(void);
void open_cfw_test_gatt_set_ccc(uint8_t connection_id,uint8_t enabled);
void open_cfw_test_gatt_set_features(uint8_t features);
void open_cfw_test_gatt_set_write_result(uint8_t result);

#endif
