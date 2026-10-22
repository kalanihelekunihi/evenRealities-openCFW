/* File-backed XMODEM / XMODEM-1K for the CLI "xmodem -r|-s" command,
 * reconstructed from the 2.2.6.10 disassembly. The protocol code is Georges
 * Menie's xmodem.c (BSD-licensed, www.menie.org) adapted by the vendor to read
 * and write a LittleFS file instead of a memory buffer.
 *
 * Stock ranges:
 *   0x00595a5c..0x00595aa7  check        (CRC16 or 8-bit sum of a block)
 *   0x00595aa8..0x00595ad5  _inbyte      (shell RX stream buffer, 1 byte)
 *   0x00595ad6..0x00595adf  _outbyte     (shell UART putchar)
 *   0x00595ae0..0x00595af1  flushinput
 *   0x00595af2..0x00595cd9  xmodemReceive (path, size)
 *   0x00595cda..0x00595ef1  xmodemTransmit (path, size)
 *   literal pool 0x595ef4..0x595f0b: "w" 0x595ef4, "r" 0x595ef8,
 *   RAM 0x200748bc (shell RX stream), RAM 0x2006b528 (xbuff),
 *   ROM 0x768270 ("xmodemReceive: fopen error\r\n"), RAM 0x2006b52b (&xbuff[3]).
 *
 * Vendor differences from Menie: receive tries 32 times per round with a 3 s
 * byte timeout and returns 0 on EOT (the length is never accumulated); a byte
 * read ends the packet only when _inbyte returns >= 256 (timeout 0xffff); the
 * file is opened on packet 1 and closed on every exit except the fopen error.
 * Transmit always sends 1K (STX) blocks, takes the size from the opened file
 * and returns the byte count (whole blocks) after the EOT is ACKed.
 * Profile g2-apollo-main-2. */
#include <stdint.h>
#include <stddef.h>

#define SOH   0x01
#define STX   0x02
#define EOT   0x04
#define ACK   0x06
#define NAK   0x15
#define CAN   0x18
#define CTRLZ 0x1A

#define MAXRETRANS 25

extern size_t xStreamBufferReceive(void *xStreamBuffer, void *pvRxData, size_t xBufferLengthBytes,
                                   uint32_t xTicksToWait);                          /* 0x57e136 */
extern void *g2_shell_rx_stream;                                                    /* RAM 0x200748bc */
extern void cli_putchar_5415d8(int32_t c);                                          /* 0x5415d8 */
extern void *audio_file_open(const char *path, const char *mode);                   /* 0x474550 fopen */
extern uint32_t audio_file_read(void *buffer, uint32_t size, uint32_t count, void *file); /* 0x474634 fread */
extern uint32_t audio_tracepoint_file_write_474682(const void *buffer, uint32_t size,
                                                   uint32_t count, void *stream);   /* 0x474682 fwrite */
extern int32_t audio_file_close(void *stream);                                      /* 0x4745f4 fclose */
extern int32_t file_size(void *stream);                                             /* 0x4748b4 */
extern int32_t g2_log_transport_queue_failure(const char *format, ...);             /* 0x4733ee am_util_stdio_printf */
extern void audio_uart_buffer_zero(void *destination, uint32_t length, uint32_t fill); /* 0x43c0e4 memset */
/* No definition in g2/src yet: table-driven CRC-16/XMODEM (poly 0x1021, init 0),
 * stock 0x59d350..0x59d37f, table ROM 0x6c0350 (256 x uint16). */
extern uint16_t crc16_ccitt_59d350(const void *buf, int32_t len);

int32_t xmodem_receive_file_595af2(const char *path, int32_t size);
int32_t xmodem_transmit_file_595cda(const char *path, int32_t size);

/* RAM 0x2006b528: xbuff, 1024 data + 3 header + 2 CRC + NUL (no named object in g2/src). */
#define XBUFF ((uint8_t *)(uintptr_t)0x2006b528u)

static const char s_mode_write[] = "w";                              /* ROM 0x595ef4 */
static const char s_mode_read[] = "r";                               /* ROM 0x595ef8 */
static const char s_fopen_error[] = "xmodemReceive: fopen error\r\n"; /* ROM 0x768270 */

