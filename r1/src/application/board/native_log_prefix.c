/* Recovered R1 prefix at0x8185c; calendar and module color remain providers. */
#include "nrf_log_str_formatter.h"
#include "nrf_log_ctrl.h"
#include "nrf_fprintf.h"
extern void r1_log_local_datetime_fill(uint8_t out[8]);
static const char *const severity_names[]={0,"E","W","I","D"};
static const char *const colors[]={"\x1b[0m","\x1b[1;30m","\x1b[1;31m","\x1b[1;32m","\x1b[1;33m","\x1b[1;34m","\x1b[1;35m","\x1b[1;36m","\x1b[1;37m"};
int r1_log_ascii_isprint(int value){return value>=32 && value<=126;}
void r1_log_prefix_process(nrf_log_str_formatter_entry_params_t *params,nrf_fprintf_ctx_t *ctx)
{
    if(params->dropped)
        nrf_fprintf(ctx,"%sLogs dropped (%d)%s\r\n",colors[2],params->dropped,colors[0]);
    if(params->severity!=NRF_LOG_SEVERITY_INFO_RAW){
        if(params->use_colors)
            nrf_fprintf(ctx,"%s",colors[nrf_log_color_id_get(params->module_id,params->severity)]);
        uint8_t datetime[8];
        r1_log_local_datetime_fill(datetime);
        nrf_fprintf(ctx,"%s/%d/%d/%02d:%02d:%02d]",severity_names[params->severity],datetime[2],datetime[3],datetime[4],datetime[5],datetime[6]);
    }
}
