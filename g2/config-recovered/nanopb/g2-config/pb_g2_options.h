/*
 * Recovered Even Realities G2 nanopb runtime option contract.
 *
 * This is openCFW first-party compatibility glue, not an upstream nanopb
 * file and not proof of the vendor's original build header. Include it
 * before pb.h (for example with -include) when reproducing the recovered
 * G2 runtime configuration.
 */
#ifndef OPENCFW_PB_G2_OPTIONS_H
#define OPENCFW_PB_G2_OPTIONS_H

#if defined(PB_ENABLE_MALLOC)
#error "G2 nanopb evidence requires PB_ENABLE_MALLOC to remain undefined"
#endif
#if defined(PB_FIELD_32BIT)
#error "G2 nanopb evidence requires the default 16-bit pb_size_t ABI"
#endif
#if defined(PB_WITHOUT_64BIT)
#error "G2 nanopb evidence requires 64-bit scalar support"
#endif
#if defined(PB_CONVERT_DOUBLE_FLOAT)
#error "G2 nanopb evidence requires native 64-bit double handling"
#endif
#if defined(PB_VALIDATE_UTF8)
#error "G2 nanopb evidence requires PB_VALIDATE_UTF8 to remain undefined"
#endif
#if defined(PB_NO_PACKED_STRUCTS)
#error "G2 nanopb evidence retains packed-structure support"
#endif
#if defined(PB_ENCODE_ARRAYS_UNPACKED)
#error "G2 nanopb evidence retains packed repeated scalar encoding"
#endif
#if defined(PB_BUFFER_ONLY)
#error "G2 nanopb evidence retains callback stream support"
#endif
#if defined(PB_NO_ERRMSG)
#error "G2 nanopb evidence retains runtime error strings"
#endif

#if defined(PB_MAX_REQUIRED_FIELDS)
#if PB_MAX_REQUIRED_FIELDS != 64
#error "G2 nanopb evidence requires PB_MAX_REQUIRED_FIELDS == 64"
#endif
#else
#define PB_MAX_REQUIRED_FIELDS 64
#endif

#endif /* OPENCFW_PB_G2_OPTIONS_H */
