/* SPDX-License-Identifier: Apache-2.0 */

#include "runtime_cordio_attc_proc.h"

#if !defined(OPEN_CFW_ATTC_PROC_ERROR_RESPONSE_ONLY) && \
    !defined(OPEN_CFW_ATTC_PROC_MTU_RESPONSE_ONLY) && \
    !defined(OPEN_CFW_ATTC_PROC_FIND_READ_RESPONSE_ONLY) && \
    !defined(OPEN_CFW_ATTC_PROC_READ_RESPONSE_ONLY) && \
    !defined(OPEN_CFW_ATTC_PROC_WRITE_RESPONSE_ONLY) && \
    !defined(OPEN_CFW_ATTC_PROC_READ_MULTI_VAR_RESPONSE_ONLY) && \
    !defined(OPEN_CFW_ATTC_PROC_MULTI_VAR_NOTIFICATION_ONLY) && \
    !defined(OPEN_CFW_ATTC_PROC_RESPONSE_ONLY) && \
    !defined(OPEN_CFW_ATTC_PROC_INDICATION_ONLY) && \
    !defined(OPEN_CFW_ATTC_PROC_SEND_MESSAGE_ONLY) && \
    !defined(OPEN_CFW_ATTC_PROC_FIND_INFO_REQUEST_ONLY) && \
    !defined(OPEN_CFW_ATTC_PROC_READ_REQUEST_ONLY) && \
    !defined(OPEN_CFW_ATTC_PROC_WRITE_REQUEST_ONLY) && \
    !defined(OPEN_CFW_ATTC_PROC_MTU_REQUEST_ONLY) && \
    !defined(OPEN_CFW_ATTC_PROC_INDICATION_CONFIRM_ONLY) && \
    !defined(OPEN_CFW_ATTC_PROC_CANCEL_REQUEST_ONLY)
#define OPEN_CFW_ATTC_PROC_BUILD_ALL 1
#endif

#ifdef OPEN_CFW_ATTC_PROC_PRODUCTION
#define OPEN_CFW_ATTC_CALLBACK \
    (*(open_cfw_cordio_attc_callback_t *)0x20061104U)
#define OPEN_CFW_ATTC_HANDLER_ID (*(uint8_t *)0x2006110CU)
#define OPEN_CFW_ATTC_AUTO_CONFIRM (*(uint8_t *)0x2006FAB8U)
#define OPEN_CFW_ATTC_ON_DECK \
    ((struct open_cfw_cordio_attc_api_message *)0x2006FA90U)
#define OPEN_CFW_ATTC_CONFIGURATION \
    (*(struct open_cfw_cordio_attc_configuration **)0x200004B4U)
#else
#define OPEN_CFW_ATTC_CALLBACK open_cfw_cordio_attc_callback
#define OPEN_CFW_ATTC_HANDLER_ID open_cfw_cordio_attc_handler_id
#define OPEN_CFW_ATTC_AUTO_CONFIRM open_cfw_cordio_attc_auto_confirm
#define OPEN_CFW_ATTC_ON_DECK open_cfw_cordio_attc_on_deck
#define OPEN_CFW_ATTC_CONFIGURATION open_cfw_cordio_attc_configuration
#endif

static __attribute__((unused)) uint16_t read_u16(const uint8_t *p)
{ return (uint16_t)p[0] | ((uint16_t)p[1] << 8); }
static __attribute__((unused)) void write_u16(uint8_t *p, uint16_t v)
{ p[0] = (uint8_t)v; p[1] = (uint8_t)(v >> 8); }
static __attribute__((unused)) void copy_bytes(uint8_t *d, const uint8_t *s, uint16_t n)
{ while (n-- != 0U) *d++ = *s++; }
static __attribute__((unused)) uint8_t method(uint8_t opcode)
{ return (uint8_t)((opcode & 0xFEU) / 2U); }

#if defined(OPEN_CFW_ATTC_PROC_BUILD_ALL) || defined(OPEN_CFW_ATTC_PROC_ERROR_RESPONSE_ONLY)
__attribute__((used,noinline)) void open_cfw_cordio_attc_process_error_response(
    struct open_cfw_cordio_attc_connection_control_block *c, uint16_t len,
    uint8_t *packet, struct open_cfw_cordio_att_event *event)
{
    uint8_t *p = packet + 9U; (void)len;
    event->header.event = c->outstanding_request.header.event; p++;
    if (event->header.event == 5U || event->header.event == 6U
        || event->header.event == 9U || event->header.event == 11U) p += 2;
    else { event->handle = read_u16(p); p += 2; }
    event->header.status = *p;
    if (event->header.status == 0U) event->header.status = OPEN_CFW_ATTC_PROC_ERROR_UNDEFINED;
    event->value_length = 0U;
}
#endif

