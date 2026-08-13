#include <stddef.h>
#include <stdint.h>
#include "wsf_types.h"
#include "wsf_buf.h"
#include "wsf_cs.h"

void WsfCsEnter(void) {}
void WsfCsExit(void) {}
void open_cfw_wsf_buf_stock_warn1(
    uint32_t severity, const char *subsystem, const char *status,
    const char *message, uint32_t source_line, const char *source_file,
    uint32_t value)
{
    (void)severity; (void)subsystem; (void)status; (void)message;
    (void)source_line; (void)source_file; (void)value;
}

static uint64_t closure_memory[64];
static wsfBufPoolDesc_t closure_desc = { 16U, 4U };
static void closure_diag(WsfBufDiag_t *info) { (void)info; }

void open_cfw_wsf_buf_closure_root(void)
{
    void *item;
    WsfBufPoolStat_t stats;
    (void)WsfBufInit((uint16_t)sizeof(closure_memory),
                     (uint8_t *)closure_memory, 1U, &closure_desc);
    item = WsfBufAlloc(4U);
    if (item != NULL) { WsfBufFree(item); }
    (void)WsfBufGetAllocStats();
    (void)WsfBufGetNumPool();
    WsfBufGetPoolStats(&stats, 0U);
    WsfBufDiagRegister(closure_diag);
}
