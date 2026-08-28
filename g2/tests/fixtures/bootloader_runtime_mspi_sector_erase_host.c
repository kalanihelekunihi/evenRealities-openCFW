#include <stdint.h>
#define OPEN_CFW_MSPI_SECTOR_ERASE_HOST 1
#include "../../components/bootloader/core_overlay/runtime_mspi_sector_erase_420a08.c"

static uint32_t available, wait_first, wait_second, wait_count;
static uint32_t enable_status, transfer_status, disable_status;
static uint32_t events[16], event_count, diag_count, diag_format, diag_address, diag_status;
static uint32_t invalid_count, command, transfer_address, length, data, option;

open_cfw_sector_erase_u32 open_cfw_sector_erase_host_available(void){return available;}
void open_cfw_sector_erase_host_event(open_cfw_sector_erase_u32 e){events[event_count++]=e;}
open_cfw_sector_erase_u32 open_cfw_sector_erase_host_wait(void){return wait_count++==0U?wait_first:wait_second;}
open_cfw_sector_erase_u32 open_cfw_sector_erase_host_enable(void){events[event_count++]=5U;return enable_status;}
open_cfw_sector_erase_u32 open_cfw_sector_erase_host_transfer(open_cfw_sector_erase_u32 c,open_cfw_sector_erase_u32 a,open_cfw_sector_erase_u32 l,const open_cfw_sector_erase_u8 *d,open_cfw_sector_erase_u32 o){events[event_count++]=6U;command=c;transfer_address=a;length=l;data=(uint32_t)(uintptr_t)d;option=o;return transfer_status;}
open_cfw_sector_erase_u32 open_cfw_sector_erase_host_disable(void){events[event_count++]=7U;return disable_status;}
void open_cfw_sector_erase_host_invalid_log(void){++invalid_count;}
void open_cfw_sector_erase_host_diag(open_cfw_sector_erase_u32 f,open_cfw_sector_erase_u32 a,open_cfw_sector_erase_u32 s){++diag_count;diag_format=f;diag_address=a;diag_status=s;}

void open_cfw_sector_erase_fixture_reset(void){available=1U;wait_first=0U;wait_second=0U;wait_count=0U;enable_status=0U;transfer_status=0U;disable_status=0U;event_count=0U;diag_count=0U;diag_format=0U;diag_address=0U;diag_status=0U;invalid_count=0U;command=0U;transfer_address=0U;length=0U;data=1U;option=0U;}
void open_cfw_sector_erase_fixture_config(uint32_t f,uint32_t v){switch(f){case 0:available=v;break;case 1:wait_first=v;break;case 2:enable_status=v;break;case 3:transfer_status=v;break;case 4:wait_second=v;break;default:disable_status=v;break;}}
uint32_t open_cfw_sector_erase_fixture_value(uint32_t f){if(f<event_count)return events[f];switch(f){case 16:return event_count;case 17:return diag_count;case 18:return diag_format;case 19:return diag_address;case 20:return diag_status;case 21:return invalid_count;case 22:return command;case 23:return transfer_address;case 24:return length;case 25:return data;default:return option;}}