#if defined(OPEN_CFW_ATTC_PROC_BUILD_ALL) || defined(OPEN_CFW_ATTC_PROC_MTU_RESPONSE_ONLY)
__attribute__((used,noinline)) void open_cfw_cordio_attc_process_mtu_response(
    struct open_cfw_cordio_attc_connection_control_block *c, uint16_t len,
    uint8_t *packet, struct open_cfw_cordio_att_event *event)
{
    uint16_t mtu = read_u16(packet + 9U);
    uint16_t rx = open_cfw_cordio_hci_get_max_rx_acl_length();
    uint16_t local = rx > 4U ? (uint16_t)(rx - 4U) : 0U;
    (void)len; (void)event;
    if (mtu < 23U) mtu = 23U;
    if (local > OPEN_CFW_ATTC_CONFIGURATION->mtu) local = OPEN_CFW_ATTC_CONFIGURATION->mtu;
    open_cfw_cordio_att_set_mtu(
        (struct open_cfw_cordio_attc_main_control_block *)c->main,
        c->slot, mtu, local);
}
#endif

#if defined(OPEN_CFW_ATTC_PROC_BUILD_ALL) || defined(OPEN_CFW_ATTC_PROC_FIND_READ_RESPONSE_ONLY)
__attribute__((used,noinline)) void open_cfw_cordio_attc_process_find_or_read_response(
    struct open_cfw_cordio_attc_connection_control_block *c, uint16_t len,
    uint8_t *packet, struct open_cfw_cordio_att_event *event)
{
    uint8_t *p = packet + 9U, *end = packet + 8U + len;
    uint8_t param; uint16_t next = c->outstanding_parameters.handles.start_handle;
    if (p >= end) { event->header.status = OPEN_CFW_ATTC_PROC_ERROR_INVALID_RESPONSE; return; }
    if (c->outstanding_request.header.event == 2U)
        param = *p++ == 1U ? 2U : 16U;
    else {
        uint8_t encoded = *p++;
        uint8_t prefix = c->outstanding_request.header.event == 4U ? 2U : 4U;
        if (encoded < prefix) { event->header.status = OPEN_CFW_ATTC_PROC_ERROR_INVALID_RESPONSE; return; }
        param = (uint8_t)(encoded - prefix);
    }
    while (p < end) {
        uint16_t handle, previous;
        if ((size_t)(end - p) < 2U) goto invalid;
        handle = read_u16(p); p += 2;
        if (handle == 0U || next == 0U || handle < next
            || handle > c->outstanding_parameters.handles.end_handle) goto invalid;
        if (c->outstanding_request.header.event == 8U) {
            previous = handle;
            if ((size_t)(end - p) < 2U) goto invalid;
            handle = read_u16(p); p += 2;
            if (handle == 0U || handle < previous || handle < next
                || handle > c->outstanding_parameters.handles.end_handle) goto invalid;
        }
        next = handle == 0xFFFFU ? 0U : (uint16_t)(handle + 1U);
        if ((size_t)(end - p) < param) goto invalid;
        p += param;
    }
    if (event->header.status == 0U && c->outstanding_request.header.status == 1U) {
        if (next == 0U || next == (uint16_t)(c->outstanding_parameters.handles.end_handle + 1U))
            c->outstanding_request.header.status = 0U;
        else { c->outstanding_parameters.handles.start_handle = next; c->outstanding_request.handle = next; }
    }
    return;
invalid:
    event->header.status = OPEN_CFW_ATTC_PROC_ERROR_INVALID_RESPONSE;
}
#endif

#if defined(OPEN_CFW_ATTC_PROC_BUILD_ALL) || defined(OPEN_CFW_ATTC_PROC_READ_RESPONSE_ONLY)
__attribute__((used,noinline)) void open_cfw_cordio_attc_process_read_response(
    struct open_cfw_cordio_attc_connection_control_block *c, uint16_t l,
    uint8_t *p, struct open_cfw_cordio_att_event *e)
{ (void)c; (void)l; (void)p; (void)e; }
#endif
#if defined(OPEN_CFW_ATTC_PROC_BUILD_ALL) || defined(OPEN_CFW_ATTC_PROC_WRITE_RESPONSE_ONLY)
__attribute__((used,noinline)) void open_cfw_cordio_attc_process_write_response(
    struct open_cfw_cordio_attc_connection_control_block *c, uint16_t l,
    uint8_t *p, struct open_cfw_cordio_att_event *e)
{ (void)c; (void)l; (void)p; e->value_length = 0U; }
#endif
#if defined(OPEN_CFW_ATTC_PROC_BUILD_ALL) || defined(OPEN_CFW_ATTC_PROC_READ_MULTI_VAR_RESPONSE_ONLY)
__attribute__((used,noinline)) void open_cfw_cordio_attc_process_read_multiple_variable_response(
    struct open_cfw_cordio_attc_connection_control_block *c, uint16_t l,
    uint8_t *p, struct open_cfw_cordio_att_event *e)
{ (void)c; (void)l; (void)p; (void)e; }
#endif

