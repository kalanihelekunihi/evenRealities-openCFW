/* SPDX-License-Identifier: Apache-2.0 */
#include "runtime_cordio_dm_priv.h"
#if !defined(OPEN_CFW_DM_PRIV_RESOLVE_ACTION_ONLY)&&!defined(OPEN_CFW_DM_PRIV_RESOLVE_AES_ONLY)&&!defined(OPEN_CFW_DM_PRIV_ADD_ACTION_ONLY)&&!defined(OPEN_CFW_DM_PRIV_REMOVE_ACTION_ONLY)&&!defined(OPEN_CFW_DM_PRIV_CLEAR_ACTION_ONLY)&&!defined(OPEN_CFW_DM_PRIV_ENABLE_ACTION_ONLY)&&!defined(OPEN_CFW_DM_PRIV_MODE_ACTION_ONLY)&&!defined(OPEN_CFW_DM_PRIV_GENERATE_ACTION_ONLY)&&!defined(OPEN_CFW_DM_PRIV_GENERATE_AES_ONLY)&&!defined(OPEN_CFW_DM_PRIV_HCI_ONLY)&&!defined(OPEN_CFW_DM_PRIV_SET_ENABLE_ONLY)&&!defined(OPEN_CFW_DM_PRIV_MESSAGE_ONLY)&&!defined(OPEN_CFW_DM_PRIV_RESET_ONLY)&&!defined(OPEN_CFW_DM_PRIV_AES_MESSAGE_ONLY)&&!defined(OPEN_CFW_DM_PRIV_INIT_ONLY)&&!defined(OPEN_CFW_DM_PRIV_RESOLVE_ONLY)&&!defined(OPEN_CFW_DM_PRIV_ADD_ONLY)&&!defined(OPEN_CFW_DM_PRIV_REMOVE_ONLY)&&!defined(OPEN_CFW_DM_PRIV_CLEAR_ONLY)&&!defined(OPEN_CFW_DM_PRIV_ENABLE_ONLY)&&!defined(OPEN_CFW_DM_PRIV_MODE_ONLY)&&!defined(OPEN_CFW_DM_PRIV_READ_PEER_ONLY)&&!defined(OPEN_CFW_DM_PRIV_READ_LOCAL_ONLY)&&!defined(OPEN_CFW_DM_PRIV_TIMEOUT_ONLY)&&!defined(OPEN_CFW_DM_PRIV_GENERATE_ONLY)
#define OPEN_CFW_DM_PRIV_ALL 1
#endif
#ifdef OPEN_CFW_DM_PRIV_PRODUCTION
#define C (*(struct open_cfw_cordio_dm_priv_control*)(uintptr_t)0x20073A58U)
#define CB (*(open_cfw_cordio_dm_priv_callback_t*)(uintptr_t)0x20073B80U)
#define HANDLER (*(uint8_t*)(uintptr_t)0x20073B84U)
#define LL (*(uint8_t*)(uintptr_t)0x20073B8EU)
#define IFACES ((uintptr_t*)(uintptr_t)0x20000694U)
#define MAIN_TABLE ((uintptr_t*)(uintptr_t)0x0076AF6CU)
#define AES_TABLE ((uintptr_t*)(uintptr_t)0x0078D454U)
#else
struct open_cfw_cordio_dm_priv_control open_cfw_cordio_dm_priv_control;open_cfw_cordio_dm_priv_callback_t open_cfw_cordio_dm_priv_callback;uint8_t open_cfw_cordio_dm_priv_handler_id,open_cfw_cordio_dm_priv_ll_enabled;uintptr_t open_cfw_cordio_dm_priv_interfaces[21];
#define C open_cfw_cordio_dm_priv_control
#define CB open_cfw_cordio_dm_priv_callback
#define HANDLER open_cfw_cordio_dm_priv_handler_id
#define LL open_cfw_cordio_dm_priv_ll_enabled
#define IFACES open_cfw_cordio_dm_priv_interfaces
#endif
static __attribute__((unused)) void cp(uint8_t*d,const uint8_t*s,unsigned n){while(n--)*d++=*s++;}static __attribute__((unused)) void zz(uint8_t*d,unsigned n){while(n--)*d++=0;}static __attribute__((unused)) uint8_t eq(const uint8_t*a,const uint8_t*b,unsigned n){uint8_t x=0;while(n--)x|=*a++^*b++;return x==0;}static __attribute__((unused)) void callback(void*p){open_cfw_cordio_dm_priv_callback_t f=CB;if(f)f(p);}
#if defined(OPEN_CFW_DM_PRIV_ALL)||defined(OPEN_CFW_DM_PRIV_RESOLVE_ACTION_ONLY)
__attribute__((used,noinline))void open_cfw_cordio_dm_privacy_action_resolve(union open_cfw_cordio_dm_priv_message*m){uint8_t b[16];if(!m)return;if(!(C.in_progress&1U)){cp(C.hash,m->resolve.address,3);cp(b,m->resolve.address+3,3);zz(b+3,13);C.in_progress|=1U;open_cfw_cordio_security_aes(m->resolve.irk,b,HANDLER,m->header.parameter,0x78U);}else{m->header.status=7U;m->header.event=0x37U;callback(m);}}
#endif
#if defined(OPEN_CFW_DM_PRIV_ALL)||defined(OPEN_CFW_DM_PRIV_RESOLVE_AES_ONLY)
__attribute__((used,noinline))void open_cfw_cordio_dm_privacy_aes_resolve_complete(union open_cfw_cordio_dm_priv_message*m){if(!m)return;m->header.status=eq(C.hash,m->aes.ciphertext,3)?0U:5U;C.in_progress&=(uint8_t)~1U;m->header.event=0x37U;callback(m);}
#endif
#if defined(OPEN_CFW_DM_PRIV_ALL)||defined(OPEN_CFW_DM_PRIV_ADD_ACTION_ONLY)
__attribute__((used,noinline))void open_cfw_cordio_dm_privacy_action_add(union open_cfw_cordio_dm_priv_message*m){if(!m)return;C.enable_ll_privacy=m->add.enable_ll_privacy;C.add_parameter=m->header.parameter;open_cfw_cordio_hci_add_resolving(m->add.address_type,m->add.peer_address,m->add.peer_irk,m->add.local_irk);}
#endif
#if defined(OPEN_CFW_DM_PRIV_ALL)||defined(OPEN_CFW_DM_PRIV_REMOVE_ACTION_ONLY)
__attribute__((used,noinline))void open_cfw_cordio_dm_privacy_action_remove(union open_cfw_cordio_dm_priv_message*m){if(!m)return;C.remove_parameter=m->header.parameter;open_cfw_cordio_hci_remove_resolving(m->remove.address_type,m->remove.peer_address);}
#endif
#if defined(OPEN_CFW_DM_PRIV_ALL)||defined(OPEN_CFW_DM_PRIV_CLEAR_ACTION_ONLY)
__attribute__((used,noinline))void open_cfw_cordio_dm_privacy_action_clear(union open_cfw_cordio_dm_priv_message*m){(void)m;open_cfw_cordio_hci_clear_resolving();}
#endif
#if defined(OPEN_CFW_DM_PRIV_ALL)||defined(OPEN_CFW_DM_PRIV_ENABLE_ACTION_ONLY)
__attribute__((used,noinline))void open_cfw_cordio_dm_privacy_action_enable(union open_cfw_cordio_dm_priv_message*m){if(m)open_cfw_cordio_dm_privacy_set_address_resolution(m->enable.enable);}
#endif
#if defined(OPEN_CFW_DM_PRIV_ALL)||defined(OPEN_CFW_DM_PRIV_MODE_ACTION_ONLY)
__attribute__((used,noinline))void open_cfw_cordio_dm_privacy_action_mode(union open_cfw_cordio_dm_priv_message*m){if(m)open_cfw_cordio_hci_set_privacy_mode(m->mode.address_type,m->mode.peer_address,m->mode.mode);}
#endif
#if defined(OPEN_CFW_DM_PRIV_ALL)||defined(OPEN_CFW_DM_PRIV_GENERATE_ACTION_ONLY)
__attribute__((used,noinline))void open_cfw_cordio_dm_privacy_action_generate(union open_cfw_cordio_dm_priv_message*m){if(!m)return;if(!(C.in_progress&2U)){open_cfw_cordio_security_random(C.generation,3);C.generation[2]=(uint8_t)((C.generation[2]&0x3fU)|0x40U);zz(C.generation+3,13);C.in_progress|=2U;open_cfw_cordio_security_aes(m->generate.irk,C.generation,HANDLER,m->header.parameter,0x79U);}else{m->header.status=7U;m->header.event=0x38U;callback(m);}}
#endif
#if defined(OPEN_CFW_DM_PRIV_ALL)||defined(OPEN_CFW_DM_PRIV_GENERATE_AES_ONLY)
__attribute__((used,noinline))void open_cfw_cordio_dm_privacy_aes_generate_complete(union open_cfw_cordio_dm_priv_message*m){uint8_t*p;if(!m)return;p=m->raw+4;cp(p,m->aes.ciphertext,3);cp(p+3,C.generation,3);C.in_progress&=(uint8_t)~2U;m->header.event=0x38U;m->header.status=0;callback(m);}
#endif
#if defined(OPEN_CFW_DM_PRIV_ALL)||defined(OPEN_CFW_DM_PRIV_HCI_ONLY)
__attribute__((used,noinline))void open_cfw_cordio_dm_privacy_hci_handler(struct open_cfw_cordio_dm_priv_header*e){if(!e)return;switch(e->event){case 21:e->event=0x3a; e->parameter=C.add_parameter;if(!e->status&&C.enable_ll_privacy&&!LL)open_cfw_cordio_dm_privacy_set_address_resolution(1);break;case 22:e->event=0x3b;e->parameter=C.remove_parameter;break;case 23:e->event=0x3c;if(!e->status&&LL)open_cfw_cordio_dm_privacy_set_address_resolution(0);break;case 24:e->event=0x3d;break;case 25:e->event=0x3e;break;case 26:e->event=0x3f;if(!e->status){LL=C.address_resolution_enable;open_cfw_cordio_dm_device_pass_event_to_privacy(LL?0x0dU:0x0cU,LL?1U:0U,0,0);}break;default:return;}callback(e);}
#endif
#if defined(OPEN_CFW_DM_PRIV_ALL)||defined(OPEN_CFW_DM_PRIV_SET_ENABLE_ONLY)
__attribute__((used,noinline))void open_cfw_cordio_dm_privacy_set_address_resolution(uint8_t enable){C.address_resolution_enable=enable;open_cfw_cordio_hci_set_address_resolution(enable);}
#endif
#if defined(OPEN_CFW_DM_PRIV_ALL)||defined(OPEN_CFW_DM_PRIV_MESSAGE_ONLY)
__attribute__((used,noinline))void open_cfw_cordio_dm_privacy_message_handler(union open_cfw_cordio_dm_priv_message*m){typedef void(*f)(union open_cfw_cordio_dm_priv_message*);if(!m||(m->header.event&7U)>=7U)return;
#ifdef OPEN_CFW_DM_PRIV_PRODUCTION
((f)(uintptr_t)MAIN_TABLE[m->header.event&7U])(m);
#else
static f const a[7]={open_cfw_cordio_dm_privacy_action_resolve,open_cfw_cordio_dm_privacy_action_add,open_cfw_cordio_dm_privacy_action_remove,open_cfw_cordio_dm_privacy_action_clear,open_cfw_cordio_dm_privacy_action_enable,open_cfw_cordio_dm_privacy_action_mode,open_cfw_cordio_dm_privacy_action_generate};a[m->header.event&7U](m);
#endif
}
#endif
#if defined(OPEN_CFW_DM_PRIV_ALL)||defined(OPEN_CFW_DM_PRIV_RESET_ONLY)
__attribute__((used,noinline))void open_cfw_cordio_dm_privacy_reset(void){C.in_progress=0;LL=0;}
#endif
#if defined(OPEN_CFW_DM_PRIV_ALL)||defined(OPEN_CFW_DM_PRIV_AES_MESSAGE_ONLY)
__attribute__((used,noinline))void open_cfw_cordio_dm_privacy_aes_message_handler(union open_cfw_cordio_dm_priv_message*m){typedef void(*f)(union open_cfw_cordio_dm_priv_message*);if(!m||(m->header.event&7U)>=2U)return;
#ifdef OPEN_CFW_DM_PRIV_PRODUCTION
((f)(uintptr_t)AES_TABLE[m->header.event&7U])(m);
#else
static f const a[2]={open_cfw_cordio_dm_privacy_aes_resolve_complete,open_cfw_cordio_dm_privacy_aes_generate_complete};a[m->header.event&7U](m);
#endif
}
#endif
#if defined(OPEN_CFW_DM_PRIV_ALL)||defined(OPEN_CFW_DM_PRIV_INIT_ONLY)
__attribute__((used,noinline))void open_cfw_cordio_dm_privacy_initialize(void){open_cfw_cordio_wsf_task_lock();IFACES[6]=(uintptr_t)0x0078A868U;IFACES[15]=(uintptr_t)0x0078A874U;open_cfw_cordio_wsf_task_unlock();}
#endif
static __attribute__((unused)) void send(void*m){if(m)open_cfw_cordio_wsf_message_send(HANDLER,m);}static __attribute__((unused)) void*alloc(unsigned n,uint8_t event,uint16_t param){union open_cfw_cordio_dm_priv_message*m=open_cfw_cordio_wsf_message_allocate((uint16_t)n);if(m){zz((uint8_t*)m,(unsigned)n);m->header.event=event;m->header.parameter=param;}return m;}
#if defined(OPEN_CFW_DM_PRIV_ALL)||defined(OPEN_CFW_DM_PRIV_RESOLVE_ONLY)
__attribute__((used,noinline))void open_cfw_cordio_dm_privacy_resolve(uint8_t*a,uint8_t*k,uint16_t p){struct open_cfw_cordio_dm_priv_resolve*m;if(!a||!k)return;m=alloc(sizeof(*m),0x30,p);if(m){cp(m->irk,k,16);cp(m->address,a,6);send(m);}}
#endif
#if defined(OPEN_CFW_DM_PRIV_ALL)||defined(OPEN_CFW_DM_PRIV_ADD_ONLY)
__attribute__((used,noinline))void open_cfw_cordio_dm_privacy_add(uint8_t t,const uint8_t*a,uint8_t*pi,uint8_t*li,uint8_t en,uint16_t p){struct open_cfw_cordio_dm_priv_add*m;if(!a||!pi||!li)return;m=alloc(sizeof(*m),0x31,p);if(m){m->address_type=t;cp(m->peer_address,a,6);cp(m->peer_irk,pi,16);cp(m->local_irk,li,16);m->enable_ll_privacy=en;send(m);}}
#endif
#if defined(OPEN_CFW_DM_PRIV_ALL)||defined(OPEN_CFW_DM_PRIV_REMOVE_ONLY)
__attribute__((used,noinline))void open_cfw_cordio_dm_privacy_remove(uint8_t t,const uint8_t*a,uint16_t p){struct open_cfw_cordio_dm_priv_remove*m;if(!a)return;m=alloc(sizeof(*m),0x32,p);if(m){m->address_type=t;cp(m->peer_address,a,6);send(m);}}
#endif
#if defined(OPEN_CFW_DM_PRIV_ALL)||defined(OPEN_CFW_DM_PRIV_CLEAR_ONLY)
__attribute__((used,noinline))void open_cfw_cordio_dm_privacy_clear(void){send(alloc(sizeof(union open_cfw_cordio_dm_priv_message),0x33,0));}
#endif
#if defined(OPEN_CFW_DM_PRIV_ALL)||defined(OPEN_CFW_DM_PRIV_READ_PEER_ONLY)
__attribute__((used,noinline))void open_cfw_cordio_dm_privacy_read_peer(uint8_t t,const uint8_t*a){if(a)open_cfw_cordio_hci_read_peer_resolvable(t,a);}
#endif
#if defined(OPEN_CFW_DM_PRIV_ALL)||defined(OPEN_CFW_DM_PRIV_READ_LOCAL_ONLY)
__attribute__((used,noinline))void open_cfw_cordio_dm_privacy_read_local(uint8_t t,const uint8_t*a){if(a)open_cfw_cordio_hci_read_local_resolvable(t,a);}
#endif
#if defined(OPEN_CFW_DM_PRIV_ALL)||defined(OPEN_CFW_DM_PRIV_ENABLE_ONLY)
__attribute__((used,noinline))void open_cfw_cordio_dm_privacy_enable(uint8_t e){struct open_cfw_cordio_dm_priv_enable*m=alloc(sizeof(union open_cfw_cordio_dm_priv_message),0x34,0);if(m){m->enable=e;send(m);}}
#endif
#if defined(OPEN_CFW_DM_PRIV_ALL)||defined(OPEN_CFW_DM_PRIV_TIMEOUT_ONLY)
__attribute__((used,noinline))void open_cfw_cordio_dm_privacy_timeout(uint16_t t){open_cfw_cordio_hci_set_rpa_timeout(t);}
#endif
#if defined(OPEN_CFW_DM_PRIV_ALL)||defined(OPEN_CFW_DM_PRIV_MODE_ONLY)
__attribute__((used,noinline))void open_cfw_cordio_dm_privacy_mode(uint8_t t,const uint8_t*a,uint8_t mode){struct open_cfw_cordio_dm_priv_mode*m;if(!a)return;m=alloc(sizeof(*m),0x35,0);if(m){m->address_type=t;cp(m->peer_address,a,6);m->mode=mode;send(m);}}
#endif
#if defined(OPEN_CFW_DM_PRIV_ALL)||defined(OPEN_CFW_DM_PRIV_GENERATE_ONLY)
__attribute__((used,noinline))void open_cfw_cordio_dm_privacy_generate(uint8_t*k,uint16_t p){struct open_cfw_cordio_dm_priv_generate*m;if(!k)return;m=alloc(sizeof(*m),0x36,p);if(m){cp(m->irk,k,16);send(m);}}
#endif
