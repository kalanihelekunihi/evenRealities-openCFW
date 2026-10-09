/* Readable reconstruction; not a production implementation or source-identity
 * substitute. Addresses and limits are in REPORT.md and source receipts. */
typedef void (*callback)(void);
void constructor_A9E4(void) {
    /* Stock literals: preinit start=end=0x2000087C, init end=0x20000880. */
    callback *pre_start = (callback *)0x2000087C;
    callback *pre_end = (callback *)0x2000087C;
    callback *init_start = (callback *)0x2000087C;
    callback *init_end = (callback *)0x20000880;
    for (callback *p = pre_start; p != pre_end; ++p) (*p)();
    /* Real 12-byte CRT section: balanced save/restore; no middle body. */
    _init_AA44();
    for (callback *p = init_start; p != init_end; ++p) (*p)();
}
void exit_A9AC(int status) {
    /* __call_exitprocs is undefined weak and linked to zero in this image. */
    callback handler = *(callback *)0x20000F54;
    if (handler) handler();
    halt_AA40(status);
}
void halt_AA40(int status) {
    (void)status;
    for (;;) { /* Stock b AA40. No division instruction survives. */ }
}
