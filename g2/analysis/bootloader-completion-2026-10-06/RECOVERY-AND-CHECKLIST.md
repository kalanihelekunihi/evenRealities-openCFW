# Recovery and concrete source checklist — 2026-10-06

The desktop interruption did not remove saved source or completed test receipts. This checklist distinguishes bounded source validation from a source-complete bootloader.

| Component | Saved validation | Remaining boundary |
|---|---|---|
| Update/image core | 4,542 cases; 1,208 original instruction bytes | Storage/runtime providers and exact compiler build |
| Startup helpers | 39 cases; 182 original bytes | Compressed data representation is authenticated fixture data |
| Startup record dispatcher and vector-base initializer | 7 cases; 276 original bytes including helpers/FPU; direct dispatcher/FPU have no stubs, system-entry providers explicit | Reset/stack limits not executed; system-init/terminal providers unresolved |
| ITCM helpers | 16 cases; source text equals 24 expanded bytes | Original 22-byte compressed representation not reproduced |
| TLSF allocator | 265 operations; 1,994 original bytes | Mutex/scheduler environment |
| DFU task/context | 213 task cases and 37 context cases | Actual task scheduling and provider closure |
| Queue/runtime wrappers | 45 cases; 450 original bytes | Exact kernel queues/timeouts/IRQ scheduling |
| Mutex wrappers | 288 cases; 258 original bytes including runtime/context | Kernel ownership/concurrency |
| NOR read wrapper | 10 cases; 174 original bytes | MSPI transfer and hardware behavior |
| NOR read setup (worker) | 17 cases; 784 original bytes | Review/integration and lower providers |
| MSPI interrupt | 37 cases; 48 original bytes | Synthetic registers |
| MSPI enable (worker) | 9 cases; all 138 stock bytes | Command-queue initializer, review/integration |
| MRAM/control with power guards | 500-case/472-byte hash-bound pass; standalone guards independently rerun | Static op5 callback branches consume at most config[0]; ROM MRAM operation and synthetic registers |
| Standalone power guards | 14 cases; 164 original bytes | Polling modeled as iterations, no calibrated timing |
| Linked littlefs/update/task/queue/runtime/NOR/mutex source | 21 calls passed | Synthetic storage/kernel callbacks; no end-to-end original/hardware boot |

Startup correction: `0x43299c` walks scatter-initialization records at `0x4330d8..0x433120`, invoking slot-relative callbacks that return the next record. It is not an ordinary constructor array. `0x432910` writes `VTOR=0x410000`; the separate literal `0x2007d000` is used for stack limits. These facts are checked against the locked bootloader SHA-256 `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`.

New source: `g2/components/bootloader/startup/record_dispatch.c`, `record_adapters.S`, `records.ld`. Execute `make -C g2/components/bootloader/startup records CPU=cortex-m4 OUT=../../../build/bootloader-completion/startup-records-compatible`; then run `verify_records.py` with that `records.elf`. Evidence: `g2/build/bootloader-completion/startup-records-compatible/comparison-first.json`. Cortex-M4 compatibility execution is separate from the actual Cortex-M55/compiler target. Counts overlap across tests and must not be summed as unique coverage.

Still required internally: full reset/system entry closure; actual HAL configuration/transfer, NOR erase/program; kernel/scheduler/IRQ closure; logger/runtime dependencies; exact resource/code partition; exact build/toolchain configuration; source-generated initialization data and full payload comparison. ROM/SBL bodies absent from this OTA remain explicit external boundaries. No bootable, source-complete or byte-identical claim is made.

SDK recovery: Ambiq and C-SKY copies/build checks are saved. EM extraction lacked its atomic completion marker after the disconnect, and was resumed after checking no extractor survived. IAR Ubuntu compiler download is absent; no activation/install attempted. Existing source/index work was preserved.

Safari recovery: native safaridriver 27.2 starts on local port 47831. Session POST timed out after 20 seconds; a subsequent `/status` returned `ready:true`, with no established-session receipt. No Safari MCP/browser/accessibility tool is exposed. Apple Events JavaScript attempt returned the explicit disabled-setting error; no settings changed. Authenticated IAR download availability remains unverified.

Independent power review resolved the stack-word question: stock guards pass a stack pointer with incidental second words, but all four statically recovered op5 callback paths consume only config[0] or no config. Active callback selection on hardware remains unverified. Mutex independently passed 288 cases/258 bytes, standalone guards reran 14/164 to separate review receipts; old standalone receipt is historical because shared verifier hash changed.

