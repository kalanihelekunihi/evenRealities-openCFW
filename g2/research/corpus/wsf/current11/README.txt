Scope
-----
This scratch-only matrix authenticates and builds the current production-excluded eleven-function clean-room G2 Cordio/Ambiq FreeRTOS WSF timer candidate. It does not edit or promote repository inputs and does not operate hardware.

Authenticated current input
---------------------------
source SHA-256: 4076f5927ca748ca1215bbd3d409d2799b34e16d820abd874a9c30f95747d791
header SHA-256: ec4b58fca5019c11aea47a56b5c0ad02313112d9289862cc2bf0af145796b2f3
prior v2 oracle artifact SHA-256: 59a67b7a29bf00aae45692f2beb745a96e27ca1dcb20c65b5733680d289d63d1

Compile/link closure
--------------------
The C file includes only runtime_cordio_wsf_timer_candidate.h. That header supplies the complete compile closure through freestanding <stdbool.h>, <stddef.h>, and <stdint.h>. The module has no memcpy, memset, libc, newlib, or compiler-runtime undefined symbol. Its exact external closure is the three recovered globals plus ten provider functions recorded in module-undefined.txt. The isolated stubs resolve all thirteen; linked-undefined.txt is empty for every configuration.

Comparison policy
-----------------
Candidate function-section bodies are compared to the eleven authenticated stock spans. Raw object bodies retain unresolved relocations. Strict normalization removes absolute addresses, relocation values, and call/branch destinations while retaining opcode, register, immediate, and field-offset dataflow. Size equality is evidence for compiler-shape selection only, never a source or byte match.

Results
-------
Thirteen configurations and 143 function rows completed. No raw or strict-normalized exact match occurred.
- -Og has the lowest common-config aggregate absolute size delta: 70 bytes, with five exact-size bodies.
- -Os -fno-optimize-sibling-calls has seven exact-size bodies and 74 bytes aggregate delta. Disabling sibling-call optimization is important for the IAR-style push/BL/pop wrappers.
- Across bounded per-function selections, eight functions can hit exact stock size. The unresolved size gaps are WsfTimerInit (+4 best), WsfTimerServiceExpired (+/-2), and WsfTimerUpdateTicks (-12 best).

Recommendations
---------------
1. Use -Og and -Os -fno-optimize-sibling-calls as the next two GCC comparator lanes; keep per-function compilation explicit rather than forcing one translation-unit optimization profile.
2. Prioritize WsfTimerUpdateTicks. Its best body is still 12 bytes short; close the retained logging/assert/fatal behavior and prove whether the fatal provider is noreturn before adjusting source shape.
3. For WsfTimerInit, qualify the exact xTimerCreate prototype/calling convention, terminal create-failure policy, tick-counter call, callback relocation, and "WSF Timer" literal placement. Its best GCC body remains 4 bytes long.
4. Treat the two-byte WsfTimerServiceExpired gap as compiler epilogue/branch selection until IAR flags or a relocatable hand-authored adapter are authenticated.
5. Before production promotion, close all thirteen provider/global relocations, every external caller, the module literal table, final placement, and target behavior. Exact size alone is insufficient.