/* Stock 0x00595a5c (check) */
static int32_t xmodem_check_595a5c(int32_t crc, const uint8_t *buf, int32_t sz)
{
    if (crc != 0) {
        uint16_t computed = crc16_ccitt_59d350(buf, sz);
        uint16_t received = (uint16_t)((buf[sz] << 8) + buf[sz + 1]);

        if (computed == received)
            return 1;
    } else {
        uint8_t cks = 0u;

        for (int32_t i = 0; i < sz; ++i)
            cks = (uint8_t)(cks + buf[i]);
        if (cks == buf[sz])
            return 1;
    }
    return 0;
}

/* Stock 0x00595aa8 (_inbyte): byte as a signed char, 0xffff on timeout. */
static int32_t xmodem_inbyte_595aa8(uint32_t timeout)
{
    int8_t c = 0;
    size_t n = xStreamBufferReceive(g2_shell_rx_stream, &c, 1u, timeout);

    if (n == 1u)
        return c;
    if (n == 0u)
        return 0xffff;
    return (int32_t)n;
}

/* Stock 0x00595ad6 (_outbyte) */
static void xmodem_outbyte_595ad6(int32_t c)
{
    cli_putchar_5415d8((uint8_t)c);
}

/* Stock 0x00595ae0 (flushinput) */
static void xmodem_flushinput_595ae0(void)
{
    while (xmodem_inbyte_595aa8(3000u) < 256) {
    }
}

static void xmodem_cancel(void)
{
    xmodem_flushinput_595ae0();
    xmodem_outbyte_595ad6(CAN);
    xmodem_outbyte_595ad6(CAN);
    xmodem_outbyte_595ad6(CAN);
}

/* Stock 0x00595af2 (xmodemReceive) */
int32_t xmodem_receive_file_595af2(const char *path, int32_t size)
{
    uint8_t *p;
    int32_t bufsz = 0;
    int32_t crc = 0;
    uint8_t trychar = 'C';
    uint8_t packetno = 1u;
    int32_t i, c, len = 0;
    int32_t retry, retrans = MAXRETRANS;
    void *fp = NULL;

    (void)size;
    for (;;) {
        for (retry = 0; retry < 32; ++retry) {
            if (trychar != 0u)
                xmodem_outbyte_595ad6(trychar);
            c = xmodem_inbyte_595aa8(3000u);
            if ((uint32_t)c < 0xffu) {
                switch (c) {
                case SOH:
                    bufsz = 128;
                    goto start_recv;
                case STX:
                    bufsz = 1024;
                    goto start_recv;
                case EOT:
                    xmodem_flushinput_595ae0();
                    xmodem_outbyte_595ad6(ACK);
                    if (fp != NULL)
                        (void)audio_file_close(fp);
                    return len;
                case CAN:
                    if (xmodem_inbyte_595aa8(1000u) == CAN) {
                        xmodem_flushinput_595ae0();
                        xmodem_outbyte_595ad6(ACK);
                        if (fp != NULL)
                            (void)audio_file_close(fp);
                        return -1;
                    }
                    break;
                default:
                    break;
                }
            }
        }
        if (trychar == 'C') {
            trychar = NAK;
            continue;
        }
        xmodem_cancel();
        if (fp != NULL)
            (void)audio_file_close(fp);
        return -2;

    start_recv:
        if (trychar == 'C')
            crc = 1;
        trychar = 0u;
        p = XBUFF;
        *p++ = (uint8_t)c;
        for (i = 0; i < bufsz + (crc != 0 ? 1 : 0) + 3; ++i) {
            c = xmodem_inbyte_595aa8(5000u);
            if (c >= 256)
                goto reject;
            *p++ = (uint8_t)c;
        }

        if (XBUFF[1] == (uint8_t)~XBUFF[2] &&
            (XBUFF[1] == packetno || XBUFF[1] == (int32_t)packetno - 1) &&
            xmodem_check_595a5c(crc, &XBUFF[3], bufsz) != 0) {
            if (XBUFF[1] == packetno) {
                if (XBUFF[1] == 1u && fp == NULL) {
                    fp = audio_file_open(path, s_mode_write);
                    if (fp == NULL) {
                        (void)g2_log_transport_queue_failure(s_fopen_error);
                        return -1;
                    }
                }
                if (fp != NULL)
                    (void)audio_tracepoint_file_write_474682(&XBUFF[3], 1u, (uint32_t)bufsz, fp);
                ++packetno;
                retrans = MAXRETRANS + 1;
            }
            if (--retrans < 1) {
                xmodem_cancel();
                if (fp != NULL)
                    (void)audio_file_close(fp);
                return -3;
            }
            xmodem_outbyte_595ad6(ACK);
            continue;
        }
    reject:
        xmodem_flushinput_595ae0();
        xmodem_outbyte_595ad6(NAK);
    }
}