EM recovery completed: extractor exited 0, expected embedded gzip SHA-256 marker verified, 12,766 TAR entries resolve to 7,439 unique file paths; all expected file paths and final regular-file sizes match. Extracted tree contains 7,440 file paths including the completion marker. SDK remains ignored under `.gitignore:150`, installer and activation unexecuted. No temporary extraction directories were deleted.

Safari native MCP discovery supersedes the earlier exposed-tool limitation: `/usr/bin/safaridriver --mcp` successfully initializes and offers supported text extraction. Its page_info returned no active tab; list_tabs exposed no IAR tab. A supported create_tab opened only the requested updates URL. get_page_content returned the actual rendered Ubuntu entry as plain text, without URL/interactive UID, and the valid-subscription requirement. This proves unavailable download in that automation context; shared authentication with the preexisting user tab is not established. No credentials, cookies or JavaScript setting changes were used.

Latest startup receipt is `startup-records-compatible/comparison-fpu.json`: seven cases and 276 distinct original bytes. FPU source `fpu.S` sets CPACR CP10/CP11 mask `0x00f00000`, executes DSB/ISB and writes FPSCR `0x02040000`. Original and source read back `0x02000000` in Unicorn; bit18 semantics are outside this emulator proof. Full reset and stack-limit setup remain unexecuted. Earlier 3/4-case receipts are historical after verifier/source changes.

New worker source: `upstream-worker/mspi-cq-init/mspi_cq_init.c`, eight cases covering all44 original bytes; lower queue initializer remains intercepted. `inventory-worker/nor-read-status/nor_read_status.c`, 12 cases covering170 original bytes; exact command-builder and fifth stack argument recovered, lower PIO/storage effects intercepted. Linking each with its caller is the next provider-removal step.

Provider closure continued: MSPI enable→queue-wrapper→queue-consumer passes12 linked cases/398 unique original bytes; consumer itself passes19/all228bytes with no calls. NOR setup→status command builder latest linked profile passes7/644bytes, standalone status13/170bytes; lowerPIO/errorproviders remain synthetic. Source/evidence are in `upstream-worker/mspi-cmdq-consumer/` and `inventory-worker/nor-read-setup/`. Reset/stack-entry assembly now compiles and links for actual Cortex-M55 via startup `reset-source`, but execution is not validated by the M4 profile.

Tool setup is now installed and verified: see `TOOLING-INSTALL-RESULT.md`. Actual IAR owned-source compile is blocked by LMSC2143 authentication, not missing binaries. Continued source proof: startup/main-init4cases338bytes and decoded callbackslot42e39d; MSPI chain now uses480source-generated table bytes exactly matching locked data, without adding instructioncoverage. Product callback recovery is next.

Secure authentication helper: `third-party/downloaded/login-iar.sh`, syntax checked only and deliberately unexecuted by agent. It retains namedruntime `opencfw-iar-session` plus privateHOMEvolume `opencfw-iar-user-home` outside imagebuild, invokes supported device-code flow without secret argv, checks login-status without show-token. Required cloudsubscription entitlement is user/vendor matter; no entitlementabsenceclaim from unauthenticated compiler result.

Latest bounded source results: startup main-init4/338 includes actual stock/source scatter and main-init bodies, confirms initialcallback42e39d before testinjection; isolated main-init6/100; MSPI full chain with sourceops12/398 plus480data-byte equality; cmdqconsumer19/228; NORsetup/status7/644; mutex288/258 andguards14/164 independentlyrerun. These profiles overlap and must not be summed. Remaining priorities: callback42e39c actualtaskstartup, clock/performance/power/HALtransfer providers, NORprogram/erase andinitializers, actualkernel/scheduler/IRQ, sourcegeneratedcompressedinitializers/vector/layout data, exactcompilerbuild/link closure, ROM/SBLexternalbodies andhardware/equality proof.

New authoritative callback profile: `g2/build/bootloader-completion/main-callback-startup-integrated-compatible/comparison-first.json`, PASS4/370 original bytes. Source-generated72B record table and real callback42e39c replace prior fixturetable/callbacksubstitution; only695compressedstream bytes stayfixtures. It writes managerhandle200004fc, notDFUthread200004d4. StandalonecallbackPASS4/44 includes observedstock invalidstoreFFFFFFFF; exception/HardFault behavior is untested and not a placeholder-safety claim. Code: `g2/components/bootloader/main_callback/`. Older338-byte profile retains explicit substitutedcallback and is superseded for this path.