#if defined(OPEN_CFW_ATTC_PROC_BUILD_ALL) || defined(OPEN_CFW_ATTC_PROC_MULTI_VAR_NOTIFICATION_ONLY)
__attribute__((used,noinline)) void open_cfw_cordio_attc_process_multiple_variable_notification(
    struct open_cfw_cordio_attc_connection_control_block *c, uint16_t len, uint8_t *packet)
{
    struct open_cfw_cordio_att_event event = {0};
    struct open_cfw_cordio_attc_main_control_block *main = c->main;
    if (len < 1U) return;
    event.header.event = method(packet[8]); event.value = packet + 9U;
    event.value_length = (uint16_t)(len - 1U); event.header.parameter = main->connection_id;
    if (OPEN_CFW_ATTC_CALLBACK != 0) OPEN_CFW_ATTC_CALLBACK(&event);
    main->bearer[c->slot].control |= OPEN_CFW_ATTC_PROC_CONFIRM_PENDING;
}
#endif

static __attribute__((unused)) uint8_t min_length(uint8_t m)
{
    switch (m) {
    case 0: return 5U; case 1: return 3U; case 2: return 2U;
    case 3: return 1U; case 4: return 2U; case 5: return 1U;
    case 6: return 1U; case 7: return 1U; case 8: return 2U;
    case 9: return 1U; case 10: return 3U; case 11: return 5U;
    case 12: return 1U; case 13: case 14: case 15: return 0U;
    case 16: return 1U; default: return 0xFFU;
    }
}
static __attribute__((unused)) void dispatch_response(
    uint8_t m, struct open_cfw_cordio_attc_connection_control_block *c,
    uint16_t len, uint8_t *packet, struct open_cfw_cordio_att_event *event)
{
    switch (m) {
    case 0: open_cfw_cordio_attc_process_error_response(c,len,packet,event); break;
    case 1: open_cfw_cordio_attc_process_mtu_response(c,len,packet,event); break;
    case 2: case 4: case 8: open_cfw_cordio_attc_process_find_or_read_response(c,len,packet,event); break;
    case 3: open_cfw_cordio_attc_process_find_by_type_response(c,len,packet,event); break;
    case 5: case 7: open_cfw_cordio_attc_process_read_response(c,len,packet,event); break;
    case 6: open_cfw_cordio_attc_process_read_long_response(c,len,packet,event); break;
    case 9: case 12: open_cfw_cordio_attc_process_write_response(c,len,packet,event); break;
    case 11: open_cfw_cordio_attc_process_prepare_write_response(c,len,packet,event); break;
    case 16: open_cfw_cordio_attc_process_read_multiple_variable_response(c,len,packet,event); break;
    default: break;
    }
}

#if defined(OPEN_CFW_ATTC_PROC_BUILD_ALL) || defined(OPEN_CFW_ATTC_PROC_RESPONSE_ONLY)
__attribute__((used,noinline)) void open_cfw_cordio_attc_process_response(
    struct open_cfw_cordio_attc_connection_control_block *c, uint16_t len, uint8_t *packet)
{
    struct open_cfw_cordio_att_event event = {0}; uint8_t m;
    struct open_cfw_cordio_attc_main_control_block *main = c->main;
    if (c->outstanding_request.header.event == 0U || len < 1U) return;
    m = method(packet[8]);
    if (m > 16U || (m != 0U && m != c->outstanding_request.header.event)) return;
    open_cfw_cordio_wsf_timer_stop_candidate(c->outstanding_timer);
    event.header.event = m; event.value = packet + 9U;
    event.value_length = (uint16_t)(len - 1U); event.handle = c->outstanding_request.handle;
    if (min_length(m) == 0xFFU || len < min_length(m)) return;
    dispatch_response(m,c,len,packet,&event);
    if (c->outstanding_request.header.status == 0U || event.header.status != 0U) {
        c->outstanding_request.header.event = 0U;
        open_cfw_cordio_attc_free_packet(&c->outstanding_request);
    }
    if (m != 1U && OPEN_CFW_ATTC_CALLBACK != 0) {
        event.continuing = c->outstanding_request.header.status;
        event.header.parameter = c->outstanding_request.header.parameter;
        OPEN_CFW_ATTC_CALLBACK(&event);
    }
    if ((main->bearer[c->slot].control & OPEN_CFW_ATTC_PROC_FLOW_DISABLED) == 0U) {
        if (c->outstanding_request.packet != 0) open_cfw_cordio_attc_send_request(c);
        else if (c->slot == 0U && c->connection_id >= 1U
            && c->connection_id <= 3U
            && OPEN_CFW_ATTC_ON_DECK[c->connection_id-1U].header.event != 0U) {
            open_cfw_cordio_attc_setup_request(
                c,&OPEN_CFW_ATTC_ON_DECK[c->connection_id-1U]);
            OPEN_CFW_ATTC_ON_DECK[c->connection_id-1U].header.event = 0U;
        }
    }
}
#endif

