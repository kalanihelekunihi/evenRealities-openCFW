#ifndef OPEN_CFW_CALLBACK_FACADES_HOST_H
#define OPEN_CFW_CALLBACK_FACADES_HOST_H
#include <stdint.h>
extern uint32_t open_cfw_test_charge_list;
extern uint32_t open_cfw_test_msg_list;
extern const char open_cfw_test_charge_type[];
extern const char open_cfw_test_msg_type[];
#define OPEN_CFW_CB_CHARGE_LIST ((void *)&open_cfw_test_charge_list)
#define OPEN_CFW_CB_MSG_LIST ((void *)&open_cfw_test_msg_list)
#define OPEN_CFW_CB_CHARGE_TYPE open_cfw_test_charge_type
#define OPEN_CFW_CB_MSG_TYPE open_cfw_test_msg_type
#define OPEN_CFW_CALLBACK_LIST_INIT(l,t) open_cfw_test_callback_init((l),(t))
#define OPEN_CFW_CALLBACK_LIST_DEINIT(l) open_cfw_test_callback_deinit(l)
#define OPEN_CFW_CALLBACK_REGISTER(l,c) open_cfw_test_callback_register((l),(c))
#define OPEN_CFW_CALLBACK_UNREGISTER(l,c) open_cfw_test_callback_unregister((l),(c))
#define OPEN_CFW_CALLBACK_NOTIFY(l,e,v) open_cfw_test_callback_notify((l),(e),(v))
void open_cfw_test_callback_init(void *, const char *);
void open_cfw_test_callback_deinit(void *);
uint32_t open_cfw_test_callback_register(void *, uintptr_t);
void open_cfw_test_callback_unregister(void *, uintptr_t);
void open_cfw_test_callback_notify(void *, uint32_t, uint32_t *);
void open_cfw_test_callback_reset(void);
uint32_t open_cfw_test_callback_word(uint32_t);
void open_cfw_test_callback_set(uint32_t,uint32_t);
#endif