/* Stock 0x00595cda (xmodemTransmit) */
int32_t xmodem_transmit_file_595cda(const char *path, int32_t size)
{
    int32_t bufsz, crc = -1;
    uint8_t packetno = 1u;
    int32_t i, c, len = 0;
    int32_t retry;
    void *fp = NULL;

    for (;;) {
        for (retry = 0; retry < 16; ++retry) {
            c = xmodem_inbyte_595aa8(1000u);
            if ((uint32_t)c < 0xffu) {
                switch (c) {
                case 'C':
                    crc = 1;
                    goto start_trans;
                case NAK:
                    crc = 0;
                    goto start_trans;
                case CAN:
                    if (xmodem_inbyte_595aa8(1000u) == CAN) {
                        xmodem_outbyte_595ad6(ACK);
                        xmodem_flushinput_595ae0();
                        return -1;
                    }
                    break;
                default:
                    break;
                }
            }
        }
        xmodem_outbyte_595ad6(CAN);
        xmodem_outbyte_595ad6(CAN);
        xmodem_outbyte_595ad6(CAN);
        xmodem_flushinput_595ae0();
        return -2;

        for (;;) {
        start_trans:
            if (fp == NULL) {
                fp = audio_file_open(path, s_mode_read);
                if (fp == NULL)
                    return -1;
                size = file_size(fp);
            }
            XBUFF[0] = STX;
            bufsz = 1024;
            XBUFF[1] = packetno;
            XBUFF[2] = (uint8_t)~packetno;
            c = size - len;
            if (c > bufsz)
                c = bufsz;
            if (c >= 1) {
                audio_uart_buffer_zero(&XBUFF[3], (uint32_t)bufsz, 0u);
                (void)audio_file_read(&XBUFF[3], 1u, (uint32_t)c, fp);
                if (c < bufsz)
                    XBUFF[3 + c] = CTRLZ;
                if (crc != 0) {
                    uint16_t ccrc = crc16_ccitt_59d350(&XBUFF[3], bufsz);

                    XBUFF[bufsz + 3] = (uint8_t)(ccrc >> 8);
                    XBUFF[bufsz + 4] = (uint8_t)ccrc;
                } else {
                    uint8_t ccks = 0u;

                    for (i = 3; i < bufsz + 3; ++i)
                        ccks = (uint8_t)(ccks + XBUFF[i]);
                    XBUFF[bufsz + 3] = ccks;
                }
                for (retry = 0; retry < MAXRETRANS; ++retry) {
                    for (i = 0; i < bufsz + 4 + (crc != 0 ? 1 : 0); ++i)
                        xmodem_outbyte_595ad6(XBUFF[i]);
                    c = xmodem_inbyte_595aa8(1000u);
                    if ((uint32_t)c < 0xffu) {
                        switch (c) {
                        case ACK:
                            ++packetno;
                            len += bufsz;
                            goto start_trans;
                        case CAN:
                            if (xmodem_inbyte_595aa8(1000u) == CAN) {
                                xmodem_outbyte_595ad6(ACK);
                                xmodem_flushinput_595ae0();
                                if (fp != NULL)
                                    (void)audio_file_close(fp);
                                return -1;
                            }
                            break;
                        case NAK:
                        default:
                            break;
                        }
                    }
                }
                xmodem_outbyte_595ad6(CAN);
                xmodem_outbyte_595ad6(CAN);
                xmodem_outbyte_595ad6(CAN);
                xmodem_flushinput_595ae0();
                if (fp != NULL)
                    (void)audio_file_close(fp);
                return -4;
            } else {
                for (retry = 0; retry < 10; ++retry) {
                    xmodem_outbyte_595ad6(EOT);
                    c = xmodem_inbyte_595aa8(2000u);
                    if (c == ACK)
                        break;
                }
                xmodem_flushinput_595ae0();
                if (fp != NULL)
                    (void)audio_file_close(fp);
                return c == ACK ? len : -5;
            }
        }
    }
}