#if defined(OPEN_CFW_ATTC_PROC_BUILD_ALL) || defined(OPEN_CFW_ATTC_PROC_INDICATION_ONLY)
__attribute__((used,noinline)) void open_cfw_cordio_attc_process_indication_notification(
    struct open_cfw_cordio_attc_connection_control_block *c, uint16_t len, uint8_t *packet)
{
    struct open_cfw_cordio_att_event event = {0}; uint8_t *confirm;
    struct open_cfw_cordio_attc_main_control_block *main = c->main;
    if (len < 3U) return;
    event.header.event = method(packet[8]); event.handle = read_u16(packet+9U);
    event.value = packet+11U; event.value_length = (uint16_t)(len-3U);
    event.header.parameter = main->connection_id;
    if (event.handle != 0U && OPEN_CFW_ATTC_CALLBACK != 0) OPEN_CFW_ATTC_CALLBACK(&event);
    if (OPEN_CFW_ATTC_AUTO_CONFIRM != 0U && event.header.event == 14U) {
        if ((main->bearer[c->slot].control & OPEN_CFW_ATTC_PROC_FLOW_DISABLED) == 0U
            && (confirm = open_cfw_cordio_att_message_allocate(9U)) != 0) {
            confirm[8] = OPEN_CFW_ATTC_PROC_PDU_VALUE_CONFIRMATION;
            open_cfw_cordio_att_l2c_data_request(main,c->slot,1U,confirm);
        }
        return;
    }
    main->bearer[c->slot].control |= OPEN_CFW_ATTC_PROC_CONFIRM_PENDING;
}
#endif

#if defined(OPEN_CFW_ATTC_PROC_BUILD_ALL) || defined(OPEN_CFW_ATTC_PROC_SEND_MESSAGE_ONLY)
__attribute__((used,noinline)) void open_cfw_cordio_attc_send_message(
    uint8_t conn, uint16_t handle, uint8_t id,
    union open_cfw_cordio_attc_packet_parameter *packet, uint8_t continuing)
{
    struct open_cfw_cordio_attc_connection_control_block *c; uint16_t mtu=0,data=0;
    uint8_t timed=0; open_cfw_cordio_wsf_task_lock_candidate();
    c=open_cfw_cordio_attc_connection_by_id(conn,0U);
    if (c != 0) { struct open_cfw_cordio_attc_main_control_block *m=c->main;
        mtu=m->bearer[0].mtu; timed=(uint8_t)((m->bearer[0].control&4U)!=0U); }
    open_cfw_cordio_wsf_task_unlock_candidate();
    if (mtu>0U && !timed) {
        if (packet != 0) data = id != 11U ? packet->length
            : (!continuing ? (uint16_t)(5U+packet->prepare->length) : 0U);
        if (data<=mtu) { struct open_cfw_cordio_attc_api_message *msg=
            open_cfw_cordio_wsf_message_allocate_candidate(sizeof(*msg));
            if (msg != 0) { msg->header.parameter=conn; msg->header.status=continuing;
                msg->header.event=id; msg->packet=packet; msg->handle=handle; msg->slot=0U;
                open_cfw_cordio_wsf_message_send_candidate(OPEN_CFW_ATTC_HANDLER_ID,msg); return; }
        } else open_cfw_cordio_attc_execute_callback(conn,id,handle,OPEN_CFW_ATTC_PROC_ERROR_MTU_EXCEEDED);
    } else if (timed) open_cfw_cordio_attc_execute_callback(conn,id,handle,OPEN_CFW_ATTC_PROC_ERROR_TIMEOUT);
    if (packet != 0) open_cfw_cordio_wsf_message_free_candidate(packet);
}
#endif

