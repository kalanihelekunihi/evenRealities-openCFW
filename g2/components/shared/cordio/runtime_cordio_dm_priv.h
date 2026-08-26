/* SPDX-License-Identifier: Apache-2.0 */
#ifndef OPEN_CFW_RUNTIME_CORDIO_DM_PRIV_H
#define OPEN_CFW_RUNTIME_CORDIO_DM_PRIV_H
#include <stddef.h>
#include <stdint.h>
struct open_cfw_cordio_dm_priv_header{uint16_t parameter;uint8_t event,status;};
struct open_cfw_cordio_dm_priv_resolve{struct open_cfw_cordio_dm_priv_header header;uint8_t irk[16],address[6];};
struct open_cfw_cordio_dm_priv_add{struct open_cfw_cordio_dm_priv_header header;uint8_t address_type,peer_address[6],peer_irk[16],local_irk[16],enable_ll_privacy;};
struct open_cfw_cordio_dm_priv_remove{struct open_cfw_cordio_dm_priv_header header;uint8_t address_type,peer_address[6];};
struct open_cfw_cordio_dm_priv_enable{struct open_cfw_cordio_dm_priv_header header;uint8_t enable;};
struct open_cfw_cordio_dm_priv_mode{struct open_cfw_cordio_dm_priv_header header;uint8_t address_type,peer_address[6],mode;};
struct open_cfw_cordio_dm_priv_generate{struct open_cfw_cordio_dm_priv_header header;uint8_t irk[16];};
struct open_cfw_cordio_dm_priv_aes{struct open_cfw_cordio_dm_priv_header header;uint8_t*ciphertext;}__attribute__((packed));
union open_cfw_cordio_dm_priv_message{struct open_cfw_cordio_dm_priv_header header;struct open_cfw_cordio_dm_priv_resolve resolve;struct open_cfw_cordio_dm_priv_add add;struct open_cfw_cordio_dm_priv_remove remove;struct open_cfw_cordio_dm_priv_enable enable;struct open_cfw_cordio_dm_priv_mode mode;struct open_cfw_cordio_dm_priv_generate generate;struct open_cfw_cordio_dm_priv_aes aes;uint8_t raw[48];};
struct open_cfw_cordio_dm_priv_control{uint8_t hash[3],in_progress;uint16_t add_parameter,remove_parameter;uint8_t enable_ll_privacy,address_resolution_enable,generation[16];};
typedef void(*open_cfw_cordio_dm_priv_callback_t)(void*);
#ifndef OPEN_CFW_DM_PRIV_PRODUCTION
extern struct open_cfw_cordio_dm_priv_control open_cfw_cordio_dm_priv_control;
extern open_cfw_cordio_dm_priv_callback_t open_cfw_cordio_dm_priv_callback;
extern uint8_t open_cfw_cordio_dm_priv_handler_id,open_cfw_cordio_dm_priv_ll_enabled;
extern uintptr_t open_cfw_cordio_dm_priv_interfaces[21];
#endif
void open_cfw_cordio_security_aes(uint8_t*,uint8_t*,uint8_t,uint16_t,uint8_t);void open_cfw_cordio_security_random(uint8_t*,uint8_t);
void open_cfw_cordio_hci_add_resolving(uint8_t,uint8_t*,uint8_t*,uint8_t*);void open_cfw_cordio_hci_remove_resolving(uint8_t,uint8_t*);void open_cfw_cordio_hci_clear_resolving(void);void open_cfw_cordio_hci_set_address_resolution(uint8_t);void open_cfw_cordio_hci_set_privacy_mode(uint8_t,uint8_t*,uint8_t);void open_cfw_cordio_hci_read_peer_resolvable(uint8_t,const uint8_t*);void open_cfw_cordio_hci_read_local_resolvable(uint8_t,const uint8_t*);void open_cfw_cordio_hci_set_rpa_timeout(uint16_t);
void open_cfw_cordio_dm_device_pass_event_to_privacy(uint8_t,uint8_t,uint8_t,uint8_t);void*open_cfw_cordio_wsf_message_allocate(uint16_t);void open_cfw_cordio_wsf_message_send(uint8_t,void*);void open_cfw_cordio_wsf_task_lock(void);void open_cfw_cordio_wsf_task_unlock(void);
void open_cfw_cordio_dm_privacy_action_resolve(union open_cfw_cordio_dm_priv_message*);void open_cfw_cordio_dm_privacy_aes_resolve_complete(union open_cfw_cordio_dm_priv_message*);void open_cfw_cordio_dm_privacy_action_add(union open_cfw_cordio_dm_priv_message*);void open_cfw_cordio_dm_privacy_action_remove(union open_cfw_cordio_dm_priv_message*);void open_cfw_cordio_dm_privacy_action_clear(union open_cfw_cordio_dm_priv_message*);void open_cfw_cordio_dm_privacy_action_enable(union open_cfw_cordio_dm_priv_message*);void open_cfw_cordio_dm_privacy_action_mode(union open_cfw_cordio_dm_priv_message*);void open_cfw_cordio_dm_privacy_action_generate(union open_cfw_cordio_dm_priv_message*);void open_cfw_cordio_dm_privacy_aes_generate_complete(union open_cfw_cordio_dm_priv_message*);void open_cfw_cordio_dm_privacy_hci_handler(struct open_cfw_cordio_dm_priv_header*);void open_cfw_cordio_dm_privacy_set_address_resolution(uint8_t);void open_cfw_cordio_dm_privacy_message_handler(union open_cfw_cordio_dm_priv_message*);void open_cfw_cordio_dm_privacy_reset(void);void open_cfw_cordio_dm_privacy_aes_message_handler(union open_cfw_cordio_dm_priv_message*);void open_cfw_cordio_dm_privacy_initialize(void);
void open_cfw_cordio_dm_privacy_resolve(uint8_t*,uint8_t*,uint16_t);void open_cfw_cordio_dm_privacy_add(uint8_t,const uint8_t*,uint8_t*,uint8_t*,uint8_t,uint16_t);void open_cfw_cordio_dm_privacy_remove(uint8_t,const uint8_t*,uint16_t);void open_cfw_cordio_dm_privacy_clear(void);void open_cfw_cordio_dm_privacy_read_peer(uint8_t,const uint8_t*);void open_cfw_cordio_dm_privacy_read_local(uint8_t,const uint8_t*);void open_cfw_cordio_dm_privacy_enable(uint8_t);void open_cfw_cordio_dm_privacy_timeout(uint16_t);void open_cfw_cordio_dm_privacy_mode(uint8_t,const uint8_t*,uint8_t);void open_cfw_cordio_dm_privacy_generate(uint8_t*,uint16_t);
_Static_assert(sizeof(struct open_cfw_cordio_dm_priv_control)==26U,"G2 privacy CB");_Static_assert(offsetof(struct open_cfw_cordio_dm_priv_resolve,address)==20U,"G2 resolve ABI");_Static_assert(offsetof(struct open_cfw_cordio_dm_priv_add,enable_ll_privacy)==43U,"G2 add ABI");_Static_assert(offsetof(struct open_cfw_cordio_dm_priv_aes,ciphertext)==4U,"G2 AES ABI");
#endif
