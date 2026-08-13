/*
 * Clean-room source re-expression of the Even Realities G2 2.2.6.10 TinyFrame
 * receive path (TF_AcceptChar), recovered by focused disassembly and documented
 * in docs/research/tinyframe-wire-format-recovery-audit.md.
 *
 * Recovered wire frame (all multi-byte fields big-endian on the wire):
 *   SOF(0x01) | ID(2) | LEN(2) | TYPE(2) | HEAD_CKSUM(2) | DATA(LEN) | DATA_CKSUM(2)
 * with HEAD_CKSUM = CRC-16/ARC over SOF||ID||LEN||TYPE and DATA_CKSUM =
 * CRC-16/ARC over the payload only when LEN is nonzero; TF_MAX_PAYLOAD_RX =
 * 0x6000 (24576).
 *
 * TinyFrame is MIT-licensed; this is a clean-room re-expression of the recovered
 * configuration and control flow, not copied firmware bytes. It exists to prove
 * the recovered receive format is reproducible from human-readable source and
 * behaviourally exact under the Linux (linux-clang) toolchain.
 */

#include <stdint.h>
#include <string.h>

#define TF_SOF_BYTE 0x01u
#define TF_MAX_PAYLOAD_RX 0x6000u  /* 24576, recovered from cmp #0x6001 */

typedef uint16_t tf_cksum_t;

/* CRC-16/ARC, identical contract to research/candidates/tinyframe_crc16.c. */
static tf_cksum_t tf_crc16_byte(uint8_t b)
{
    tf_cksum_t crc = b;
    int i;
    for (i = 0; i < 8; i++)
        crc = (crc & 1u) ? (tf_cksum_t)((crc >> 1) ^ 0xA001u)
                         : (tf_cksum_t)(crc >> 1);
    return crc;
}
static tf_cksum_t tf_cksum_add_byte(tf_cksum_t crc, uint8_t byte)
{
    return (tf_cksum_t)(tf_crc16_byte((uint8_t)((crc ^ byte) & 0xFFu))
                        ^ (crc >> 8));
}

/* Parser states, using the recovered numeric assignments (SOF=0, ID=3, LEN=1,
 * TYPE=4, HEAD_CKSUM=2, DATA=5, DATA_CKSUM=6). The concrete values are
 * immaterial to behaviour; they mirror the firmware for fidelity. */
enum {
    TF_STATE_SOF = 0,
    TF_STATE_ID = 3,
    TF_STATE_LEN = 1,
    TF_STATE_TYPE = 4,
    TF_STATE_HEAD_CKSUM = 2,
    TF_STATE_DATA = 5,
    TF_STATE_DATA_CKSUM = 6
};

typedef struct {
    uint8_t state;
    uint16_t id;
    uint16_t len;
    uint16_t type;
    uint16_t rxi;        /* bytes accumulated in the current field/payload */
    uint16_t cksum;      /* running CRC-16 */
    uint16_t ref_cksum;  /* checksum accumulator read from the wire */
    uint8_t data[TF_MAX_PAYLOAD_RX];
} tf_rx_t;

/* Result of a completed frame; populated by the callback below. */
typedef struct {
    int accepted;
    uint16_t id;
    uint16_t len;
    uint16_t type;
    uint8_t data[TF_MAX_PAYLOAD_RX];
} tf_frame_t;

void tf_rx_init(tf_rx_t *tf)
{
    memset(tf, 0, sizeof(*tf));
    tf->state = TF_STATE_SOF;
}

/* Accumulate one big-endian byte into a 16-bit field (MSB first), matching the
 * recovered `field = (field << 8) | byte` assembly (orrs r,r,byte<<8). */
static uint16_t tf_be_accum(uint16_t field, uint8_t byte)
{
    return (uint16_t)((field << 8) | byte);
}

/*
 * Feed one received byte. On a fully validated frame, *out is populated and the
 * function returns 1; otherwise 0. Head- or data-checksum mismatch resets the
 * parser to SOF (returns 0), exactly as the firmware does.
 */
int tf_accept_char(tf_rx_t *tf, uint8_t c, tf_frame_t *out)
{
    switch (tf->state) {
    case TF_STATE_SOF:
        if (c == TF_SOF_BYTE) {
            tf->state = TF_STATE_ID;
            tf->rxi = 0;
            tf->cksum = tf_cksum_add_byte(0, c);
        }
        return 0;

    case TF_STATE_ID:
        tf->cksum = tf_cksum_add_byte(tf->cksum, c);
        tf->id = tf_be_accum(tf->id, c);
        if (++tf->rxi == 2) { tf->state = TF_STATE_LEN; tf->rxi = 0; }
        return 0;

    case TF_STATE_LEN:
        tf->cksum = tf_cksum_add_byte(tf->cksum, c);
        tf->len = tf_be_accum(tf->len, c);
        if (++tf->rxi == 2) { tf->state = TF_STATE_TYPE; tf->rxi = 0; }
        return 0;

    case TF_STATE_TYPE:
        tf->cksum = tf_cksum_add_byte(tf->cksum, c);
        tf->type = tf_be_accum(tf->type, c);
        if (++tf->rxi == 2) {
            tf->state = TF_STATE_HEAD_CKSUM;
            tf->rxi = 0;
            tf->ref_cksum = 0;
        }
        return 0;

    case TF_STATE_HEAD_CKSUM:
        tf->ref_cksum = tf_be_accum(tf->ref_cksum, c);
        if (++tf->rxi == 2) {
            if (tf->ref_cksum != tf->cksum) {
                tf->state = TF_STATE_SOF;  /* head checksum mismatch */
                return 0;
            }
            if (tf->len > TF_MAX_PAYLOAD_RX) {
                tf->state = TF_STATE_SOF;  /* over the recovered RX cap */
                return 0;
            }
            tf->rxi = 0;
            if (tf->len == 0) {
                tf->state = TF_STATE_SOF;
                if (out) {
                    out->accepted = 1;
                    out->id = tf->id;
                    out->len = 0;
                    out->type = tf->type;
                }
                return 1;
            }
            tf->cksum = 0;
            tf->state = TF_STATE_DATA;
        }
        return 0;

    case TF_STATE_DATA:
        tf->cksum = tf_cksum_add_byte(tf->cksum, c);
        tf->data[tf->rxi] = c;
        if (++tf->rxi == tf->len) {
            tf->state = TF_STATE_DATA_CKSUM;
            tf->rxi = 0;
            tf->ref_cksum = 0;
        }
        return 0;

    case TF_STATE_DATA_CKSUM:
        tf->ref_cksum = tf_be_accum(tf->ref_cksum, c);
        if (++tf->rxi == 2) {
            tf->state = TF_STATE_SOF;
            if (tf->ref_cksum == tf->cksum) {
                if (out) {
                    out->accepted = 1;
                    out->id = tf->id;
                    out->len = tf->len;
                    out->type = tf->type;
                    memcpy(out->data, tf->data, tf->len);
                }
                return 1;
            }
        }
        return 0;

    default:
        tf->state = TF_STATE_SOF;
        return 0;
    }
}
