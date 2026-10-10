# Official SDK bounded formatter execution

## Finite result

The unchanged AmbiqSuite5.2.0 `am_util_stdio_snprintf` / `am_util_stdio_vsnprintf` passed108 ordinary guarded native-source cases. Eight separate internal-buffer probes retain **four sanitizer overflow diagnostics**. This API is not standard C snprintf: accepted bytes are copied **without a terminating NUL**; insufficient capacity returns0 without modifying the destination; it does not truncate or return the would-have-written length. Formatting occurs in a global buffer before the output-capacity check, allowing an oversized input to overflow that internal buffer even when n=0 or1.

The requested finite formatter goal is complete under these tests. Neither safe arbitrary-input formatting nor console delivery, startup, hardware, ARM ABI, stock formatter identity or TLSF stock binding is proven. No source replacement/fix or coverage promotion is made. Independent review is pending.

## Exact inputs and execution settings

SDK source/header are reused read-only from ../sdk-runtime-link-20261010-implementation, whose sdk-receipts.json authenticates the downloaded official zip (`d9751350ef593b306838792a64a5620e4912c84ddf32dc9ff6aacd5cca049cad`). input-receipts.json hashes both unchanged files and the installed compiler executable. Copyright/license notices remain intact; SDK source was not patched or copied with notices removed.

Installed Apple clang21 compiles native macOS arm64 with O1, no builtin substitution, AddressSanitizer+UndefinedBehaviorSanitizer, no sanitizer recovery, and recorded commands. This is native source execution using native va_list/system headers, not execution of the ARM object from the prior compile/link experiment. Both API entry points are tested; the vsnprintf adapter uses real va_start/va_end. Global text translation retains its default false setting. Two macro configurations are explicit: plain1024-byte internal buffer versus AM_PART_APOLLO5_API's aligned2048-byte buffer. Neither macro configuration is claimed recovered from stock.

Each input runs in an isolated child process. mmap creates an accessible destination page bordered by PROT_NONE pages; the exact declared destination capacity ends at the trailing guard. The whole destination page begins with0xA7 and is compared against independently specified expected bytes after each call. This validates content, unchanged remainder/canaries and absence of copied termination; it does not rely on strlen of the unterminated result. ASan/UBSan instrument the unchanged SDK C. No output callback is installed and no console printf API from the SDK is exercised.

## Ordinary tests

The92 initial cases vary both macros and both entry points. Capacities0/1/3/4/5/6/1023/1024/UINT32_MAX bracket four-character output. Expectations include character/string substitution, zero-padded decimal, space width, unsigned UINT32_MAX, lowercase/uppercase hexadecimal, signed d/i, literal percent, positive/negative two-decimal floats, empty output and one-character exact-fit rejection/acceptance. An intentionally inaccessible format pointer with n>=1024 verifies the existing early-return guard as a direct-interface projection; it does not establish admissible caller use of invalid pointers.

Sixteen additional cases bracket the largest accepted capacity using generated1022/1023-character strings and n1022/1023. A1022-character output with n1023 copies exactly1022bytes, leaving the last byte0xA7. Equal lengths reject with0 and preserve the whole destination page. A1023-character formatted string fits the plain global with its internal terminator but is rejected for n1023. None of these ordinary cases emitted sanitizer diagnostics or changed a byte beyond its expected destination writes.

The source guard n>=AM_PRINTF_BUFSIZE rejects n1024 and UINT32_MAX before formatting, regardless of the doubled buffer macro. For smaller n, the source first calls vsprintf into g_prfbuf, rejects ui32NumChars>=n, and otherwise copies ui32NumChars bytes only. These observations are limited to the declared inputs/settings; return0 remains ambiguous between empty output and rejection.

## Internal capacity failures and instrumentation limit

Six initial oversize probes call snprintf with n1 or0 and long `%s` input. Plain configuration has three ASan global-buffer-overflow failures:1024characters with n1;1024characters with n0;2049characters with n1. Each diagnostic/process exit is retained, not converted to a passing safety test. Expected output-buffer rejection cannot prevent the earlier global-buffer write.

The aligned configuration's1024-character inputs fit its doubled global and return0 without destination writes. Its2049-character input initially returned0 **without a default ASan diagnostic**, despite exceeding the declared2048-byte internal object. That receipt is preserved and is not interpreted as proof of safety. To discriminate sanitizer blindness from actual bounds behavior, internal-guard.c includes the unchanged SDK source into the test translation unit solely to access its private buffer and explicitly poisons64 shadow bytes immediately after the exact object end. No formatter body or buffer declaration changes. This control allows1024characters and detects a **use-after-poison write** for2049characters with n1. Both outcomes are retained; this extra guard has different translation-unit instrumentation and is not production compilation. The exact internal default-sanitizer omission was not diagnosed further.

All116 child runs are accounted for:108 ordinary expected-completion cases plus8 internal probes. The four fatal diagnostics are intentional bounded failure observations; the initial aligned2049 nonfatal observation is a documented instrumentation limitation, not a passed buffer-safety result. Global sharing/concurrency, arbitrary widths/precisions, hostile format strings, null arguments beyond the explicit early-guard projection, signed minima, all float values and ARM backend behavior remain untested.

## Reproduction and preservation

Run run.py, run-boundary.py, run-internal.py, then verify.py in a new audit-owned directory while keeping the authenticated SDK input paths available. They retain complete stdout/stderr for each child, build commands and expected results. Native binaries, harnesses, failures, tool versions and source hashes are sealed in DELIVERABLES.json. Failed processes are expected only for the explicitly listed internal-capacity probes.

Prior SDK link tests were not repeated; new capacity hypotheses motivated only the additional boundary/shadow-guard cases. The paused actual FlashDB provider and separate denied discovery/source-acquisition phases were untouched. No device, startup, source/index/submodule/permission/remote change or commit occurred. preservation.json verifies existing seals,110 audit inputs and four checkpoints, with index stable during the verification interval.

The evidence boundary is now the exact supported source/configuration and finite buffer cases above. Further production integration would require authentic runtime/stock binding and caller length contracts; those are not supplied by this test. No claim that all possible knowledge is exhausted is made.
