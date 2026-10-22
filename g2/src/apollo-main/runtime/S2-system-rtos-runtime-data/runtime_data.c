/* IAR DLIB runtime objects reconstructed for Apollo main (IAR runtime is
 * proprietary and not pinned) and the SEGGER RTT control block and buffers
 * (SEGGER RTT is not pinned either). .data values are from the decoded
 * startup init image (RAM 0x20000000..0x20004557).
 *
 * Not defined on purpose: g2_iar_putchar_select_a/_b and g2_iar_fputc_weak
 * are weak references that are undefined in the stock link (see
 * runtime/a-68-iar-stdout/iar_stdout.c). */
#include <stdint.h>
#include "g2_segger_rtt.h"

/* RAM 0x20074f10 (.bss): C11 Annex K constraint handler, NULL by default. */
void (*g2_iar_constraint_handler)(const char *message, void *ptr, uint32_t error);

/* RAM 0x20004488 (.data, 0x38 B): the "C" locale lconv. Seven string
 * pointers to "" (ROM 0x78f6f5), eight CHAR_MAX bytes, decimal point "."
 * at +0x24 (ROM 0x78f6ce), two more "" pointers, then six CHAR_MAX bytes
 * and two zero bytes. */
typedef struct {
    const char *str_00[7]; /* +0x00 */
    char chr_1c[8];        /* +0x1c */
    const char *str_24[3]; /* +0x24 decimal_point, +0x28, +0x2c */
    char chr_30[8];        /* +0x30 */
} g2_iar_lconv_t;
_Static_assert(sizeof(g2_iar_lconv_t) == 0x38u, "IAR lconv span 0x20004488..0x200044bf");

static const char lconv_empty[] = "";
static const char lconv_point[] = ".";

g2_iar_lconv_t g2_iar_lconv_20004488 = {
    {lconv_empty, lconv_empty, lconv_empty, lconv_empty, lconv_empty, lconv_empty, lconv_empty},
    {(char)0xff, (char)0xff, (char)0xff, (char)0xff, (char)0xff, (char)0xff, (char)0xff, (char)0xff},
    {lconv_point, lconv_empty, lconv_empty},
    {(char)0xff, (char)0xff, (char)0xff, (char)0xff, (char)0xff, (char)0xff, 0, 0},
};

/* RAM 0x20072f38 / 0x20072f88 (.bss): 0x50-byte stream buffers of the two
 * IAR FILE objects below (stderr-like and stdout). */
uint8_t g2_iar_stderr_buffer_20072f38[0x50] __attribute__((aligned(4)));
uint8_t g2_iar_stdout_buffer_20072f88[0x50] __attribute__((aligned(4)));

/* RAM 0x200043f8 (.data, 2 x 0x48 B): IAR __iar_Stdout at +0 and the second
 * stream at +0x48 (0x20004440). Words: +0 mode/handle bytes, +4 buffer,
 * +8 buffer end, +0xc/+0x10 next/read end, +0x18 write end, +0x20 and +0x24
 * point into the FILE itself (+0x44 and +0x30). */
typedef struct {
    uint8_t mode[4];   /* +0x00 */
    uint8_t *buf;      /* +0x04 */
    uint8_t *bend;     /* +0x08 */
    uint8_t *next;     /* +0x0c */
    uint8_t *rend;     /* +0x10 */
    uint32_t word_14;  /* +0x14 */
    uint8_t *wend;     /* +0x18 */
    uint32_t word_1c;  /* +0x1c */
    void *self_44;     /* +0x20 -> FILE + 0x44 */
    void *self_30;     /* +0x24 -> FILE + 0x30 */
    uint32_t tail[8];  /* +0x28 */
} g2_iar_file_t;
_Static_assert(sizeof(g2_iar_file_t) == 0x48u, "IAR FILE");

g2_iar_file_t g2_iar_stdout_200043f8[2] = {
    {{0x02u, 0x04u, 0x01u, 0x01u},
     g2_iar_stdout_buffer_20072f88, g2_iar_stdout_buffer_20072f88 + 0x50,
     g2_iar_stdout_buffer_20072f88, g2_iar_stdout_buffer_20072f88, 0u,
     g2_iar_stdout_buffer_20072f88, 0u,
     (uint8_t *)&g2_iar_stdout_200043f8[0] + 0x44, (uint8_t *)&g2_iar_stdout_200043f8[0] + 0x30,
     {0u}},
    {{0x02u, 0x08u, 0x02u, 0x02u},
     g2_iar_stderr_buffer_20072f38, g2_iar_stderr_buffer_20072f38 + 0x50,
     g2_iar_stderr_buffer_20072f38, g2_iar_stderr_buffer_20072f38, 0u,
     g2_iar_stderr_buffer_20072f38, 0u,
     (uint8_t *)&g2_iar_stdout_200043f8[1] + 0x44, (uint8_t *)&g2_iar_stdout_200043f8[1] + 0x30,
     {0u}},
};

/* SEGGER RTT (runtime/p-18-segger-rtt): control block initialised at run
 * time by the RTT init path, so all three objects are .bss. */
g2_rtt_control_block_t g2_segger_rtt;                            /* RAM 0x20071520 (_SEGGER_RTT) */
char g2_segger_rtt_up_buffer[0x400] __attribute__((aligned(4))); /* RAM 0x2006c530 */
char g2_segger_rtt_down_buffer[0x10] __attribute__((aligned(4))); /* RAM 0x20073ec4 */