static __attribute__((unused)) union open_cfw_cordio_attc_packet_parameter *alloc_packet(uint16_t n)
{ return open_cfw_cordio_att_message_allocate(n); }

#if defined(OPEN_CFW_ATTC_PROC_BUILD_ALL) || defined(OPEN_CFW_ATTC_PROC_FIND_INFO_REQUEST_ONLY)
__attribute__((used,noinline)) void open_cfw_cordio_attc_find_information_request(uint8_t c,uint16_t s,uint16_t e,uint8_t cont)
{ union open_cfw_cordio_attc_packet_parameter *p=alloc_packet(13U); if(!p)return;
  p->handles.length=5U;p->handles.start_handle=s;p->handles.end_handle=e;((uint8_t*)p)[8]=4U;
  open_cfw_cordio_attc_send_message(c,s,2U,p,cont); }
#endif
#if defined(OPEN_CFW_ATTC_PROC_BUILD_ALL) || defined(OPEN_CFW_ATTC_PROC_READ_REQUEST_ONLY)
__attribute__((used,noinline)) void open_cfw_cordio_attc_read_request(uint8_t c,uint16_t h)
{ union open_cfw_cordio_attc_packet_parameter *p=alloc_packet(11U);if(!p)return;p->length=3U;
  ((uint8_t*)p)[8]=10U;write_u16((uint8_t*)p+9U,h);open_cfw_cordio_attc_send_message(c,h,5U,p,0U); }
#endif
#if defined(OPEN_CFW_ATTC_PROC_BUILD_ALL) || defined(OPEN_CFW_ATTC_PROC_WRITE_REQUEST_ONLY)
__attribute__((used,noinline)) void open_cfw_cordio_attc_write_request(uint8_t c,uint16_t h,uint16_t n,uint8_t *v)
{ union open_cfw_cordio_attc_packet_parameter *p=alloc_packet((uint16_t)(11U+n));if(!p)return;
  p->length=(uint16_t)(3U+n);((uint8_t*)p)[8]=18U;write_u16((uint8_t*)p+9U,h);
  copy_bytes((uint8_t*)p+11U,v,n);open_cfw_cordio_attc_send_message(c,h,9U,p,0U); }
#endif
#if defined(OPEN_CFW_ATTC_PROC_BUILD_ALL) || defined(OPEN_CFW_ATTC_PROC_CANCEL_REQUEST_ONLY)
__attribute__((used,noinline)) void open_cfw_cordio_attc_cancel_request(uint8_t c)
{ open_cfw_cordio_attc_send_message(c,0U,OPEN_CFW_ATTC_PROC_MESSAGE_CANCEL,0,0U); }
#endif
#if defined(OPEN_CFW_ATTC_PROC_BUILD_ALL) || defined(OPEN_CFW_ATTC_PROC_MTU_REQUEST_ONLY)
__attribute__((used,noinline)) void open_cfw_cordio_attc_mtu_request(uint8_t c,uint16_t mtu)
{ union open_cfw_cordio_attc_packet_parameter *p=alloc_packet(11U);if(!p)return;p->length=3U;
  ((uint8_t*)p)[8]=2U;write_u16((uint8_t*)p+9U,mtu);open_cfw_cordio_attc_send_message(c,0U,1U,p,0U); }
#endif
#if defined(OPEN_CFW_ATTC_PROC_BUILD_ALL) || defined(OPEN_CFW_ATTC_PROC_INDICATION_CONFIRM_ONLY)
__attribute__((used,noinline)) void open_cfw_cordio_attc_indication_confirm(uint8_t conn)
{ struct open_cfw_cordio_attc_connection_control_block *c;uint8_t *p;
  if(conn==0U)return;c=open_cfw_cordio_attc_connection_by_handle((uint16_t)(conn-1U),0U);
  if(c!=0){struct open_cfw_cordio_attc_main_control_block *m=c->main;
    if((m->bearer[0].control&OPEN_CFW_ATTC_PROC_CONFIRM_PENDING)!=0U
      &&(m->bearer[0].control&OPEN_CFW_ATTC_PROC_FLOW_DISABLED)==0U
      &&(p=open_cfw_cordio_att_message_allocate(9U))!=0){m->bearer[0].control&=(uint8_t)~OPEN_CFW_ATTC_PROC_CONFIRM_PENDING;
      p[8]=OPEN_CFW_ATTC_PROC_PDU_VALUE_CONFIRMATION;open_cfw_cordio_att_l2c_data_request(m,0U,1U,p);}}
}
#endif
