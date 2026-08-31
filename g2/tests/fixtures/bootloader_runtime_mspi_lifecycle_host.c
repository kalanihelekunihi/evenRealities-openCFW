/* SPDX-License-Identifier: BSD-3-Clause */
#include "../../components/bootloader/core_overlay/runtime_mspi_lifecycle_425066.h"
static open_cfw_mspi_lifecycle_state state;
static open_cfw_mspi_lifecycle_trace trace;
void open_cfw_test_lifecycle_reset(open_cfw_mspi_lifecycle_u32 prefix,
    open_cfw_mspi_lifecycle_u32 configured, open_cfw_mspi_lifecycle_u32 tcb,
    open_cfw_mspi_lifecycle_u32 cq, open_cfw_mspi_lifecycle_u32 hp,
    open_cfw_mspi_lifecycle_u32 xip, open_cfw_mspi_lifecycle_u32 delay,
    open_cfw_mspi_lifecycle_u32 disable_status)
{
    unsigned i; open_cfw_mspi_lifecycle_u8 *p=(void *)&state,*q=(void *)&trace;
    for(i=0;i<sizeof(state);i++)p[i]=0; for(i=0;i<sizeof(trace);i++)q[i]=0;
    state.prefix=prefix;state.module=2;state.configured=(open_cfw_mspi_lifecycle_u8)configured;
    state.tcb_address=tcb;state.tcb_size=64;state.num_cq_entries=cq;
    state.num_hp_entries=hp;state.xip_enabled=(open_cfw_mspi_lifecycle_u8)xip;
    state.xip_delay=delay;state.last_processed=state.num_hp_pending=state.block=
        state.num_transactions=state.pending_hp_transactions=state.num_unsolicited=0xa5a5a5a5U;
    state.hp=state.sequence=state.autonomous=0xa5U;trace.cq_disable_status=disable_status;
}
open_cfw_mspi_lifecycle_u32 open_cfw_test_lifecycle_run(
    open_cfw_mspi_lifecycle_u32 operation, open_cfw_mspi_lifecycle_u32 null_state)
{
    open_cfw_mspi_lifecycle_state *p=null_state?(void *)0:&state;
    if(operation==0)return open_cfw_bootloader_mspi_enable_425066(p,&trace);
    if(operation==1)return open_cfw_bootloader_mspi_disable_4250f0(p,&trace);
    if(operation==2)return open_cfw_bootloader_mspi_deinitialize_42516c(p,&trace);
    return 0xffffffffU;
}
open_cfw_mspi_lifecycle_u32 open_cfw_test_lifecycle_state(open_cfw_mspi_lifecycle_u32 n)
{
    open_cfw_mspi_lifecycle_u32 *p=(void *)&state;if(n<13U)return p[n];
    if(n==13)return state.configured;if(n==14)return state.hp;
    if(n==15)return state.sequence;if(n==16)return state.autonomous;return 0xffffffffU;
}
open_cfw_mspi_lifecycle_u32 open_cfw_test_lifecycle_trace(open_cfw_mspi_lifecycle_u32 n)
{ open_cfw_mspi_lifecycle_u32 *p=(void *)&trace;return n<7U?p[n]:0xffffffffU; }
#include "../../components/bootloader/core_overlay/runtime_mspi_lifecycle_425066.c"
