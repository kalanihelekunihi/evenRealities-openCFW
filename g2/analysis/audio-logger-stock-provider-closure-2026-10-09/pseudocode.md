# Logger data and control flow

```c
// Stock 0x54171C..0x54176A; newly interpreted raw code, decompiler failed.
void logger_uart_init_prefix(void) {
    logger_set_sink((void *)0x5415C3);                 // 0x472C7C
    uart_set_callback(1,(void *)0x5415E7);             // 0x55E8F0
    // Remaining allocation/thread creation is not exercised here.
    // allocate(2048,1,0,0,...);                     // 0x57DEEA boundary
}
// 0x5415C2..0x5415D8
void logger_uart_sink(const char *text) {
    size_t n = stock_strlen(text);                   // 0x44A43C
    uart_channel_write(1,text,n);                    // 0x55E7FA
}
struct uart_channel { // selected fields only; 28 byte stride, base0x20000D2C
    uint32_t unknown0;
    void *handle;                                   // +4
    uint8_t unknown8[12];
    void *callback;                                 // +20
    uint8_t active;                                 // +24
    volatile uint8_t completion;                    // +25
    uint8_t unknown26[2];
};
uint32_t uart_channel_write(uint8_t ch,const void *buf,uint32_t n) {
    uint8_t transfer[56] = {0};
    if(ch>=4 || channels[ch].active!=1) return 1;
    channels[ch].completion=0;
    *(const void **)(transfer+0)=buf;
    *(uint32_t *)(transfer+4)=n;
    // +12 timeout=0; +16 callback=0; +52 type=0(blocking write).
    uint32_t status=uart_transfer(channels[ch].handle,transfer); // 0x58E3F8
    for(unsigned i=0;i<1000 && channels[ch].completion!=1;i++)
        wrapper_delay(10);                          //0x491102 ->0x4807A0
    return status==0 ? 0 : 1;
}
```

The write loop's exhaustion does not independently affect the return value: result depends on HAL submit status. Thus a wrapper return0 does not alone establish its completion flag became1. Post-HAL completion loop is static evidence only in this batch; active dynamic tests stop before HAL dispatch.

Stock HAL0x58E3F8 validates low25 handle bits against0x1EA9E06 and dispatches transfer byte+52:0blocking_write0x58E454,1blocking_read0x58E49E,2nonblocking_write0x58E4E8,3nonblocking_read0x58E50A, other1. Selected pinned SDK am_hal_uart_transfer and magic0xEA9E06 plus init bit corroborate UART identity, not whole-body closure.

The conditional ITM disable flow remains separate. Native source files now reproduce the ten selected poll/debug/ITM/TPIU bodies; see compat.h for exact recovered global addresses. am_hal_debug_disable returns debug-power's final status, ignoring its earlier debug-count result and trace-release result. Its trace count and power count are independently decremented.
