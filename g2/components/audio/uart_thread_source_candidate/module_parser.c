/* Experimental TinyFrame byte parser, native 0x491be4 and start0x491bb6.
 * Layout and CRC16/ARC update derive from authenticated Apollo instructions.
 * Frame dispatch0x4919e8 and diagnostic strings remain typed contracts. */
#include <stdint.h>

extern void audio_uart_parser_frame_done(void *module); /* 0x4919e8 */
extern uint32_t audio_log_flags(void); /* selected 0x43d0ce */
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                                uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern const char g2_tf_log_module[],g2_tf_log_file[],g2_tf_log_function[];
extern const char g2_tf_timeout_message[],g2_tf_timeout_short[];
extern const char g2_tf_payload_long_message[],g2_tf_payload_long_short[];
extern const char g2_tf_header_crc_message[],g2_tf_header_crc_short[];
extern const char g2_tf_body_crc_message[],g2_tf_body_crc_short[];

static uint16_t crc_update(uint16_t crc, uint8_t value) {
    crc ^= value;
    for (unsigned i=0;i<8u;++i)
        crc = (uint16_t)((crc >> 1) ^ ((crc & 1u) ? 0xa001u : 0u));
    return crc;
}

static uint16_t *half(uint8_t *base, uint32_t offset) {
    return (uint16_t *)(base + offset);
}

static void parser_log(uint32_t line, uint32_t compressed_level,
                       const char *message, const char *short_message,
                       uint32_t argument, uint8_t has_argument) {
    if (audio_log_flags() & 2u) {
        if (has_argument)
            audio_log_extended(1,g2_tf_log_module,g2_tf_log_file,
                               g2_tf_log_function,line,message,argument);
        else
            audio_log_extended(1,g2_tf_log_module,g2_tf_log_file,
                               g2_tf_log_function,line,message);
    }
    uint32_t flags = audio_log_flags();
    if ((flags & 1u) || (audio_log_flags() & 4u)) {
        if (has_argument)
            (void)compressed_log_output(compressed_level,short_message,
                                        short_message,argument);
        else
            (void)compressed_log_output(compressed_level,short_message,
                                        short_message);
    }
}

static void parser_start(uint8_t *base) {
    *half(base,0x601au) = crc_update(0u,1u);
    base[0x6020u] = 0u;
    base[0x10u] = 3u;
    *half(base,0x6018u) = 0u;
}

void audio_uart_module_feed_byte(void *module, uint8_t value) {
    uint8_t *base = (uint8_t *)module;
    if (*half(base,0x12u) > 99u && base[0x10u] != 0u) {
        base[0x10u] = 0u;
        parser_log(0x251u,0x04000000u,g2_tf_timeout_message,
                   g2_tf_timeout_short,0u,0u);
    }
    *half(base,0x12u) = 0u;
    switch (base[0x10u]) {
    case 0:
        if (value == 1u) parser_start(base);
        break;
    case 1: /* two-byte frame length */
        *half(base,0x601au) = crc_update(*half(base,0x601au),value);
        *half(base,0x16u) = (uint16_t)((*half(base,0x16u) << 8) | value);
        if (++*half(base,0x6018u) == 2u) {
            base[0x10u] = 4u;
            *half(base,0x6018u) = 0u;
        }
        break;
    case 2: /* two-byte header checksum */
        *half(base,0x601cu) = (uint16_t)((*half(base,0x601cu) << 8) | value);
        if (++*half(base,0x6018u) == 2u) {
            if (*half(base,0x601au) == *half(base,0x601cu)) {
                if (*half(base,0x16u) == 0u) {
                    audio_uart_parser_frame_done(base);
                    base[0x10u] = 0u;
                } else {
                    base[0x10u] = 5u;
                    *half(base,0x6018u) = 0u;
                    *half(base,0x601au) = 0u;
                    if (*half(base,0x16u) > 0x6000u) {
                        parser_log(0x2a5u,0x04400000u,
                                   g2_tf_payload_long_message,
                                   g2_tf_payload_long_short,
                                   *half(base,0x16u),1u);
                        base[0x6020u] = 1u;
                    }
                }
            } else {
                parser_log(0x292u,0x04000000u,g2_tf_header_crc_message,
                           g2_tf_header_crc_short,0u,0u);
                base[0x10u] = 0u;
            }
        }
        break;
    case 3: /* two-byte ID */
        *half(base,0x601au) = crc_update(*half(base,0x601au),value);
        *half(base,0x14u) = (uint16_t)((*half(base,0x14u) << 8) | value);
        if (++*half(base,0x6018u) == 2u) {
            base[0x10u] = 1u;
            *half(base,0x6018u) = 0u;
        }
        break;
    case 4: /* two-byte type */
        *half(base,0x601au) = crc_update(*half(base,0x601au),value);
        *half(base,0x601eu) = (uint16_t)((*half(base,0x601eu) << 8) | value);
        if (++*half(base,0x6018u) == 2u) {
            base[0x10u] = 2u;
            *half(base,0x6018u) = 0u;
            *half(base,0x601cu) = 0u;
        }
        break;
    case 5: /* body */
        if (base[0x6020u] == 0u) {
            *half(base,0x601au) = crc_update(*half(base,0x601au),value);
            uint16_t index = *half(base,0x6018u);
            *half(base,0x6018u) = (uint16_t)(index + 1u);
            base[0x18u + index] = value;
        } else {
            ++*half(base,0x6018u);
        }
        if (*half(base,0x6018u) == *half(base,0x16u)) {
            base[0x10u] = 6u;
            *half(base,0x6018u) = 0u;
            *half(base,0x601cu) = 0u;
        }
        break;
    case 6: /* two-byte body checksum */
        *half(base,0x601cu) = (uint16_t)((*half(base,0x601cu) << 8) | value);
        if (++*half(base,0x6018u) == 2u) {
            if (base[0x6020u] == 0u) {
                if (*half(base,0x601au) == *half(base,0x601cu))
                    audio_uart_parser_frame_done(base);
                else
                    parser_log(0x2cau,0x04000000u,g2_tf_body_crc_message,
                               g2_tf_body_crc_short,0u,0u);
            }
            base[0x10u] = 0u;
        }
        break;
    default:
        break;
    }
}
