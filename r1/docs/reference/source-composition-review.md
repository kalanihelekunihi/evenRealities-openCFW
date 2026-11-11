# R1 relocatable composition in the normal source build

The current report is `build/r1-goodix-log-c-20261110/report.json`:
963 compiled units, 52 application relocatable imports and 23 bootloader
relocatable imports. The strict bootloader link resolves all 23. The strict
application link still has 39 missing references
and its initialized load image exceeds FLASH by 29,928 bytes. The separate
ld region diagnostic is 23,000 bytes. The
[individual-object final-link review](application-source-link-review.md)
records the registry placement and reset data-copy checks.
The [typed structured logger](structured-typed-log-c-review.md) now has a C
entry and record encoder for the stock typed payload modes.
The [profile callback](user-profile-c-review.md) and
[health settings callback](health-settings-c-callback-review.md) now use C
entry frames and close their previously unresolved command-table symbols.
The [manager version log](manager-logging-c-review.md) closes another startup
provider without pulling in newlib's large `sscanf` implementation.
The [GoMore source selectors](gomore-source-select-c-review.md) close two
native imports after 1,831 paired stock/C comparisons.
The [GoMore step and activity accumulators](gomore-accumulators-c-review.md)
close two more after 1,244 paired comparisons.
The [GoMore eleven-byte record table](gomore-record11-c-review.md) closes
another import using existing C model data, with all 256 caller indices
compared against stock.
The [GoMore motion classifier](gomore-motion-classifier-c-review.md) closes
another native import with 548 paired comparisons and all 180 stock entry
bytes executed.
The [GoMore motion gate](gomore-motion-gate-c-review.md) closes one more
import after 832 paired comparisons and all 352 stock entry bytes executed.
The [multicast callback tail call](subscriber-multicast-pure-c-review.md)
removes one handwritten assembly trampoline with identical compiled object bytes.
The [subscriber callback tail call](subscriber-consume-pure-c-review.md)
removes another with identical compiled object bytes.
The [DFU authorization C frame](dfu-auth-frame-pure-c-review.md) removes a
third assembly boundary, preserving the native frame address in paired replay.
The [DFU system-event and control-point C frames](dfu-backend-frames-pure-c-review.md)
remove two more; both preserve their native frame addresses in paired replay.
The [GoMore numerical sleep score](gomore-sleep-score-c-review.md) closes one
native import after 1,181 paired stock/C comparisons, correcting four
low-bit/branch details in the existing shared C primitive.
The [GoMore interval and stage statistics](gomore-sleep-statistics-c-review.md)
close two more with 822 packed/unpacked paired stock/C comparisons.
The [Goodix formatted logging hook](goodix-log-hook-c-review.md) closes one
upstream integration import using source-owned formatting and RTT output.
The [application reset entry](application-reset-c-review.md) now supplies the
Nordic initialization and linker-owned data/BSS initialization. The [application vector table](application-vector-c-review.md)
now has all 128 stock slots in C. The five
[fault entry adapters](application-fault-vectors-c-review.md) now capture
exception LR/SP and call the source diagnostic and reset path.
The [bootloader startup vectors](bootloader-vector-c-review.md) are also C;
there are no assembly source units in the R1 manifest. Its strict link passes.
The [native engine-profile converter](gomore-engine-profile-c-review.md) now uses C:7116 comparisons and8 compiled controls. All436 instruction bytes execute with actual C promotion and disabled logger. Lifecycle/filter/composite and authorization/runtime work remains open.
The [native engine-state initializers](gomore-engine-state-c-review.md) now use C:8704 comparisons and7 compiled controls. All174 instruction bytes execute. Lifecycle engine initialization still needs filter/profile/composite and authorization/runtime dependencies;hardware/startup work remains open.
The [native confidence stage](goodix-spo2-confidence-c-review.md) now uses C:1176 comparisons,including192 direct full graph,912 explicit feature-boundary and72 calculate/model/output caller pairs;8 compiled controls. All674 instruction bytes execute. Its calculate import closes;other health algorithms and hardware/startup work remain open.
The [native dual-window feature extractor](goodix-dual-window-c-review.md) now uses C:584 comparisons,28 bounded correlation-oracle checks and8 compiled controls. All520 instruction bytes execute through the actual C helper graph. Confidence and hardware/startup work remain open.
The [native peak-selection routines](goodix-peak-selection-c-review.md) now use C:5508 comparisons,612 independent oracle pairs and7 compiled controls. All610 instruction bytes execute. Feature extraction,confidence and hardware/startup work remain open.
The [native peak-rate routine](goodix-peak-rate-c-review.md) now uses C:30972 comparisons,1452 independent oracle pairs and6 compiled controls. All316 instruction bytes execute. Peak selection,feature extraction,confidence and hardware/startup work remain open.
The [native packed conversions](goodix-packed-conversion-c-review.md) now use typed C:five entries,521664 comparisons and11 compiled controls. All322 instruction bytes execute. Peak selection,rate extraction,confidence and hardware/startup work remain open.
The [native autocorrelation support](goodix-autocorrelation-c-review.md) now uses C:four entries,34016 comparisons,360 independent oracle pairs and9 compiled controls. All468 native instruction bytes execute. Peak selection,packing,rate extraction and confidence remain open.
The [native peak-feature metrics](goodix-peak-metrics-c-review.md) now use C:51200 comparisons,including2048 independent oracle pairs and10 compiled controls. All220 native bytes execute;sentinel mutation,NaN/FPSCR,score arithmetic and ordered aliases are verified. The remaining correlation/peak/packing/rate path and confidence parent remain open.
The [native confidence statistics](goodix-spo2-statistics-c-review.md) now use C:nine entries,99368 comparisons,including4608 independent oracle pairs and9 compiled controls. All388 native bytes execute;count edge cases,RTZ/FPSCR,strides and live aliases are verified. The feature extractor and confidence parent remain open.
The [native Gaussian interval helper](goodix-gaussian-interval-c-review.md) now uses C:8112 comparisons,including512 numerical-oracle pairs and8 compiled controls. All216 native bytes execute;five-argument hard-float ABI,double exp,f32 stepping and zero-sigma division flags are verified. Confidence and its feature/statistics dependencies remain open.
The [native output-packing stage](goodix-spo2-output-c-review.md) now uses C:134344 comparisons,including4864 rational-oracle pairs,456 real caller pairs and9 compiled controls. All460 native instruction bytes execute;ordered aliases,signed status and f32-before-double scaling are verified. Confidence and its dependencies remain open.
The [native selection stage](goodix-spo2-select-c-review.md) now uses C:369694 comparisons,including4864 independent oracle pairs,456 real caller pairs and10 compiled controls.734 bytes execute and10 unreachable clamp bytes are proved. Live aliases,RTZ/FPSCR,unsigned warmups and mode transitions are verified;confidence/output remain open.
The [native output-quality stage](goodix-spo2-output-quality-c-review.md) now uses C:40584 comparisons,4864 independent integer oracles and9 compiled controls. Real helpers cover344 native bytes;explicit extrema boundaries cover the retained4-byte reverse subtraction. Actual calculate/model/inference/quality integration is checked;three later SpO2 stages remain open.
The [native SpO2 inference parent](goodix-spo2-infer-c-review.md) now uses C:290 instruction bytes,4444 comparisons across real-graph/caller/boundary suites and9 compiled defect controls. Actual heap, model and normalization plus signaling clamp semantics are verified; four later SpO2 stages remain open.
The [native model graph runner](goodix-model-graph-execute-c-review.md) now uses C:five entries,1476 instruction bytes,256 full graph comparisons and8 compiled defect controls. Actual C constructors/heap/operators and full public RAM/ABI are verified. Parent inference and other hardware/startup dependencies remain open.
The [native quantized convolution and helpers](goodix-model-i8-convolution-c-review.md) now use C:3968 instruction bytes,211,945 comparisons and18 rejected compiled defects. Native selective shapes,unroll order,Q31/FP rules,padding,aliases and constructor integration are verified. All model callback bindings now resolve;parent inference/hardware/startup remain open.
The [native recurrent GRU callback](goodix-model-recurrent-c-review.md) now uses C:1120 bytes,18,504 cases/sequences covering20,604 paired invocations and17 rejected compiled defects. Scratch layout, persistent state, live aliases, actual C heap/constructor/math and normal objects are verified. Quantized convolution is the sole remaining model callback binding.
The [native recurrent support helpers](goodix-recurrent-support-c-review.md) now use C:four entries/660 bytes,321,024 comparisons and16 rejected compiled defects. Actual C quantization/floor, live modular matrix and range policies are verified. Both remaining model callback bindings are still open.
The [native float convolution callback](goodix-model-convolution-c-review.md) now uses C:1234 bytes,41,428 comparisons and16 rejected compiled defects. Native padding/relocation, grouped stride, live metadata, C arithmetic and constructor integration are verified. Two callback bindings remain.
The [native float dense callback](goodix-model-dense-c-review.md) now uses C:252 bytes,20,074 comparisons and10 rejected compiled defects. Separate rounding, live activation/output geometry and actual C expf/constructor are verified. Three callback bindings remain.
The [native quantized merge callback](goodix-model-merge-c-review.md) now uses C:418 bytes,26,381 comparisons and13 rejected compiled defects. Cached union, live ranges/data, raw epsilon and actual C rounding/memory are verified. Four callback bindings remain.
The [typed C classifier return](classifier-container-c-review.md) removes two empty assembly blocks and eight register bindings while retaining all four native result words.851,968 stock pairs,132 FPU-disabled pairs and314,640 changed-caller regressions pass. Six compiled defects are rejected. Compiler-private label renumbering in one unmodified helper is exactly audited; imports stay72/22.
The [native tensor concatenation callback](goodix-model-concatenate-c-review.md) now uses C:two entries,146 instruction bytes,27,304 routine or getter/callback comparisons and eight rejected compiled defects. Actual C memory providers, live metadata and cached geometry are verified. Five callback bindings remain.
The [native softmax and C math arithmetic](goodix-softmax-arithmetic-c-review.md) resolve another callback and remove nine arithmetic assembly expressions.25,359 softmax/getter comparisons,689,664 primitive comparisons,264,960 math regressions and132,480 stock expf comparisons pass. Fourteen compiled defects are rejected. Six callback bindings remain.
The [native float pooling callback](goodix-model-float-pool-c-review.md) now uses C:260 instruction bytes,32,761 routine or constructor/callback comparisons and seven rejected compiled defects. Prefix reads, empty windows, cached geometry and live aliases are verified. Seven callback bindings remain.
The [native scalar/vector multiplication callback](goodix-model-scale-c-review.md) now uses C:152 instruction bytes,26,247 routine or getter/callback comparisons and seven rejected compiled defects. Live bounds, cached scalar/stride and FP behavior are verified. Eight callback bindings remain.
The [native tensor stride transform](goodix-model-transform-c-review.md) now uses C:92 instruction bytes,19,946 routine or constructor/callback comparisons and six rejected compiled defects. Real C descriptor dispatch, raw float payloads and live aliases are verified. Nine callback bindings remain.
The [native model quantization callbacks](goodix-model-quantization-c-review.md) now use C: six entries,900 instruction bytes,46,157 routine or constructor/callback comparisons and139,268 isolated saturation comparisons. Twelve compiled defects are rejected. Three executor address imports resolve; ten remain in the current report, correcting the prior narrative count. The inference graph remains open.
The [native model pool/float-add callbacks](goodix-model-pool-add-c-review.md) now use C:598 instruction bytes,47,479 routine or constructor/callback comparisons, independent math oracles and eleven rejected compiled defects. Existing C constructors call real C function pointers; two executor address imports resolve. Other callbacks and the inference graph remain open.
The [native inference normalization and tensor helpers](goodix-spo2-infer-support-c-review.md) now use C:214 instruction bytes,33,328 direct comparisons,1,752 constructor/stage snapshots and nine rejected compiled defects. Native tensor layout/return and FP/overlap behavior are verified. The inference parent and operator callbacks remain open; imports stay82/22.
The [native SpO2 transition routines](goodix-spo2-transition-c-review.md) now use C:98 instruction bytes,178,266 direct comparisons/state oracles,3,724 constructor/stage snapshots and ten rejected compiled defects. Actual processing feeds transition through dropout/recovery, with prior filter classification supplied as input. The transition import resolves; five SpO2 stages remain open.
The [complete native SpO2 summary graph](goodix-spo2-summary-c-review.md) now uses C:17 ABI entries,1,742 instruction bytes,41,723 routine/stage comparisons,108,888 paired push invocations and16 rejected compiled defects. Actual constructors, queues, heap/math, ratio and quality execute together through dropout/recovery and history saturation. The summary import resolves; six SpO2 stages remain open.
The [native SpO2 quality/logistic routines](goodix-spo2-quality-c-review.md) now use C:48,160 stock comparisons, independent flag/finite-score oracles and seven compiled defect controls. All572 native instruction bytes execute; no new assembly or state is added. The quality import resolves; seven SpO2 stages remain open.
The [C integer conversion helper](f32-integer-c-review.md) replaces two assembly sites in the sensor math provider. It passes 393,216 instruction comparisons, 264,960 normal-profile expf/tanhf regressions, 132,480 stock expf comparisons and four compiled defect controls. Imports and state are unchanged.
The [native ratio/peak-history chain](goodix-spo2-ratio-c-review.md) now implements ten entries and all 1,304 native instruction bytes in C. Verification covers 10,348 routine/window comparisons, 33,150 rolling pushes, independent graph/history oracles and thirteen rejected compiled defects. Real constructors, dropout/recovery and 20-entry history saturation are checked. The ratio import resolves; eight later SpO2 stages remain open.
The [FFT scratch and dual-return C improvement](spectral-tail-dual-return-c-review.md) owns both FFT tail words and removes the final assembly block from the math-selection unit. The shared hard-float provider passes 282,176 dual-return/caller/control pairs. All 576 normal-product pipeline comparisons preserve live stage outputs.64 extra exact-reuse wrapper cases expose the old heap-header read and verify the fix;576 total direct-DFT checks pass. The intentional allocation/status difference and unchanged imports 86/22 are documented.
The [math/compiler-intrinsic conversion](math-selection-intrinsics-c-review.md) removes three inline assembly blocks:316256 verified calls and six rejected compiled defects cover C addition/FPSCR effects and the APSR-returning flag helper. One dual-result D0 ABI bridge remains. The combined parent/math build has915 units and imports86/22;902 unrelated source/object pairs plus the typed caller object are unchanged.
The [native spectral parent](goodix-spectral-parent-c-review.md) now connects the real C rolling-buffer, heap, cleanup/window, FFT and peak/harmonic stages:3,268 scenario pairs and twelve rejected compiled defects. Independent signal/DFT checks pass;470 reachable native bytes execute and eight fixed-result capacity bytes are proved unreachable. The spectral import resolves; nine later SpO2 stages remain open.
The [native harmonic grouping stage](goodix-spectral-harmonic-c-review.md) now uses ordinary C:5,329 scenarios and twelve compiled controls pass, executing all1,162 native bytes with actual C heap/math/memory. Independent signal oracles and131072 primitive VNMLS comparisons pass. All903 prior source/object pairs and imports87/22 are unchanged. The spectral parent remains open.
The [native maximum/peak selector](goodix-spectral-peaks-c-review.md) now uses ordinary C:6,840 scenarios and twelve compiled defect controls pass. All378 reachable native bytes execute; two unreachable branch bytes are proved separately. Sensor geometry, live aliases and clamped replacement are checked. All902 prior source/object pairs and imports87/22 remain unchanged. Harmonic and spectral parent remain open.
The [spectral prepare/copy and VMLS correction](goodix-spectral-prepare-c-review.md) now use ordinary C:1,377 scenario pairs and twelve compiled defect controls pass, with all240 native bytes covered. Actual C heap lifecycle, FFT, memory, packed conversion and encoded math execute together. The real core VMLS correction passes262144 isolated instruction pairs and3139 FFT regressions;900 prior source/object pairs are unchanged. Imports remain87/22; spectral parent and peak/harmonic stages remain open.
The [native FFT core](goodix-spectral-fft-c-review.md) now uses ordinary C:2,833 scenario pairs,577 independent oracles and twelve compiled defect controls pass. All808 instruction bytes and260 coefficient bytes are checked. Imports remain87/22; allocator/wrapper integration and spectral orchestration remain open.
The [spectral quantile/sort/mask helpers](goodix-spectral-quantile-c-review.md) now use C:6,806 scenario pairs and twelve defect controls pass, with all504 native bytes covered. Independent rational oracles and actual cleanup/window chains preserve original-input endpoints and live mask aliases. Imports remain87/22; FFT and spectral orchestration remain open.
The [spectral cleanup/window helpers](goodix-spectral-cleanup-c-review.md) now use C:21,472 scenario pairs, including1,344 chained cases and3,040 independent finite oracles, pass with ten defect controls. All308 instruction bytes and500 coefficient bytes are checked. Imports remain87/22; quantile and FFT processing remain open.
The [motion accumulator](goodix-spo2-motion-c-review.md) now uses C:63,648 function comparisons plus9,408 isolated conversion comparisons pass with twelve defect controls. The actual optical/motion root executes with real math; only constructor allocation is modeled. Imports fall to87/22. The root API signature cleanup preserves its prior object.
The [optical accumulator and root dispatch](goodix-spo2-optical-c-review.md) now use C:15,176 function comparisons and9,408 isolated conversion comparisons pass with twelve defect controls. All526 new instruction bytes execute. Actual rolling features and constructors are integrated; motion remains explicit. Imports stay88/22.
The [shared sensor rolling features](goodix-rolling-feature-c-review.md) now use native-layout C:27,208 direct/oracle/lifecycle invocation comparisons and nine defect controls pass, covering all542 instruction bytes. Real constructor sessions and fixed filter coefficients are checked. Imports remain88/22; parent optical/motion processing remains unfinished.
The [SpO2 cached-result encoder](goodix-spo2-result-encode-c-review.md) now uses C:2,541 direct/frame cases and four defect controls pass. Partial/error-window output and live aliases are preserved; eleven later stages remain. Imports fall to88/22.
The [SpO2 batch accumulator](goodix-spo2-batch-c-review.md) now uses C:3,766 invocation comparisons across2,422 scenarios and twelve defect controls pass. Window lifecycle, NaN operand order and signed averaging are preserved. Batch import removed; imports fall to89/22.
The [SpO2 numeric decoder](goodix-spo2-decode-c-review.md) now uses C with real arithmetic helpers and nominal gain state:5,127 direct/core/frame comparisons and fourteen defect controls pass. Fixed powers and native RW defaults are independently checked. Decoder import removed; imports fall to90/22.
The [SpO2 channel assembler and parity helpers](goodix-spo2-assemble-c-review.md) now use C:10,559 direct/core comparisons and twelve defect controls pass. Live enable/PPG effects are preserved; the numeric decoder remains explicit. Imports stay91/22.
The [SpO2 packet layout](goodix-spo2-packet-layout-c-review.md) now explicitly preserves the enable/PPG byte view used by the native assembler:4,433 paired cases pass and the old separate-array object is rejected. No state or imports are added.
The [SpO2 core control flow](goodix-spo2-calculate-c-review.md) now uses C:1,821 stock comparisons and twelve compiled defect controls pass. Native calibration and allocation/error sequencing are preserved. Fourteen deeper processing stages remain explicit, increasing application imports78 to91; no complete computation engine is claimed.
The [SpO2 calibration polynomial](goodix-spo2-math-c-review.md) now has a native C owner:4,640 stock comparisons and four compiled defect controls pass. No state or imports are added; the calculation core remains unfinished.
The [SpO2 frame adapter](goodix-spo2-execute-c-review.md) now uses C: 4,433 direct/dispatcher comparisons and sixteen defect controls pass, including bounded floating-point rounding checks. All five frame adapters execute in integration. The computation core remains explicit as `goodix_spo2_calc`; imports stay 78/22.
The [soft-ADT frame adapter and event reporters](goodix-soft-adt-execute-c-review.md) now use C: 7,270 direct/dispatcher comparisons and seventeen defect controls pass. Native cold report-state/timeout defaults match. Existing state owners are shared; computation remains explicit as `goodix_nadt_calc`, so imports stay 78/22.
The [HR frame adapter](goodix-hr-execute-c-review.md) now uses C: 4,995 direct/dispatcher comparisons and fourteen defect controls pass. Actual HR records feed the HRV adapter. The aggregate import is replaced by explicit unfinished calculation/diagnostic providers, so application imports increase 77 to 78; no core completion is claimed.
The [HRV frame adapter](goodix-hrv-execute-c-review.md) now uses C: 4,620 direct/dispatcher comparisons and thirteen defect controls pass. Canonical HR cache/frame owners are reused with no new state. The unresolved aggregate adapter is replaced by explicit unfinished `goodix_hrv_calc`; imports remain 77/22.
The [ADT wear executor, moving filter and soft-event reporter](goodix-adt-calculate-c-review.md) now use C: 10,325 direct/integrated stock comparisons and thirteen defect controls pass. Existing flags are shared; 28 bytes represent native cache/history. ADT import removed without added imports; four engine executors remain.
The [native Goodix calculation dispatcher](goodix-algorithm-calculate-c-review.md) now uses C: 3,377 paired cases and nine defect controls pass with actual sleep/popcount/memory helpers. One aggregate import is replaced by five explicit unfinished engine executors, increasing application imports from 74 to 78; no calculation-engine completion is claimed.
The [clock update and pending setter](time-update-pure-c-review.md) now use ordinary C without fixed-register constraints: 41,184 Clang/GCC stock comparisons and seven defect controls pass, preserving live backend/context slots, raw pending decisions and offset boundaries. No added state or imports.
The [native NADT initializer](goodix-nadt-initialize-c-review.md) now uses C with a shared reset and explicit configuration state:4096 paired cases, including512 actual allocator/deinit lifecycles, and9 defect controls pass. NADT constructor import removed; byte identity remains waived.
The [native HRV initializer](goodix-hrv-initialize-c-review.md) and checked float-storage helper now use C:1273 direct comparisons, all982 native instruction bytes,128 full real-C allocator/teardown lifecycles and23 defect controls pass. Exact rational floating-point rounding/status checked; successful lifecycles call no function ports. Constructor import removed without added state/imports.
The [native mode6 constructor](goodix-mode6-c-review.md), reusable layer and merge getter now use C:279 direct comparisons, all768 native instruction bytes,128 full real-C HR constructor/teardown lifecycles and20 defect controls pass. Successful lifecycles call no function ports and prove all three model extents. No writable state added; executor implementation/inference and hardware boot remain open.
The [native graph families](goodix-graph-families-c-review.md) and three packed helpers now use C:710 direct comparisons, all1838 native instruction bytes,128 full C allocator/teardown lifecycles and20 compiled defect controls pass. Exact mode0/1 model extents verified. Typed pointer comparison preserves real packed-scalar/address collisions. No writable state added; mode6 and executor implementations remain open.
The [native graph initializer](goodix-graph-initialize-c-review.md) now uses C descriptors and the authenticated startup schema:339 direct comparisons, all236 native instruction bytes,128 full C allocator/teardown lifecycles and16 compiled defect controls pass. All878 prior nongenerated objects remain unchanged; no writable state added. Two family builders and mode6 construction remain open.
The [native graph dispatch](goodix-graph-dispatch-c-review.md) and mode0/1/2 wrappers now use C:408 direct comparisons, all216 native instruction bytes,128 full C allocator/teardown lifecycles and16 compiled defect controls pass. Modes0/1 allocate through C; the deeper graph initializer and mode6 constructor remain modeled. No writable state added.
The [native HR workspace](goodix-hba-workspace-c-review.md), two filter helpers and four resource getters now use C:477 direct comparisons, all440 native instruction bytes,128 full C allocator/teardown lifecycles and22 compiled defect controls pass. Canonical readonly resources are reused, five imports removed, no writable state added. The exact ceil60 caller is folded; graph construction remains open.
The [native HR context constructor](goodix-hba-initialize-c-review.md), byte queue and library code now use C:830 direct comparisons, all440 native instruction bytes,128 actual C allocator/complete-teardown lifecycles and22 compiled defect controls pass. The workspace owner expands4 to16 bytes to cover native writes. Workspace/graph initialization and four resource getters remain open.
The [native SpO2 graph](goodix-model-graph-c-review.md) and seven helpers now use C: 1,605 comparisons with independent complete layouts, all 1,196 native instruction bytes, 128 actual C heap lifecycles and eighteen compiled defect controls pass. Graph assembly no longer uses a modeled provider; eleven opaque executor identity bindings, numerical inference and physical boot remain open.
The [generated SpO2 model constructor](goodix-generated-model-c-review.md) and four descriptor/accessor entries now use C. All 5,794 paired cases, independent complete layouts, 128 real C heap lifecycles and twenty compiled defect controls pass. Graph assembly and four opaque executor address data bindings remain unresolved; inference and physical boot remain open.
The [SpO2 model resource](goodix-spo2-model-resource-c-review.md) supplies 15,696 bytes of readonly numeric model data, the weights accessor and checked forwarding head. All 546 direct, 582 constructor and 128 real-C-heap lifecycle cases pass; ten compiled defects are rejected. Native construction from stock, RAM-rebased and compiled C data yields identical normalized records with the same 3,924-word cursor endpoint. The 883-unit build has 63 application and 22 boot imports; generated model construction/inference and physical boot remain open.
The [SpO2 session initializers](goodix-spo2-session-c-review.md) replace two imports with four C bodies. All 670 direct, 614 full-constructor and 128 real-C-heap/complete-teardown cases pass; sixteen compiled defects are rejected and all 288 native instruction bytes execute. The 882-unit build has 64 application and 22 boot imports, no added imports/state, and only weights/model resources remain open beneath the SpO2 constructor. Signed-division proof requires nonzero descriptor divisors; physical hardware and final linking remain open.
The [SpO2 context constructor](goodix-spo2-initialize-c-review.md) and twelve helpers now use C: 614 direct cases, 128 actual-C heap/complete-teardown lifecycle cases and twenty compiled defects pass; all 668 native instruction bytes execute. The 881-unit build replaces one constructor import with four deeper initialization/resource imports (66 application, 22 boot). No new writable state. A same-ELF QEMU/Unicorn probe isolates a broad memory-hook discrepancy; final fixtures retain full memory comparisons with scoped owner observation.
The [Goodix engine setup](goodix-engine-setup-c-review.md) supplies four engines and four small providers, reusing six existing configuration providers. All 4,080 direct and 2,567 actual-controller comparisons pass; thirteen compiled defects are rejected and all 504 native instruction bytes execute. The 880-unit build replaces four engine imports with four context-constructor imports (63 application, 22 boot). One native flag byte receives ownership; final linking, context construction and physical hardware remain open.
The [Goodix initialization controller](goodix-algorithm-init-c-review.md) and five sensor adapters now use C: 2,567 direct comparisons pass, twelve compiled defects are rejected, and all 282 native instruction bytes execute. The 879-unit build replaces GH3X2X_AlgoInit with four deeper engine dependencies, raising application imports from 60 to 63 (boot remains 22). Six bytes of native state receive explicit ownership; hardware bring-up and final linking remain open.
The [Goodix algorithm version dispatcher](goodix-algorithm-version-c-review.md) now uses C across nine native entries: 3,122 direct graph comparisons pass, eight compiled defects are rejected, and all 768 admitted instruction bytes execute. The 878-unit build removes GH3X2X_AlgoVersion from imports (60 application, 22 boot). The unchecked weights helper remains unadmitted; its caller uses terminated text with an explicitly excluded private scratch tail.
The [pure C board callbacks](board-callbacks-pure-c-review.md) replace 20 naked callback bodies. All 23,880 direct and 7,200 actual charge-chain comparisons pass; twelve compiled defects are rejected. The full 877-unit build passes with unchanged 61 application and 22 boot imports. Final executable linking, hardware delivery and boot remain open.
The [pure C wear decisions](wear-decisions-pure-c-review.md) remove all three remaining assembly boundaries from wear-on/off using GCC strict signaling comparisons and the existing C conversion provider. All 7,011 wear-on, 7,503 wear-off, 1,688 actual motion-pipeline and 131,712 focused FP comparisons pass; fourteen compiled defects are rejected. All 774 native decision instruction bytes execute. Both tested objects match the normal build; 865 other nongenerated objects, writable state and import sets remain unchanged. Cold FP activation, physical sensors, final linking and boot remain open.
The [native algorithm shutdown controller](goodix-algorithm-shutdown-c-review.md) closes GH3X2X_AlgoDeinit with all callback slots bound to C, reducing application imports from 62 to 61. All 16,384 mask, 3,072 signed-status, 148 mutation, twelve null-frame forwarding, 512 actual-C shutdown and sixteen real memory-configuration caller comparisons pass; seventeen compiled defects are rejected. All 96 native instruction bytes execute. The tested object matches its normal object and 866 prior nongenerated objects remain identical. Initialization/calculation, cold FP activation, physical sensors, final linking and boot remain open.
The [native NADT reset and ADT teardown](goodix-native-nadt-reset-c-review.md) recover the complete state/workspace reset, filter initializer and public callbacks. All 1,024 reset/adapter, 4,368 filter, 1,536 ADT, 256 mutation, 2,080 modeled-status, 784 actual-C-fill and 256 actual-C-heap comparisons pass; nineteen compiled defects are rejected. All 278 native instruction bytes execute. Both tested objects match normal objects and 864 prior nongenerated objects remain identical. FP fixtures use an active context; cold FP activation, the controller, initialization/calculation, physical hardware and boot remain open.
The [native SpO2 teardown graph and HR/SpO2 adapters](goodix-native-spo2-teardown-c-review.md) connect every SpO2 release descendant to C and expose public shutdown adapters. All 816 parent, 2,040 helper, 520 mutation, 4,160 adapter, 3,268 actual-SpO2-heap and 2,048 actual-HR-heap comparisons pass; twenty-four compiled defects are rejected. All 606 native instruction bytes execute. Both tested objects equal their normal objects and 862 prior nongenerated objects remain identical. Initialization/computation, ADT/soft ADT shutdown, controller, physical sensors, final linking and boot remain open.
The [native processing parent and typed dispatch](goodix-native-processing-teardown-c-review.md) connect every teardown descendant to ordinary C while preserving live owners and leaving those owners uncleared. All 2,048 parent type/mask, 328 single-field, 368 mutation, 256 dispatch, eight shared-helper and 2,048 actual-C-heap comparisons pass; twelve compiled defects are rejected. All 138 native entry instruction bytes execute. The tested object equals its normal build and 861 prior nongenerated objects remain identical. Initialization, physical hardware, final linking and boot remain open.
The [native record destructors](goodix-native-record-teardown-c-review.md) release three record buffers then their root, with an additional optional buffer for extended records. All 576 field/result, 80 live-mutation, six null-argument and 256 actual-C-heap comparisons pass; nine compiled defects are rejected. All 100 native instruction bytes execute. The normal build matches the tested object and preserves 860 prior nongenerated objects. Parent dispatch, physical hardware and boot remain open.
The [native processing-workspace teardown](goodix-native-workspace-teardown-c-review.md) releases nine record-owned buffers and clears sixteen other nullable cells while retaining the workspace allocation. All 65,536 clear-mask, 1,024 record-mask, 20 live-mutation, 48 helper and 640 actual-C-heap comparisons pass; ten compiled defects are rejected. All 230 native instruction bytes execute. The normal build matches the tested object and preserves 859 prior nongenerated objects. Processing parent teardown, typed destructor dispatch, physical memory and boot remain open.
The [native HRV context teardown](goodix-native-hrv-teardown-c-review.md) preserves live owner reloads, release/clear timing and status adaptation in ordinary C. All 49,152 field-mask, 120 mutation, 18 helper and 1,440 actual-C-heap comparisons pass; ten compiled defects are rejected. All 168 native instruction bytes execute. The new object matches the normal build, and 858 prior nongenerated objects remain identical. HRV initialization/computation, remaining algorithm lifecycle, physical memory and boot remain open.
The [native Goodix resize ABI](goodix-native-reallocate-c-review.md) preserves null, zero-size, shrink/split and full-capacity growth copy behavior in ordinary C. All 20,928 resize comparisons, 36 boundary cases and 1,000 C-only lifecycle operations pass; ten compiled defects are rejected. All 152 native instruction bytes execute, with exact pool images and write order/width/value. The new object matches the normal build, and 857 prior nongenerated objects remain identical. Native deinitialization, algorithm lifecycle, physical memory and boot remain open.
The [native public Goodix allocator and exhaustion policy](goodix-native-malloc-c-review.md) preserve wilderness allocation, payload clearing, watchdog/manager signaling and the non-returning delay loop. All 5,032 allocation, 408 policy and 160 bridge comparisons plus 1,000 C-only lifecycle operations pass; ten compiled defects are rejected. Of 212 native instruction bytes, 208 execute; four follow non-returning fatal calls. The new object matches the normal build, and 856 prior nongenerated objects remain identical. Deinitialization, real reset/scheduler behavior, physical memory and boot remain open.
The [native Goodix bin allocation core](goodix-native-bin-allocate-c-review.md) preserves bin selection, ordered fit and split metadata in ordinary C. All 22,272 comparisons and 1,000 mixed operations pass; nine compiled defects are rejected. Full pool images and write order/width/value match. Of 246 native instruction bytes, 244 execute; a two-byte lower-bound update is not selected by canonical two-bin state. The new object matches the normal build, and 855 prior nongenerated objects remain identical. That step left the public wrapper and fatal policy open; the receipt above recovers them. Physical validation and boot remain open.
The [native Goodix release/query/bin helpers](goodix-native-heap-free-c-review.md) use the canonical pool cell without new state. All 4,613 release comparisons, 2,054 bin inputs and 500 mixed stock-allocation/C-release operations pass; nine compiled defects are rejected. Full pool images and write order/width/value match. Of 484 native instruction bytes, 480 execute; the remaining four form an unreachable increment path. The new object matches the normal build and 854 prior nongenerated objects remain identical. Allocation/reallocation, exhaustion, physical memory and boot remain open.
The [native Goodix pool initializer](goodix-native-heap-init-c-review.md) closes goodix_mem_init with ordinary C and the existing byte-fill body. All 3,520 modeled-fill, 560 actual-fill and 288 actual algorithm-chain comparisons pass; nine compiled defects are rejected. All 124 native instruction bytes execute. Descriptor writes match width/order/value, and the actual chain matches full pool bytes. The new object matches the normal build; 853 prior nongenerated objects remain identical. Allocation/reallocation APIs, physical sensors, final placement and boot remain open.
The [Goodix algorithm configuration front end](goodix-algorithm-config-c-review.md) implements three entries and four typed register lists. All 41,216 direct, 36,864 hook/getter and 36,864 hook/getter/loader comparisons pass; nine compiled defects are rejected. All 108 native entry instruction bytes execute. The new object matches the normal build and 852 prior nongenerated objects remain identical. That build replaced the configuration import with goodix_mem_init and retained 63 imports; the initializer receipt above closes that dependency. Allocation/release APIs, virtual register application, physical sensors and boot remain open.
The [Goodix initialization hook correction](goodix-init-hook-c-review.md) restores the stock halfword watermark reset before the recovery gate. All 8,960 direct and 8,192 actual-getter comparisons pass; five compiled defects and the previous normal-build hook are rejected. All 32 hook instruction bytes execute; 852 nongenerated objects remain identical. Ownership now separates the hook at 0x6a500 from the algorithm configuration entry at 0x29f58. Physical watermark behavior, final placement and boot remain open.
The [ordinary C sensor-data notification throttle](notification-throttle-pure-c-review.md) removes its assembly while preserving unsigned clock handling, live timestamp reads and the final commit after all five stages. All 2,832 direct and 4,032 actual connection-predicate/backend-thunk comparisons pass; eight compiled defects are rejected. All 72 native instruction bytes execute. The other 851 prior nongenerated objects remain identical. Backend getter/stage delivery and physical hardware remain unverified.
The [ordinary C health initialization entries](health-init-entry-pure-c-review.md) remove the remaining assembly from their unit. All 5,440 direct and 3,456 publisher/enqueue comparisons pass; eight compiled defects are rejected. All 92 native instruction bytes execute. The other 851 prior nongenerated objects remain identical. The nested event publisher frame bridge remains; physical sensor initialization, delivery and boot remain open.
The [ordinary C activity writer](activity-store-pure-c-review.md) completes assembly removal from the activity-storage unit, preserving three packed writes and live callbacks. All 41,627 direct, 936 real-calendar and 2,594 activity-caller comparisons pass; nine compiled defects are rejected. All 246 native instruction bytes execute and monitored widths/order/values match. The bucket helper and 851 other nongenerated objects remain identical. Physical activity/clock and boot remain open.
The [ordinary C activity bucket helper](activity-bucket-pure-c-review.md) removes its calendar-frame assembly while preserving the full byte-domain calculation. All 68,161 direct, 936 real-calendar and 2,594 activity-caller comparisons pass; six compiled defects are rejected. All 50 native instruction bytes execute. The parent assembly/relocations and 851 other nongenerated objects remain identical. Physical clock, parent final-image alignment and boot remain open.
The [ordinary C sensor-state publishers](health-state-publish-pure-c-review.md) remove their saved-word assembly wrappers, preserving low-byte gates and full backing words. All 4,608 direct and 1,728 service/publisher/enqueue comparisons pass; seven compiled defects are rejected. All 48 native instruction bytes execute. The other 851 prior nongenerated objects remain identical. The nested publisher frame bridge remains; physical delivery and boot remain open.
The [ordinary C latest-sample entries](latest-entry-pure-c-review.md) remove three private-frame assembly wrappers while preserving the shared packing body. All 300 actual-provider, 20,520 partial-provider and 876 writer/latest/reset comparisons pass; seven compiled defects are rejected. All 128 native instruction bytes execute. The other 851 prior nongenerated objects remain identical. Caller scratch/private frames are excluded; physical sensors and boot remain open.
The [ordinary C HRV writer](hrv-store-pure-c-review.md) completes assembly removal from the sample-storage unit and explicitly selects its SRAM unaligned-access profile. All 51,866 direct, 876 cache-chain and 138,344 other-writer regression comparisons pass; nine compiled defects are rejected. All 226 native instruction bytes execute; monitored SRAM access widths/order/values match. The other 851 prior nongenerated objects remain identical. Physical sensors and boot remain open.
The [ordinary C HR sample writer](hr-store-pure-c-review.md) replaces its assembly and embedded pool. All 34,586 direct, 876 cache-chain and 103,758 other-writer regression comparisons pass; seven compiled defects are rejected. All 220 native instruction bytes execute. The other 851 prior nongenerated objects remain identical. HRV is the only assembly writer left in this unit; physical sensors and boot remain open.
The [ordinary C SpO2 sample writer](spo2-store-pure-c-review.md) replaces its assembly and embedded pool. All 34,586 direct, 876 cache-chain and 69,172 stress/temperature regression comparisons pass; seven compiled defects are rejected. All 222 reachable native bytes execute. A fresh serial build compiles every unit after earlier GCC process terminations; the tested object equals its final object. The other 851 prior nongenerated objects remain identical. Physical sensors and boot remain open.
The [ordinary C temperature sample writer](temperature-store-pure-c-review.md) removes its assembly and embedded pool while preserving stored bytes and diagnostics adding250 with uint32 wrap. All 43,226 direct, 576 writer/read/reset and 25,946 stress regression comparisons pass; seven compiled defects are rejected. All 244 reachable native bytes execute. The other 851 prior nongenerated objects remain identical. Physical sensors and boot remain open.
The [ordinary C stress sample writer](stress-sample-pure-c-review.md) replaces its assembly and embedded literal pool while sharing the existing hourly/stress owner. All 25,946 direct and 576 writer/read/reset comparisons pass; seven compiled defects are rejected. All 220 native instruction bytes execute. Other writer sections/relocations and 851 other nongenerated objects remain identical. Physical sensors and boot remain open.
The [temperature/stress layout completion](scalar-cache-layout-review.md) keeps existing timestamps contiguous with their cache owners, preserving the hourly/stress overlap. All 576 writer/read/reset and 876 prior-cache regression comparisons pass; three linked layout defects are rejected. All 852 prior nongenerated objects and import sets remain identical. Physical sensors and final startup/scatter placement remain open.
The [shared health-cache ownership fix](health-cache-ownership-review.md) unifies HR/HRV/SpO2 accessors and resets with sample-writer/latest-reader prefixes, removing 310 duplicate definition bytes. Normal composition now keeps contiguous cache/metadata groups under section garbage collection. All 864 writer/read/reset and 12 activity-reset comparisons pass; four compiled defects are rejected. The other 851 prior nongenerated objects and import sets remain unchanged. Physical behavior and final startup/scatter placement remain open.
The [ordinary C multicast entry](multicast-entry-pure-c-review.md) removes its caller-scratch restoration wrapper while preserving the opaque callback trampoline. All 6,997 direct and 192 publisher/queue/consumer comparisons pass; six compiled defects are rejected. All 202 native instruction bytes execute. The other 851 prior nongenerated objects, imports, manifest and state remain unchanged. Physical scheduling and boot remain open.
The [ordinary C retained diagnostic sink](retained-log-sink-pure-c-review.md) removes its variadic assembly bridge and frame worker. All 308 actual-formatter and 180 controlled-callback comparisons pass; eight compiled defects are rejected. All 146 native instruction bytes execute. The other 851 prior nongenerated objects, imports, manifest and state remain unchanged. Physical transport, retention and boot remain open.
The [ordinary C snapshot builder](crash-snapshot-builder-pure-c-review.md) removes its frame adapter and private helper. All 17,088 direct and 216 actual initializer/snapshot/CRC comparisons pass; eight compiled defects are rejected. All 350 head/tail instruction bytes execute. The other 851 prior nongenerated objects, imports, manifest and persistent state remain unchanged. Physical retention and boot remain open.
The [ordinary C retained-record initializer](crash-initializer-pure-c-review.md) replaces its frame adapter and consolidates the unlinked duplicate bridge. All 6,048 direct and 216 actual initializer/snapshot/CRC comparisons pass; ten compiled defects are rejected. All 104 native instruction bytes execute. The duplicate-unit removal leaves participating object counts unchanged; the other 851 prior nongenerated objects remain identical. The 736-byte getter and distinct 896-byte admission rule remain native. Physical retention and boot remain open.
The [ordinary C local-hour query](hour-index-pure-c-review.md) removes its frame bridge and private preparation helper using canonical calendar types. All 2,655 direct/average and 1,560 real C RTC/calendar/average comparisons pass; five compiled defects are rejected. All 30 native hour instruction bytes execute. Averaging code/relocations and FPSCR behavior remain unchanged, including its architectural saturation primitive. The other 852 prior nongenerated objects, imports and state remain identical; physical clock and boot remain open.
The [ordinary C synchronization-marker backend](sleep-sync-marker-pure-c-review.md) replaces header-match/acknowledgement programming assembly while preserving the sole 12-byte context owner. All 24,080 direct and 6,912 record/event-then-sync flash-model comparisons pass; nine compiled defects are rejected. All 228 native instruction bytes execute. The other 852 prior nongenerated objects, imports and persistent state remain unchanged. Physical flash and boot remain open.
The [ordinary C record-store caller and event](sleep-record-pure-c-review.md) remove the remaining assembly from that unit and close its literal-pool alignment dependency. All 31,104 direct, 3,456 full record/event flash-model and 288 scan/delete regression comparisons pass; ten compiled defects are rejected. All 416 native instruction bytes execute. Default linking uses compiler-provided alignment; 852 other prior nongenerated objects, imports and persistent state remain unchanged. Physical NOR and boot remain open.
The [ordinary C sleep-sector selector/fallback](sleep-sector-select-pure-c-review.md) replaces both selection and erase-fallback assembly. All 17,200 direct and 1,728 full record-store/flash-model comparisons pass; nine compiled defects are rejected. All 346 native instruction bytes execute. The other 852 prior nongenerated objects, imports and persistent state remain unchanged. That historical fixture aligned the retained parent assembly to four bytes; the subsequent record-caller C conversion closes that dependency. Physical NOR and boot remain open.
The [ordinary C sleep-sector finalizer](sleep-sector-finalize-pure-c-review.md) replaces completion-marker assembly. All 19,280 direct and 1,458 actual write/finalize-chain comparisons pass; eight compiled defects are rejected. All 192 native instruction bytes execute. The fixed target, unsigned minimum counter and live callbacks remain native; 852 other prior nongenerated objects, imports and persistent state are unchanged. Physical programming and boot remain open.
The [ordinary C sleep-sector write](sleep-sector-write-pure-c-review.md) replaces payload/header programming assembly. All 9,922 direct, 144 distinct-boundary mutation and 648 record-store-chain comparisons pass; eight compiled defects are rejected. All 508 native instruction bytes execute with actual CRC and memory-clear routines. The other 852 prior nongenerated objects remain identical; imports and persistent state are unchanged. Sector finalization, physical programming and boot remain open.
The [C sleep-header scan and delete-all](sleep-delete-c-review.md) closes sleep deletion through the existing C erase core. All 14,680 direct, 480 variable-partial-read and 972 actual clear-all-chain comparisons pass; eight compiled defects are rejected. All 186 reachable native instruction bytes execute. Failed-read/header-carry and byte-count-wrap behavior remains native; 852 other prior nongenerated objects and prior sections in the changed unit remain identical. Physical flash and boot remain open.
The [ordinary C sleep-sector erase](sleep-erase-pure-c-review.md) replaces the count, erase loop and event-thunk assembly. All 18,651 direct and 2,880 record-store recovery comparisons pass; seven compiled defects are rejected. All 66 native instruction bytes execute, 852 other prior nongenerated objects remain identical, and parent assembly code/relocations are unchanged. Imports and persistent state are unchanged; physical erase and boot remain open.
The [C clear-all storage orchestration](health-clear-c-review.md) closes the reset cache-clear entry and database accessor. All 18,432 direct and 54 actual-cache/database/memory comparisons pass; seven compiled defects are rejected. Existing cache and database owners are reused, and 851 other prior nongenerated objects remain identical. Sleep-history deletion is now explicit; physical erase and final boot remain open.
The [C native previous-state append adapter](state-append-c-review.md) closes the flash append import through one shared algorithm. All 17,370 stock/C, 17,922 prior-API regression and 768 actual parent-chain comparisons pass. Negative FAL failures stop later operations and overflowing lengths are rejected separately from stock-compatible cases. All 850 other prior nongenerated objects remain identical. Physical flash and final boot remain open.
The [C synchronized worker-exit path](worker-exit-c-review.md) closes the manager worker-exit import using existing task/flag owners. All 4,440 direct and 576 manager/status/payload/reset chain comparisons pass; all 392 native instruction bytes execute and eight compiled defects are rejected. All 850 prior nongenerated objects remain identical. The native previous-state append adapter becomes explicit, keeping the import count unchanged. Physical RTOS/storage behavior and final boot remain open.
The [C manager hardware-event dispatcher](manager-events-c-review.md) connects ordered worker-exit, reset, status and factory-clear policy, with a checked peer-delete wrapper and participating CMSIS reset primitive. All 10,530 dispatch, three peer-wrapper and 1,404 actual status-ring comparisons pass; nine compiled defects are rejected. All 848 prior nongenerated objects remain identical. The broad dispatch import closes and three real worker/health/assertion dependencies become explicit; physical reset and final boot remain open.
The [C NV store bootstrap](nv-bootstrap-c-review.md) closes the eight-slot class-restore dependency. All 10,080 stock/C comparisons and 756 full NV initialization-chain comparisons pass, alongside 22 malformed-header/class-size rejection cases and seven compiled defect controls. All 847 prior nongenerated objects remain identical. Stored size mismatches are deliberately skipped before CRC/copy; physical flash behavior and final boot remain open.
The [C NV startup initializer](nv-startup-c-review.md) closes the manager storage-initialization dependency, reusing the seven existing cached-class owners and KV port. All 3,840 direct, 128 actual port-chain and 2,048 dirty-scan regression comparisons pass; six compiled defects are rejected. All 845 other prior nongenerated objects remain identical; the shared-table unit retains identical code/data/normalized relocations. Store bootstrap remains an explicit import, leaving the import count unchanged.
The [C application manager](application-manager-c-review.md) connects the launch worker to hardware/task startup and its persistent event/watchdog loop. All 720 direct and 384 actual suspension-handshake comparisons pass; six compiled defects are rejected and the ready byte matches native cold initialization. All 845 prior nongenerated objects are unchanged. One worker import closes and five real lower services become explicit, leaving 65 application imports; physical scheduling, hardware behavior and final boot remain open.
The [ordinary C cached calendar logger](log-calendar-pure-c-review.md) removes its fixed assembly frame and uses initialized conversion storage. All 2,896 direct and 2,824 actual registered-backend-thunk comparisons pass; five compiled defects are rejected. The prefix declaration is corrected with identical object output; all 844 other nongenerated objects and imports remain unchanged. Physical RTC behavior and final boot remain unverified.
The [ordinary C connection-presence gates](connection-gates-pure-c-review.md) remove scratch-register assembly from both predicates. All 132,809 stock/C comparisons pass, including exhaustive handle values and the actual response, charge-event and notification-throttle callers; five compiled defects are rejected. All 844 other nongenerated objects and imports remain unchanged.
The [ordinary C reset-reason decoder](reset-decode-pure-c-review.md) removes its scratch-register assembly entry. All 23,426 direct and 2,160 actual startup/retained-reader/CRC comparisons pass; five compiled defects are rejected. Constant data, imports and all 844 other nongenerated objects remain unchanged. Physical reset/retention and final boot remain unverified.
The [C STACMD GPIO dispatcher](stacmd-void-c-review.md) replaces its raw-return assembly adapter and makes ignored transmit/recovery results void. All 479 stock/previous/C frame cases and four defect controls pass. The C gateway and pulse bodies retain their instruction bytes; one inter-bit ADD changes temporary register.
The [C charger predicates and status route](device-status-pure-c-review.md) remove scratch-register/frame handling from status queries and phone operation one. All 25,336 direct and 49,152 actual table/charger/header comparisons pass; five compiled defects are rejected. Imports and default record data are unchanged.
The [typed C BMA callbacks](bma-callbacks-pure-c-review.md) replace assembly-name aliases with SDK-compatible adapters and correct the FIFO delay prototype. All 19,168 interface/callback and 2,168 FIFO comparisons pass; five compiled defects are rejected. Six native BMA runtime units now have no inline assembly.
The [ordinary C QMA tap configuration](qma-tap-pure-c-review.md) removes its final private-frame wrapper. All 37,134 direct and 846 actual retry-graph comparisons pass, plus 144 fallback cases and five defect controls. Both native QMA runtime units now have no inline assembly.
The [C LIS routing and tap policies](lis-aux-pure-c-review.md) remove three private-frame bridges and align motion auxiliary types. All 136,808 stock/C comparisons, 108 unwritten-read cases and five defect controls pass. All seven native LIS runtime C units are now free of inline assembly; physical validation remains separate.
The [typed C LIS configuration](lis-config-pure-c-review.md) removes its entry and register-call assembly adapters. All 32,921 stock/C policy comparisons and 378 actual register-graph comparisons pass; five compiled defects are rejected. Only the configuration object and its manifest profile selection change.
The [ordinary C LIS register entries](lis-entries-pure-c-review.md) replace 22 assembly bridges. All 190,272 stock/C comparisons, 528 unwritten-read cases and 378 actual configuration-graph comparisons pass; five compiled defects are rejected. Other motion assembly and physical validation remain separate.
The [ordinary C QMA transport](qma-transport-pure-c-review.md) removes its chip/FIFO/callback assembly bridges and delay flag binding. All 16,385 direct and 16,435 actual bus/wrapper comparisons pass, plus 36 unwritten-byte cases; five compiled defects are rejected. Imports and persistent runtime data are unchanged.
The [C settings accessors and regulator route](system-settings-pure-c-review.md) remove three private-frame wrappers and close the settings table import. All 9,912 stock/C comparisons, 48 failed-read cases and 25,856 actual table/cache/header cases pass; five compiled defects are rejected. The architectural regulator SVC remains.
The [ordinary C power-control command](power-command-pure-c-review.md) removes its frame/tail assembly bridge. Direct and actual KV-field fixtures each pass 4,560 comparisons; five compiled defects are rejected. Post-delay command reads and post-callback handle reloads remain. Imports are unchanged.
The [ordinary C low-battery escalation](battery-low-pure-c-review.md) removes register/stack assembly constraints. Direct and actual KV-field fixtures each pass 7,360 comparisons; five compiled defects are rejected. Full stored records match while unused caller scratch bits are excluded. Imports remain unchanged.
The [ordinary C charger status entry](yhm-status-pure-c-review.md) removes the saved-scratch assembly wrapper. Direct and actual-transport fixtures each pass 27,648 stock/C comparisons plus 6,912 unwritten-read cases; three compiled defects are rejected. Imports remain unchanged.
The [ordinary C charger ladder entry](yhm-ladder-pure-c-review.md) removes its final assembly wrapper and stack-history dependency. All 26,720 stock/C pairs, 90 unwritten-read fallback cases and four defect controls pass. Only the ladder object changes; imports and multiplier bytes remain unchanged.
The [C response headers, shared serial getter and time providers](protocol-serial-c-review.md) remove seven assembly entry bridges and consolidate the serial accessor. Direct comparisons, cached consumers and touch regressions pass; failed cached reads have explicit C policies. Imports remain unchanged.
The [bounded C EUS receive reassembler](rx-reassembly-c-review.md) closes the missing BLE transport entry. All 1,358 stock/C sequence comparisons and thirteen C-only safety scenarios pass; fifteen compiled defects are rejected. Actual C CRC/memory/sender bodies execute, with all 422 reachable native instruction bytes covered. Emulated stock malformed input overwrites adjacent ACK state; the C capacity checks reject it and recover. New narrow state owners are authenticated, with four explicit C-only capacity bytes. All 841 prior nongenerated objects remain unchanged. Physical delivery and final boot remain unverified; the stock4063/4096 framing asymmetry was subsequently fixed in the range review below.
The [C buttonless DFU event policy](dfu-policy-c-review.md) closes the registered update-event callback and its disconnect helper. All 5,708 stock/C comparisons pass through the actual advertising configuration copy, connected iterator and typed S140 callback; thirteen compiled defects are rejected. All 446 reachable native instruction bytes execute; the remaining two-byte branch is independently unreachable from the legal entries. No state is added, and all 840 prior nongenerated objects remain unchanged. Physical disconnect, reset, DFU and final boot remain unverified.
The [C peer-manager event policy and bond diagnostic](peer-policy-c-review.md) close the registered BLE pairing/peer callback without new imports. All 4,775 direct stock/C comparisons and 56 actual-registration/delivery comparisons pass; eighteen compiled defects are rejected, and all 1,404 native instruction bytes execute. Existing BLE control/connection owners are reused with one authenticated two-byte last-peer owner. All 839 prior nongenerated objects are unchanged. SDK storage/security services and physical pairing remain modeled or unverified.
The [C touch-switch command entry](touch-switch-c-review.md) connects the actual system command table to one ordinary C handler body, with its previous public name retained as an alias. All 6,378 stock/C comparisons pass through direct and actual module-dispatch paths, covering all 184 native instruction bytes; eleven compiled defects are rejected. One assembly bridge and one unresolved import are removed. All 838 other prior nongenerated objects are unchanged, including the typed module object. No new state is introduced; final source linking and hardware remain open.
The [C glasses wear/display and deferred hardware policy](glasses-status-c-review.md) resolve both factory callback imports and implement their status producer and fast-mode scheduler helper. All 10,519 integrated stock/C comparisons and 1,696 GAP regressions pass; sixteen compiled defects are rejected and all 666 native instruction bytes in the four roots execute. Existing factory, touch and connection/parameter owners are reused with no new mutable state. All 838 prior nongenerated objects are unchanged. Final source linking and hardware behavior remain open.
The [C GAP observer and disconnect cleanup](gap-event-c-review.md) replace the broad GAP event import with the actual connection-slot writer, QWR assignment, role cleanup, ACK clear and PHY routing. All 1,696 integrated stock/C comparisons pass and eighteen compiled defects are rejected; all 1,910 native instruction bytes in the observer/ACK/reset ranges execute. Existing state owners are reused apart from one authenticated latch byte. All 836 prior nongenerated objects are unchanged. Two exact factory timeout callbacks remain explicit imports; final firmware linking and boot remain open.
The [C connection PHY update helper](connection-phy-c-review.md) adds the guarded typed S140 PHY path. All 55,440 stock/C comparisons and five boundary replays pass; six compiled defects are rejected. All 835 prior nongenerated objects remain unchanged. It adds no mutable state and leaves the import set unchanged; its GAP event caller remains open.
The [C peer-address, disconnect, power and report closure](peer-address-c-review.md) closes all eight lower consumer dependencies and removes the common header scratch-register assembly. All 5,494 direct, 4,641 consumer and 144 encoder/FIFO comparisons pass; twenty compiled defects are rejected. Existing GAP/battery ownership is reused and one zero-initialized21-byte connection-slot cache is added. The GAP event writer and final boot remain open.
The [C BLE connection event consumer](connection-consumer-c-review.md) replaces the broad queue consumer import with its full event policy and eight explicit lower hardware/service dependencies. All 3,993 direct, 3,993 actual-parameter and 144 encoder/FIFO comparisons pass; seventeen compiled defects are rejected. Queue ownership, target/advertising policy and security-request ordering are checked; real lower backends and final boot remain open.
The [C BLE parameter helpers and shared profile](connection-mode-c-review.md) supply the connection mode/update and delayed slow-mode paths, and remove the observer’s duplicate GAP profile byte. All 6,232 stock/C comparisons pass; thirteen compiled defects are rejected. SDK SVC gateways and the actual C observer/GAP/callback paths execute with lower services modeled. That helper review changes no imports; the subsequent consumer integration is recorded above.
The [C slider state machine and typed IQS callback](slider-state-c-review.md) close the main slider dependency. All 10,482 direct, 8,498 actual-gesture and 756 IQS event callback comparisons pass; sixteen compiled defects are rejected. Shared state is reused, seven remaining context initializers match stock, and all 831 prior nongenerated objects remain identical. Physical sensing and final boot remain unverified.
The [C slider velocity and release helpers](slider-support-c-review.md) add two verified leaves using the existing contact owner. All 21,398 stock/C comparisons pass; nine compiled defects are rejected. That leaf review changes no imports; its subsequent state-machine integration is recorded above.
The [C pending-tap timeout and gesture entry](touch-pending-c-review.md) close one touch dependency and replace the gesture assembly bridge with a C packet frame. All 3,956 direct and 1,496 actual gesture/timer-queue comparisons pass; eight compiled defects are rejected. Existing shared state is reused, and standard memory routines execute.
The [capacity-aware C BSN reader](bsn-reader-c-review.md) closes the hardware detector storage import. All 6,128 direct, 1,084 cached-class and 734 complete setup comparisons pass, alongside 13,813 C capacity/error checks; eleven compiled defects are rejected. Valid/erased records retain their behavior, malformed lengths use a bounded erased-value fallback, and the setup probe executes actual standard memory routines.
The [C IQS error audit and formatter entries](iqs-audit-c-review.md) close the recovery audit import and remove two assembly variadic bridges. All 1,354 direct audit, 1,108 formatter/port/registry, 2,916 formatter ABI and 224 retained-logger comparisons pass; thirteen compiled defects are rejected. Rate limiting, live state, channel statistics, cleared partial reads and defined empty-list behavior are verified. Private ABI identity and physical timing remain separate.
The [C touch model calibration and cached getters](touch-calibration-c-review.md) close three imports and remove three captured assembly entry bridges. All 68,238 direct, 2,542 cached-class, 752 configuration and 612 IRQ-path comparisons pass; thirteen compiled defects are rejected. Every lower/upper calibration byte pair is checked with exact binary32 results, while initialized private-frame fallbacks and modeled memory-provider limits are explicit.
The [C IQS configuration and model selector](iqs-configure-c-review.md) supplies the ten-transfer controller setup and twenty authenticated register-data records. All 1,644 direct, 806 actual-port/registry, and 612 IRQ/reset-path comparisons pass; twelve compiled defects are rejected. Live configuration/table changes and full-word divider selection are verified. Three real lower helpers become explicit as the configuration import closes.
The [C IQS recovery and reset policies](iqs-recovery-c-review.md) supply the IRQ recovery paths using existing state owners. All 5,848 direct, 1,348 actual event/port/registry, and 612 IRQ-path comparisons pass; twelve compiled defects are rejected. Saturating errors, retry exhaustion, close/reinitialization requests, register writes and live logging inputs are verified. The real lower audit/configuration imports replace the two recovery imports.
The [C cached hardware variant detector](hardware-variant-c-review.md) supplies the IQS board-model path. All 2,421 direct and 612 actual IRQ/port/registry comparisons pass, along with twelve IRQ private-buffer fallback checks; six compiled defects are rejected. Cold cache bytes and one-time BSN classification are verified. The real product BSN storage accessor replaces the detector import; the import count stays unchanged.
The [C IQS IRQ worker and float event path](iqs-irq-c-review.md) cover ten entries. All 1,968 direct and 612 port/registry-integrated cases pass; both passes check twelve private-buffer fallback cases. Twelve compiled defects are rejected. Distinct end/acknowledgement exits, raw signed selectors, averaging and late float callback arguments are verified. Three lower hardware policies become explicit as the worker import closes.
The [C IQS register ports](iqs-port-c-review.md) close the write-port import without new units or state. All 9,408 direct and 576 registry-integrated call pairs pass, plus 264 factory-chain cases; eight compiled defects are rejected. Existing transport sections remain identical, and the ignored address/option words and retained request behavior are verified.
The [C touch dispatcher and control adapters](touch-dispatch-c-review.md) cover fourteen native entries. All 5,328 direct and 264 actual bus/registry pairs pass; twelve compiled defects are rejected. Queue/IRQ-before-park order, recovery, factory precedence and cold fields are verified. One import closes and three lower hardware/tap dependencies become explicit.
The [C touch worker and callback registration](touch-worker-c-review.md) closes the worker import and exposes the dispatcher and slider state machine. All 859 stock/C pairs pass and ten compiled defects are rejected. Existing ready setter, power step, IRQ/event-post wrapper and allocation-fault C bodies execute in the tests; new narrow watchdog/callback words match cold RW.
The [C persistent peer restore](peer-restore-c-review.md) closes one import without adding state or dependencies. All 2,230 direct and 225 actual cached-KV/dirty-scan pairs pass, plus 40 defined short-read checks; ten compiled defects are rejected. Marker repair, fresh record reads, live write handles, optional outputs and address-header classification reuse existing owners.
The [C GAP identity and preferred-parameter setup](gap-identity-c-review.md) closes one import without new dependencies. All 1,984 direct and 132 actual formatter/SDK-state pairs pass; both passes check 21 defined partial-query fallback cases, and ten compiled defects are rejected. Narrow owners match cold RW, while successful address/name/configuration behavior preserves native ordering.
The [C BLE initialization and PM/DFU setup](ble-initialize-c-review.md) passes 2,320 direct cases and 53 actual GATT/QWR cases; ten compiled defects are rejected. The bootstrap import closes and three real GAP/event policies become explicit. Existing provider objects, including the worker after its declaration correction, remain identical.
The [C peripheral watchdog](peripheral-watchdog-c-review.md) closes one import with no new dependencies. All 2,768 direct cases and 144 actual SDK-count/C-availability cases pass; ten compiled defects are rejected. Counter wrap/log cadence, advertising recovery, timer rearming and the stock invalid-state assertion are preserved without a retained opcode word.
The [C advertising stop/restart policies](advertising-control-c-review.md) close two imports with no new dependencies. Direct and actual availability/status-adapter passes each cover 2,004 cases, and eight compiled defects are rejected. Handle reloads, stop error 8, startup continuation, gated result logging and status publication match stock within the valid SDK mode domain.
The [C BLE transmit-power policy](tx-power-c-review.md) closes one import without adding dependencies. Both direct and actual error-logger passes cover 2,000 cases; actual SDK state/atomic reads and error logging pass 344 further cases. Eight compiled defects are rejected. Power settings, connection eligibility, advertising availability and live handle reads use existing owners and the pinned SDK controller gateway.
The [C BLE worker and timer callbacks](ble-worker-c-review.md) pass 4,102 stock/C comparisons and reject eight compiled defects. Advertising precedence, live watchdog reads, callback logging, queue publication and suspend/fault behavior are covered. One worker import closes and seven lower BLE policies become explicit. The current user goal accepts open-toolchain builds without byte identity.
The [C task startup and BLE/touch lifecycle](task-startup-c-review.md) supply ordered creation, fixed native metadata and handle publication/failure behavior. All 32 startup pairs, 12 actual lifecycle startup pairs and 96 lifecycle/fault pairs pass; eight compiled defects are rejected. Two worker bodies become explicit, increasing application imports from 69 to 71.
The [C startup suspension barrier](task-barrier-c-review.md) uses existing live handle owners in the stock nine-worker order. All 240 ordered pairs and 54 actual handshake pairs pass; six compiled defects are rejected. Shared task-prefix declarations preserve all three consumer objects. Application imports remain 69.
The [pure C persistent-record updates](nv-update-pure-c-review.md) replace four assembly stack wrappers with defined C buffers. All 1504 direct triples, 128 actual cached-write/dirty-scan triples and 72 fallback cases pass; eight compiled defects are rejected. Manifest and application imports remain unchanged at 821 units/69 imports.
The [C NFC/charging dispatcher](nfc-dispatch-c-review.md) closes the worker dispatch import, preserving independent flag order, ID retries and live queue/state reads. All 6427 direct pairs and 30 actual worker/dispatcher pairs pass; ten compiled defects are rejected. The unused contextual charging-event copy is retired. Application imports decrease from 70 to 69.
The [C charged policy and NFC continuation](pmic-charged-c-review.md) fill the remaining PMIC policy path using existing owners and SDK providers. All 7741 direct pairs and 96 actual GPIO pulse pairs pass; ten compiled defects are rejected. The NFC dispatcher remains open and application imports remain 70.
The [C dock advertisement sender](dock-advertisement-c-review.md) closes the remaining dock reply import and corrects the parser to forward its phase explicitly. All 1232 direct pairs and 216 actual parser/sender/SDK pairs pass; seven compiled defects are rejected. Application imports decrease from 71 to 70.
The [C dock-frame policy](dock-policy-c-review.md) supplies heartbeat/reply policy, field-seen adapters and field control over existing SDK/scheduler providers. All 3646 direct pairs and 63 actual formatter pairs pass; ten compiled defects are rejected. The parser import closes and dock advertisement sending becomes explicit; application imports remain 71.
The [C mailbox receive gate](mailbox-receive-c-review.md) uses actual SDK read providers and isolates all 257 possible receive bytes from adjacent IRQ state. All 995 paired cases and 16 explicit fallback cases pass; seven compiled defects are rejected. One receive import closes and the dock parser becomes explicit; application imports remain 71.
The [C PMIC charge policy](pmic-charge-policy-c-review.md) supplies charge/temperature policy and its timer flag adapter using existing hardware owners. All 2058 direct pairs and 36 actual cancellation pairs pass; nine compiled defects are rejected. Its mailbox handler becomes explicit, increasing imports from 70 to 71.
The [C recurring PMIC retry callback](pmic-retry-c-review.md) fills a dependency of the remaining NFC flag dispatcher, rearming before signaling through the existing scheduler and shared task owner. All 288 direct pairs, 128 actual scheduler registrations and 64 expiry/dispatch/rearm roundtrips pass; five compiled defects are rejected. Application imports remain 70.
The [C battery initializer and ship-mode getter](battery-initialize-c-review.md) close the worker initialization import through existing battery and persistence owners. All 800 startup pairs, 96 getter pairs, 64 actual cached-reader pairs and explicit short/failed-read fallbacks pass; six compiled defects are rejected. Application imports decrease from 71 to 70.
The [C static mailbox update](st25-mailbox-c-review.md) closes the remaining ST25 setup register-update import. All 27648 stock/C pairs, 54 explicit fallback cases and the configuration integration pass; five compiled defects are rejected. Application imports decrease from 72 to 71.
The [C ST25 configuration policy](st25-configuration-c-review.md) supplies initialization, security/password, GPO and mailbox-read adapters using typed SDK fields. All 1440 direct pairs, 36 escaped-byte mutation pairs and 16 actual SDK-provider pairs pass; ten compiled defects are rejected. One initializer import is replaced by the explicit native mailbox RMW boundary; the total remains 72.
The [C NFC IRQ storm limiter](nfc-irq-monitor-c-review.md) closes the registered monitor callback through a seven-timestamp suppression window. All 10752 boundary pairs, 1024 seeded pairs, 168 mutation pairs and four actual setup/registered-callback sequences pass; eight compiled defects are rejected. Application imports decrease from 73 to 72.
The [C late NFC/charger setup](nfc-late-setup-c-review.md) supplies six setup/IRQ entries over the existing I2C5, YHM and battery owners. All 720 adapter pairs, 192 setup pairs and eight callback-use sequences pass; nine compiled defects are rejected. One setup import closes and two chip/monitor dependencies become explicit, increasing application imports from 72 to 73.
The [C recurring battery callback](battery-periodic-c-review.md) closes the periodic registration dependency through existing C flag and delayed-event providers. All 288 direct pairs, 64 scheduler registrations and 64 expiry/dispatch/rearm roundtrips pass, as do the actual worker consumer probes; six compiled defects are rejected. Application imports decrease from 73 to 72.
The [C NFC/charging task](nfc-charge-task-c-review.md) supplies create/stop and the sync/queue/watchdog/notification loop over the existing thread owner. All 32 lifecycle pairs, 528 worker pairs and 176 actual startup-sync pairs pass; eight compiled defects are rejected. Four hardware initialization/dispatch dependencies become explicit, increasing application imports from 69 to 73.
The [C worker suspension handshake](suspend-handshake-c-review.md) signals workers and waits through the existing shared acknowledgement owner. All 2688 direct pairs, 12 handle-mutation pairs, 1736 actual CMSIS pairs and 24 publisher/waiter pairs pass; eight compiled defects are rejected. Imports are unchanged; full manager startup and suspension remain open.
The [C SoftDevice resource bootstrap](softdevice-bootstrap-c-review.md) supplies the tag-1 notification queue and extended-connection-event setup using typed SDK calls. All 4512 direct pairs, 144 live RAM/mode pairs and 128 actual SDK configuration/enable pairs pass; eight compiled defects are rejected. Error logging returns and setup continues. Imports are unchanged; the manager startup dependency remains open.
The [C touch release callbacks](touch-release-pure-c-review.md) remove both assembly entry bridges while preserving fully initialized task messages and gesture records. All 2400 direct pairs, 24 mutation pairs, 240 actual-gesture integration pairs and 160 service-close caller pairs pass; six compiled defects are rejected. State/kernel bytes, imports and manifest are unchanged.
The [C console receive and tokenizer](console-c-review.md) supplies the manager RTT input path and a relocatable shared tokenizer cursor. All 372 tokenizer and 216 integrated receive pairs pass; four compiled defects are rejected. The tokenizer import is replaced by the explicit command-dispatch dependency.
The [C RTT receive driver](rtt-read-c-review.md) supplies locked and unlocked readers over the existing control block and native initializer. All 7792 warm and 1024 cold stock/C pairs pass, including live host write-offset changes; four compiled defects are rejected. The write graph and import sets are unchanged.
The [clock bootstrap normal-link integration](clock-bootstrap-link-review.md) enables the existing C constructor, backend table and second-change callback after 4400 constructor pairs, 128 direct callback pairs and 1152 actual timestamp/RTC-path pairs. Callback frames differ under the accepted ordinary C ABI; imports and all nongenerated object hashes stay unchanged.
The [C application launch lifecycle](application-launch-c-review.md) owns the RTOS launch/startup/stop routines and replaces the entry's absolute callback address with a relocatable C owner. All 216 stock/C pairs, 16 source-entry integration cases and four compiled defects pass. The manager worker becomes one explicit unresolved dependency; reset and physical boot remain open.
The [shared logging registry](log-registry-review.md) preserves the native 32 IDs, aliases SDK variables to that one owner and retains two extra SDK modules. All 2233 SDK/macro/getter executions pass, including 448 stock/C color pairs; three imports close. Dynamic record startup placement and logger backend output remain unverified.
The [fstorage registry layout](fstorage-registry-review.md) closes two boundary imports and registers the existing device-flash and FDS instances once each. All 640 stock/C busy comparisons and 64 actual facade lifecycle workflows pass. FDS cold callback identity, backend flash and final startup placement remain unverified.
The [shared SDK registry ABI repair](sdk-registry-abi-review.md) aligns SoftDevice, SoC and power users with the existing legacy iterator and closes ten registry imports. The old state-notifier loop is reproduced; 40 iterator masks, 40 notifier cases and 36 actual stack-to-BLE/SoC poll cases pass after repair. Empty power handlers and excluded product observers remain open.
The [BLE registry linker layout](ble-registry-link-review.md) closes eight boundary imports using section-relative symbols for the four existing priority ranges. Actual SDK poll/iterator execution passes 48 event scenarios and all 16 empty-range masks after final relocation; two linked boundary defects are rejected. All composed allocated bytes and relocations remain unchanged.
The [single DFU BLE registration](dfu-observer-owner-review.md) removes a duplicate SDK record while preserving all service code, state and other relocations. Seventy dispatch scenarios reproduce the old double DFU callback and verify the five-record stock inventory after the fix. Imports are unchanged.
The [stock Goodix disabled upload hook](goodix-upload-c-review.md) closes a hardware frame-processing import using its pinned C behavior. All 512 direct and 90 real call-site pairs pass; two data-access defects are rejected. No protocol behavior is invented.
The [stream logging ABI adapter](stream-log-abi-review.md) closes the remaining rate-reducer logging import with a four-byte tail branch to the existing SDK void provider. All 2367 paired reducer cases, 1024 direct ABI cases and three compiled defects pass; the reducer body is unchanged. SDK logging and physical timing remain modeled/unverified.
The [C persistent-class registry](nv-registry-c-review.md) closes two linker-span imports using the seven existing C handle owners. All 2048 stock/C scan comparisons pass, including handle replacement during writes; four compiled defects are rejected. Application imports decrease from 95 to 93.
The [charge-state notification C routine](charge-notify-c-review.md) replaces the assembly packet builder while retaining separate hardware queries and full-charge priority. All 2530 stock/previous/new cases and five compiled defects pass through actual event/header and PMIC state/status implementations with modeled services. Template bytes and imports remain unchanged; strict bootloader linking passes.
The [DFU authorization typed SDK calls](dfu-auth-sdk-c-review.md) replace two custom SVC wrappers while preserving partial-read history and exact busy retries. All 6746 stock/previous/new cases and five compiled defects pass, including 28 actual HVC/finalizer paths with modeled services. Other observer bodies and imports remain unchanged; strict bootloader linking passes.
The [radio/regulator typed SDK calls](radio-sdk-c-review.md) replace five custom SVC wrappers. All 1300 boundary pairs, 4800 stock/previous/new length cases, 5184 notification pairs, existing link/init regressions and five compiled defects pass with modeled services. Full-word notification lookup rejection remains before SDK narrowing. Other function bodies and imports stay unchanged; strict bootloader linking passes.
The [DFU backend typed SDK calls](dfu-backend-sdk-c-review.md) replace three handwritten SVC wrappers while retaining response frame aliases and caller-history bytes. All 4550 stock/previous/new cases, 1728 shared-state pairs and four compiled defects pass; SDK SVC executes with modeled services. Other backend bodies and imports remain unchanged, and strict bootloader linking passes.
The [DFU vector-table SDK C call](dfu-sdm-c-review.md) replaces bespoke SVC register assembly with the pinned Nordic typed API. All 3584 paired stock/C cases and three compiled defects tested in both paths pass; SDK SVC executes with modeled exception handling. Imports stay unchanged, all other payload inputs remain stable, and strict bootloader linking passes.
The [shared zero-divisor primitive and Bosch C arithmetic](divide-zero-c-review.md) close the architectural stream dependency and remove inline division assembly from the Bosch driver. All 7224 paired cases and five compiled defects pass with the actual zero provider linked. One UDIV primitive remains for zero only; enabled trapping and physical hardware remain unverified. One import closes, none are added, and strict bootloader linking passes.
The [FlashDB count-query C adapter](flash-query-pure-c-review.md) replaces the assembly entry and supplies a compatible bool callback without duplicating the counter. All 1740 focused pairs, 2016 integrated query pairs and five compiled defects pass. The actual iterator runs for 1008 initialized integrated pairs, with lower reads modeled; private frames and incidental saved arguments are excluded. Imports remain unchanged and strict bootloader linking passes.
The [ordinary C QMA interrupt entry](qma-irq-pure-c-review.md) removes its saved-register frame adapter because the status word is initialized before use. All 4278 paired stock/C cases and five compiled defects pass through actual read retry loops with modeled bus/delay/event providers. Other QMA sections, imports and source-plan selections remain unchanged; strict bootloader linking passes.
The [charger ladder C kernel](yhm-ladder-kernel-c-review.md) removes register pinning and direct SP access from the algorithm while retaining a small raw-entry fallback frame. All 23872 paired stock/C cases and five compiled defects pass across 32 FP modes; exact operands, FP status, selected indices and transport bytes match. Transport remains modeled. Imports and the existing qualified dispatch tail stay unchanged; strict bootloader linking passes.
The [pKey flash-store C provider](pkey-store-c-review.md) closes the missing 0x6b724 service through the existing shared FAL owner. All 1008 paired stock/C cases, 24 write/load round trips and six compiled defect controls pass. Binding, copying and CRC execute, with actual native heap in 28 cases; flash callbacks remain modeled. One import closes, none are added, and strict bootloader linking passes.
The [cached getter consolidation](record-read-consolidation-c-review.md) replaces a duplicate read/copy implementation with a thin call to the existing canonical getter. Its packed output view retains identical canonical object bytes. All 1240 stock/C cases and five compiled defect controls pass, including two-word returns and profile features. Imports are unchanged and strict bootloader linking passes.
The [STACMD frame C adapters](stacmd-frame-pure-c-review.md) remove scratch-register capture/restoration from read/write framing and bit-output copying. All 479 stock/previous/C protocol cases and four compiled defect controls pass through actual drivers with GPIO-only models, matching GPIO traces and NOP counts. Timing-driver bytes/relocations remain unchanged; physical timing is unverified. Imports are unchanged and strict bootloader linking passes.
The [reentrant newlib string formatter closure](newlib-format-closure-c-review.md) closes four imports using pinned C sources and a Nordic assertion adapter. All 4050 format calls, four assertion cases and four compiled defect controls pass; cached heap stabilizes after warming. Native public snprintf remains unchanged. Scheduler/fatal-handler boundaries are modeled; four imports close with none added and strict bootloader linking succeeds.
The [newlib shared-heap C adapter](newlib-heap-adapter-c-review.md) closes _malloc_r/_free_r and supplies calloc/realloc on the existing native allocator, retaining fatal native exhaustion. All 648 calls across 22 scenarios and six compiled defect controls pass, including 512 seeded operations, exact copy/zero lengths and full heap recovery. Scheduler boundaries remain modeled; two imports close with none added and strict bootloader linking succeeds.
The [pinned newlib math dependencies](newlib-math-deps-c-review.md) close frexp and __fpclassifyd without source modifications. An independent bit oracle checks 21504 patterns across every binary64 exponent and both signs; 43016 calls and four compiled defect controls pass without stock code or modeled providers. Default FP environment only; full formatting remains unfinished. Two imports close with none added, and strict bootloader linking succeeds.
The [record reinitialization C binding](record-reinit-binding-c-review.md) closes a missing name through the existing canonical 0x4c37c force entry, retaining identical allocated lifecycle bytes and relocations. All 2968 stock/C cases and four compiled defects pass through actual profile/failure callers and memclr; deeper authorization/initialization remains modeled. One import closes, none are added and strict bootloader linking succeeds.
The [cached health-settings C getter](record-read-c-review.md) closes the missing 0x735e0 service using explicit fallback register words. All 984 stock/C cases and four compiled defects pass, including actual cached KV/memcpy and the existing settings callback. Failed reads preserve fallback bytes; private scratch and physical persistence are excluded. One import closes, none are added and strict bootloader linking succeeds.
The [RTT CMSIS C wrapper](rtt-cmsis-c-review.md) replaces handwritten special-register assembly and register pinning with pinned CMSIS intrinsics, retaining the required BASEPRI instructions and mask policy. All 17756 stock/previous/C cases and five compiled defect controls pass, including actual cold initializer/ring/memory execution. Physical IRQ/debugger behavior remains unverified; imports are unchanged and strict bootloader linking passes.
The [health-settings persistence C wrapper](record-persist-pure-c-review.md) replaces its naked frame adapter with a local twelve-byte buffer. All 1728 modeled and 144 actual cached-KV/memcpy stock/previous/C cases and four compiled defect controls pass, preserving unaligned ordered copies, handle reloads and dirty flags. Private scratch contents and physical flash are outside this proof. Imports are unchanged and strict bootloader linking passes.
The [paired GXT310 temperature C routine](gxt-temp-pair-pure-c-review.md) removes register pinning and empty assembly constraints. All 64512 stock/previous/C cases and four compiled defect controls verify ordered halfword stores, overlapping pointers, channel selection, delay and cleanup with modeled providers. Imports remain unchanged and strict bootloader linking passes.
The [sensor math C APIs](sensor-math-api-c-review.md) close seven Goodix/quantized runtime imports through existing canonical algorithms. Normal math closure linking succeeds; 8248 API comparisons, 420 normal Goodix motion samples, 28 isolated quantized consumer cases and seven compiled defect controls pass without mapped stock code. Four selected FP profiles and isolated quantized source limit this proof.
The [paired GXT310 chip-ID C routine](gxt-id-pair-pure-c-review.md) removes register pinning and empty assembly constraints. The resulting compiled object is identical; 36864 stock/previous/C cases and four compiled defect controls verify ordered stores, channel selection, delay and cleanup with modeled providers. Imports remain unchanged and strict bootloader linking passes.
The [battery acquisition C paths](battery-acquisition-pure-c-review.md) remove register pinning and the naked averaging wrapper while retaining VPMIC/rectifier ownership, handle reloads, clipping, sample resets and integer scaling. All 1664 stock/previous/C cases and five defect controls pass, including actual paired/scaled consumer execution with modeled driver callbacks. Imports stay unchanged and strict bootloader linking succeeds.
The [named ADC C wrappers](adc-pure-c-review.md) remove two naked assembly wrappers while retaining explicit fallback-sample semantics and unchanged driver bodies. All 1728 stock/previous/C comparisons and four defect controls pass. SAADC callbacks are modeled; physical conversion and timing are unverified. Import sets are unchanged and the strict bootloader link passes.
The [C EABI conversion providers](eabi-conversions-c-review.md) close six sensor runtime imports, preserving recovered stock bit-conversion behavior through canonical C helpers. Verification passes 32,586 calls and five defect controls. Floating-point exception flags and nondefault rounding are unclaimed; Goodix consumer probes use unchanged source recompiled with function sections.
The [CMSIS RTC1 system timer](cmsis-rtc-timer-c-review.md) replaces the unresolved SysTick assumptions with matching 1024-Hz count/frequency APIs. It passes 7208 snapshots and 288 actual-IRQ catch-up scenarios (8944 calls), five defect controls and three configuration rejections. Two imports close; the rest of the CMSIS frontend remains unchanged.
The [RTC1 app-timer counter adapter](app-timer-counter-c-review.md) closes two imports through the pinned SDK counter contract and selected 1024-Hz FreeRTOS RTC1 setup. It passes 2708 calls with the SDK oracle and actual peer-manager rollover/expiry flow, four defect controls and three compile-time configuration rejections. It introduces no counter state or clock ownership; stock entry-address identity remains unclaimed.
The [assembly-free input GPIO wrappers](input-gpio-pure-c-review.md) pass 2960 open and 4608 read/callback/close cases plus four defect controls. Six existing driver/helper bodies retain identical bytes and relocations; private-frame and caller-clobbered register values are excluded. Import sets are unchanged and the bootloader still links.
The [assembly-free output GPIO wrappers](output-gpio-pure-c-review.md) pass 7906 stock/C/previous-wrapper comparisons and four defect controls. The original configuration and driver kernels remain unchanged; incidental R3/private-frame state is outside the typed C contract. Import sets are unchanged and the bootloader still links.
The [assembly-free NFC identity path](nfc-pure-c-review.md) preserves its byte-output C contract in 15872 stock comparisons and 480 actual ST25 driver/binding cases, plus four defect controls. Incidental R3/upper-scratch/private-frame state is explicitly outside that contract. Import sets are unchanged and the bootloader still links.
The [C bootloader reset body](boot-reset-c-review.md) replaces the SDK assembly data-copy/startup sequence while retaining the vector/exception unit. It passes 960 handoff cases across 30 layouts, the same SDK baseline cases, 16 production-vector/layout cases and four defect controls. The strict bootloader link succeeds with 1536 flash bytes remaining; SystemInit/main and physical boot remain outside that execution proof.
The [persistent profile-record update](record-update-c-review.md) now uses ordinary C and passes 360 controlled-provider cases plus 512 real-validator/comparison cases, including 256 actual event-callback cases, and four defect controls. Import sets are unchanged; the strict bootloader link still succeeds.
The [vendor DFU integration probe](vendor-dfu-c-review.md) accepts all 14 preserved official init packets through the actual signature path and 42 chunked ingestion cases. It rejects 42 authentication mutations and checks malformed/bounded inputs. The actual C hash path accepts the full 646408-byte reference application and rejects a one-bit change. Physical and full DFU activation remain outstanding.
The [ECDSA exceptional-point correction](boot-ecc-complete-c-review.md) fixes the observed generator/negative-generator and accumulator failures. The final ELF passes 213 signature checks and 224 independent group-law cases plus four compiled defect controls and the prior-upstream regression. All 776 prior payload objects are unchanged. It links within the same flash region with 1552 bytes remaining.
The [bootloader portable-C ECDSA route](boot-ecc-c-review.md) closes the remaining crypto imports and permits a strict GNU final ELF link within the existing 24 KiB region. The original route exposed a curve-generator-key failure, subsequently corrected and tested above. Physical and positive vendor-package validation remain outstanding.
The [bootloader C SHA-256 backend](boot-sha256-c-review.md) removes three proprietary hash imports using pinned SDK C sources. It passes 154 streaming cases and 27,100 emulated calls plus two defect controls; all 696 application objects are unchanged. The strict GNU layout link leaves two crypto code dependencies.
The [bootloader C startup entry](boot-start-c-review.md) now clears BSS and calls main after the pinned SDK reset handler copies data and runs SystemInit. It passes 640 handoff cases across 20 memory layouts plus six defect controls; all 776 prior objects are identical. The missing runtime entry closes and BSS-end linker metadata becomes explicit.
The [bootloader C runtime providers](boot-runtime-c-review.md) close seven memory/shift imports without new dependencies. They pass 3,551 checked runtime calls, including 512 stock application comparison calls and 209 actual nanopb decode cases, plus eight defect controls. Comparison code is shared without application string state; unrelated existing sections remain unchanged.
The [device boot dispatcher](device-initcalls-c-review.md) now participates in composition and connects all thirteen existing registration providers to application startup. It passes 174 stock/C cases and eight runtime defect controls; all 768 other objects are identical, and the boot-constructor dependency closes without new imports.
The [persistence/export event adapter](persist-event-c-review.md) now uses ordinary C and passes 1,948 stock comparisons across the log and EP integrations, plus eight defect controls. All 768 other objects are identical; only this adapter body changes in the shared object. State and import sets are unchanged.
The [EP storage initialization and cursor scan](ep-init-c-review.md) now close the guard initialization dependency in C and pass 1,024 stock/C cases plus eight defect controls. Existing storage, flush and guard bodies execute together; all 768 prior objects are identical. No state or lower imports are added.
The [EP storage read/write/erase wrappers](ep-storage-c-review.md) now close three dependencies in C and pass 7,505 stock/C cases plus eight defect controls. The wrappers execute with the actual flush/guard paths; all 767 prior objects are identical. No new imports are added.
The [EP ring flush and sector preparation](ep-flush-c-review.md) now use C and pass 3,808 stock/C cases plus eight defect controls. The authenticated cursor halfword reuses the existing status-ring owners; all 766 prior objects are identical. The flush dependency closes and storage read/write/erase become explicit.
The [EP export guard and poll/force entries](export-guard-c-review.md) now use C and pass 1,668 stock/C cases plus eight defect controls. Stock startup authenticates the four narrow state owners; all 765 prior objects are identical. The poll event closes and the initialization/flush dependencies become explicit.
The [integrated flash-log path](log-chain-review.md) passes 920 stock comparisons and eight cross-component defect controls. Actual cache extraction, memcpy, export-state access, periodic controller, initialization and writer execute together; reconstructed execution is prohibited from entering stock instruction addresses. Physical flash and RTOS services remain modeled.
The [flash-log initializer](log-init-c-review.md) now closes its dependency in C and passes 2,992 stock/C cases plus eight defect controls. All 764 prior objects are identical; no state or lower imports are added.
The [flash-log sector writer](log-writer-c-review.md) and sector-count accessor now use C and pass 1,972 stock/C cases plus eight defect controls. Stock initialization confirms the narrow state owners; all 763 prior objects are identical. The writer dependency closes and initialization becomes explicit.
The [periodic flash-log controller](log-persist-c-review.md) now uses C and passes 1,998 stock/C cases plus eight defect controls. Stock initialization confirms its last-tick word and 4 KiB snapshot; all 762 prior objects are identical. Its event dependency closes and the flash writer becomes explicit.
The [wear/charge timer callback](wear-charge-timer-c-review.md) now closes its dependency in C and passes 7,864 stock/C cases plus eight defect controls. All 761 prior objects are identical; no state or lower dependencies are added.
The [wear/charge transition](wear-charge-c-review.md) now uses C and passes 4,048 stock/C cases plus eight defect controls. Stock startup authenticates the new status-byte and timer-word owners; all 760 prior objects are identical. The event-service dependency closes and its timer callback becomes explicit.
The [temperature mode event adapter](temperature-mode-event-c-review.md) now uses C and passes 4,152 stock/C cases plus eight defect controls. All 759 other objects are identical; only this adapter body changes in the shared object. No state or imports are added.
The [heart-rate mode and measurement event adapters](hr-events-c-review.md) now use C and pass 9,486 stock/C cases plus sixteen defect controls. All 759 other objects are identical; only these two adapter bodies change in the shared object. No state or imports are added.
The [oxygen mode and measurement event adapters](spo2-events-c-review.md) now use C and pass 2,244 stock/C cases plus sixteen defect controls. All 759 other objects are identical; only these two adapter bodies change in the shared object. No state or imports are added.
The [stress mode and enable event adapters](stress-events-c-review.md) now use ordinary C and pass 2,772 stock/C cases plus sixteen defect controls. All 759 other objects are identical; only these two adapter bodies change in the shared object. No state or imports are added.
The [temperature measurement event adapter](temperature-event-c-review.md) is now ordinary C. Its combined path with the one-shot controller passes 1,240 stock/C cases and eight defect controls. All 759 other objects are identical; only this adapter body changes in the shared object, with no new state or imports.
The [temperature one-shot control](temperature-once-c-review.md) closes the measurement-start event dependency in C using existing shared state. It passes 700 stock/C cases and eight defect controls; all 759 prior objects are identical.
The [stress controls](stress-control-c-review.md) close two event dependencies using C authorization enable, mode transition/setter and hourly timer callback. They pass 1,458 stock/C cases and eight defect controls; stock initialization confirms the eight-byte owner and all 758 prior objects remain identical.
The [SpO2 once-result callback](spo2-once-result-c-review.md) now closes its controller dependency using existing predicate/calibration and integer support. It passes 5,116 stock/C and mixed timing/control cases plus eight defect controls. All 757 prior objects are identical; no state or lower imports are added.
The [SpO2 once/mode controls](spo2-control-c-review.md) close two event imports and expose the once-result callback. They pass 1,254 direct/adapter/lifecycle cases and eight defect controls. Stock startup authenticates the third slot used by initial mode 2; 755 prior objects are identical and only four zero owner bytes are added, with existing code/relocations unchanged.
The [sleep low-power handler](sleep-low-power-c-review.md) now closes its event import using the canonical sleep owner. It passes 1,576 direct/adapter/shared-transition cases and eight defect controls; all 755 prior objects are identical. No new state or lower imports are added.
The [HR timing scheduler/result/timeout](hr-timing-c-review.md) now close the timing callback import using shared owners. They pass 3,024 direct/mixed cases, 2,328 actual configuration/KV integration cases and eight defect controls. The consumed NV flag and native record depth match; irrelevant unwritten private scratch is excluded. All 754 prior objects are identical.
The [HR mode transition and setter](hr-mode-transition-c-review.md) close the mode event import and recover the fifth handle slot used by initial mode 4. They pass 2,340 direct/mixed cases, 4,302 controller/result regressions and eight defect controls. Stock startup confirms the 20-byte owner; 752 prior objects are identical and the changed owner retains all existing allocated code/relocations. The timing callback remains an explicit dependency.
The [one-shot HR result and range check](hr-once-result-c-review.md) close the result callback import and execute with the C controller and canonical state owners. They pass 2,790 direct/mixed cases plus eight defect controls; all 752 prior objects are identical. Physical stream/event delivery remains unproved.
The [one-shot HR stream control](hr-once-control-c-review.md) now uses C and the existing HR/HRV state owners. It passes 1,512 direct, event-adapter and teardown/release sequence cases plus eight defect controls. All 751 prior objects are identical; the control import closes and the HR result callback becomes explicit.
The [five native eight-byte record functions](gomore-record8-c-review.md) close both health-enable record imports with no new state or dependencies. They pass 1,557 stock/C primitive and actual health-enable/adapter cases plus eight defect controls. All 750 prior objects are identical; validation, selector/commit overlap ordering and outer-adapter status conventions are preserved.
The [health-enable event and settings toggle](health-enable-c-review.md) now use C through the actual byte-truncating callback. They pass 1,344 direct/callback/mixed cases and eight defect controls, with all 749 prior objects identical. One event-service import closes and two algorithm-record providers become explicit.
The [explicit activity refresh C handler](activity-explicit-c-review.md) closes one registered event import using the existing accumulator owner. It passes 822 direct/repeated and 72 mixed periodic/explicit cases plus eight defect controls. All 748 prior objects are identical; no new state or lower imports are added.
The [sleep vivo probe C path](sleep-vivo-probe-c-review.md) closes the starter import and implements its timer callback. It passes 1,344 direct/repeated sequences, 840 report/shared-state integrations and nine defect controls. All 747 prior objects are identical; the probe flag reuses the canonical sleep owner and the adjacent four-byte timer has its authenticated zero initializer. Timer/authorization services and physical sensing remain separate boundaries.
The [sleep result report and shared activity-mode state](algo-sleep-report-c-review.md) close the report dependency and remove one duplicate state byte. The report/getter/default-mode/force-wake paths pass 744 direct and mixed cases plus 1,264 output-dispatcher integration cases and eight defect controls. All 744 other prior objects remain identical; the two changed callers retain allocated code bytes with shared-state relocation names. The vivo probe starter is the new lower dependency.
The [activity accumulator C path](activity-accumulator-c-review.md) closes the activity output import and owns the authenticated 24-byte counter/bucket state. It passes 822 direct cases, 1,264 actual output-dispatcher integration cases and nine defect controls; all 745 prior objects remain identical. Clock/mode/event boundaries and physical persistence remain separate.
The [sensor output dispatcher](gomore-sensor-output-c-review.md) now connects the accelerometer/raw-HR ready gate to C output lifecycle handling. It passes 1,264 direct cases, 678 actual timestamp/failure/completion-helper integration cases and ten defect controls. All 744 prior objects are identical; one dispatcher import closes and activity accumulation/sleep reporting become explicit lower imports.
The [acknowledgement registry C paths](ack-registry-c-review.md) close two imports using the existing shared table, sequence and mutex owners. They pass 372 direct/mixed cases, 956 event-send and 870 packet-flush integration cases plus eight compiled defect controls. All 743 prior objects are identical. Mutex/tick/logging/free services and the transport backend remain modeled boundaries in these new replays.
The [event-post and protocol C paths](health-event-post-c-review.md) close five lower imports and expose two acknowledgement registry providers. They pass 956 direct stock/C cases, 870 flush-through-send integration cases and six defect controls; 741 prior objects remain identical and the three other encoder assembly bodies retain their allocated bytes. Registry internals now have the subsequent C review above; physical transport remains unproved.
The [event-post and protocol C paths](health-event-post-c-review.md) close five lower imports and expose two acknowledgement registry providers. They pass 956 direct stock/C cases, 870 flush-through-send integration cases and six defect controls; 741 prior objects remain identical and the three other encoder assembly bodies retain their allocated bytes. Registry internals now have the subsequent C review above; physical transport remains unproved.
The [four packet-flush C paths](health-packet-flush-c-review.md) replace unresolved flush imports with C packing/allocation/reset logic, exposing five lower event-post/sync-field providers. They pass 870 direct and 612 actual merge-to-flush cases plus eight defect controls. Caller/merge allocated bytes are unchanged, with twelve intended relocation replacements; 739 other objects remain identical.
The [four offline merge C paths](health-offline-merge-c-review.md) close four imports and reuse shared queue/builders. They pass 612 stock/C cases, including mixed enqueue/consume flows and provider-time state mutation, plus eight defect controls. Four caller relocations change; allocated bytes and 739 other objects remain identical. Packet-flush bodies remain unresolved.
The [offline consume/empty and builder-reset C paths](health-offline-consume-c-review.md) close eight imports through twelve caller relocation replacements, with existing allocated bytes unchanged. They pass 2,576 direct/mixed-sequence cases, 144 actual native flush-caller cases and six defect controls; 738 prior objects remain identical. Queue merge and packet-flush bodies remain unfinished.
The [clock-invalid guards and offline enqueue C paths](health-offline-enqueue-c-review.md) close four imports and own the recovered bounded rings/cursors. They pass 2,244 direct and 830 reader/hour integration cases plus six defect controls; stock decompression confirms cursor initializers. All 738 prior objects remain identical.
The [time-transition storage C callback](health-time-storage-c-review.md) resolves the second database subscription, reusing replay/reset/record providers for backward-time wipe, first-valid-time recovery, wrapped local-day reset and four-field timestamp clamping. It passes 385 direct and 457 registered-callback integration cases plus six defect controls; all 737 prior objects are identical.
The [hour-boundary storage C path](health-hour-storage-c-review.md) resolves one subscription callback with six cache readers and two missing resets. It passes 794 direct and 447 registered-callback integration cases plus six defect controls; all 736 prior objects are unchanged. Four clock-invalid record dispatch providers are now explicit, increasing imports by three.
The [retained snapshot restore and shared hourly/stress state](crash-snapshot-restore-c-review.md) now use C and a single canonical 120-byte state owner, removing the snapshot import and 48 bytes of duplicate allocation. Restore/helpers/query pass 1,904 direct cases, 417 startup cases and eight defect controls; average, daily initialization and replay regressions pass another 4,788 cases.
The [daily health-record replay](health-daily-replay-c-review.md) and six cache writers now use C, resolving the replay import. Shared C storage/accessors pass 1,620 direct cases, 417 startup integration cases and four defect controls; 732 prior objects remain identical and the temperature accessor is the only changed prior object.
The [health-database C startup](health-db-startup-c-review.md) resolves the service initializer, reuses native descriptor/event owners, and supplies typed lock/time callbacks with the recovered static mutex allocation. It passes 465 stock/C cases and four defect controls; all 732 prior objects are unchanged. Four deeper replay/subscription/snapshot imports become explicit.
The [retained crash-time C helpers](crash-time-c-review.md) add prerequisites for health-database startup. They pass 1,230 direct stock/C cases, 128 stock-startup integration cases and four defect controls. Existing instructions/data/relocations and import sets are unchanged; full DB startup now has the C provider reviewed above.
The [sleep-storage FAL initialization](sleep-storage-init-c-review.md) resolves the missing service-startup provider through the existing context owner. Success/partial-failure/logging behavior passes 4,320 stock/C cases and four defect controls; all 731 prior R1 objects remain unchanged.
The [motion IRQ notification C ABI](motion-irq-pure-c-review.md) removes the assembly branch adapter and gives all interrupt table entries compatible void prototypes. Actual product tables/callbacks pass 1,216 stock/C cases and four defect controls; imports are unchanged.
The [sensor calibration C records](sensor-calibration-pure-c-review.md) replace two naked calibration entry bridges with explicit C storage under the valid-record precondition. Both readers pass 4,096 stock/C/cache-chain cases and four defect controls; extraction bodies and imports are unchanged.
The [GXT310 average C ABI](gxt-average-pure-c-review.md) removes register constraints and inline assembly from averaging. It passes 10,240 stock/C comparisons through actual C channel adapters and four defect controls. The obsolete 48-byte exact selection is retired; normal imports are unchanged.
The [GXT310 read/trigger C ABI](gxt-read-trigger-pure-c-review.md) replaces two naked entry bridges with explicit C transfer words. It passes 66,208 read and 8,448 trigger comparisons plus four defect controls; other module instructions and relocations are unchanged. Imports are unchanged.
The [temperature reducer C workspace](temp-reduce-pure-c-review.md) removes fixed registers, inline assembly and stack-address helpers. Sampling, trimmed arithmetic, calibration and logs pass 36,720 stock/C comparisons and four defect controls; imports are unchanged.
The [nv_r1 configuration C accessors](device-config-c-review.md) resolve four factory/sensor dependencies using the existing 124-byte cached class. All 2,304 scenarios agree across stock, direct C and the actual C cache/memory chain; four defects are rejected and all prior R1 objects are unchanged.
The [FreeRTOS task suspension](task-suspend-c-review.md) resolves the CMSIS suspend import using the notification-aware TCB and existing list owners. Event unlink, notification state, unblock reset and startup paths pass 1,728 cases and four defect controls; prior notification-module code and relocations are unchanged.
The [FreeRTOS task resume](task-resume-c-review.md) resolves the CMSIS resume import using existing suspended/pending/ready-list owners. Eligibility, critical placement and priority yields pass 1,080 cases and four defect controls; previous task-wait instructions and named relocations are unchanged.
The [RTC backend C ABI](clock-port-pure-c-review.md) removes the port unit's fixed-register and empty assembly constraints. Wrapper forwarding/status behavior passes 256 stock/C cases; request code is unchanged. Two obsolete exact-byte selections are retired from the optional hybrid comparison plan; imports are unchanged.
The [FreeRTOS periodic delay](delay-until-c-review.md) resolves the CMSIS delay-until import using the existing delayed-list helper. Tick-wrap/list/yield behavior passes 1,800 cases and four defect controls; prior task-wait instructions and named relocations are unchanged.
The [FreeRTOS queue registry](queue-registry-c-review.md) resolves both CMSIS registry imports in a separate configured C owner. It passes 7,203 operation sequences, 28,812 mutations and 86,436 queries; all prior R1 objects and the native delete contract remain unchanged.
The [FreeRTOS stack watermark](stack-watermark-c-review.md) resolves the CMSIS stack-space import using the existing TCB stack pointer. The fill-byte scan passes 12,624 cases and four defect controls; previous task-query code and relocations are unchanged.
The [battery voltage/report C ABI](battery-report-pure-c-review.md) removes NOP layout padding and scratch-register restoration from the voltage service and two report units. Refresh gating, packet bytes, handle reload and log/dispatch behavior pass 1,431 stock/C comparisons. Imports are unchanged.
The [stuck-charge recovery C ABI](battery-recovery-pure-c-review.md) removes all register constraints, stack helpers and inline assembly from recovery. Charging decisions, live state and logs pass 3,968 paired stock/C cases; incidental scratch registers and private stack aliases are retired. Imports are unchanged.
The [FreeRTOS unordered event wait](rtos-unordered-wait-c-review.md) resolves the event-group wait import using the existing delayed-list helper. Actual C list routines pass 7,200 cases; four defect controls are rejected and prior module instructions and relocations are unchanged.
The [FreeRTOS stream-buffer support APIs](rtos-stream-support-c-review.md) resolve timeout-snapshot and notification-state imports using the existing tick/TCB owners. Critical ordering and state/value preservation pass tests; old module code and source prefixes remain unchanged.
The [FreeRTOS queue query APIs](rtos-queue-query-c-review.md) resolve two CMSIS imports using the existing native Queue_t and pinned kernel bodies. Critical-section snapshot tests pass; all 28 pre-existing mutex-kernel instruction sections and named relocations are unchanged.
The [FreeRTOS task/timer query APIs](rtos-query-c-review.md) resolve three CMSIS imports using pinned kernel C and existing native layout contracts. Priority critical-section behavior passes replay; the existing timer-ID function is unchanged.
The [standard C memory APIs](memory-api-c-review.md) resolve three BLE/formatting imports by sharing native C comparison/padded-copy routines and adding bounded byte search. The subset links without native bindings; the other 727 objects are unchanged.
The [battery ADC filter C workspace](battery-filter-pure-c-review.md) removes fixed registers, stack helpers and inline assembly. Five-sample sequencing, live context changes, post-close mutations and unsigned calibration pass stock replay; imports are unchanged.
The [PMIC system-tracking C status ABI](yhm-track-pure-c-review.md) removes register bindings and inline assembly from set/clear bodies. Both operations pass stock replay; compatibility thunk bytes and named relocations are unchanged. Imports are unchanged.
The [ship-control startup C loop](ship-init-pure-c-review.md) removes register bindings and manual Thumb-pointer arithmetic. Handle reload, operation and 200 calibrated-delay calls pass replay; the delay primitive remains unchanged. Imports are unchanged.
The [motion IRQ cache C ABI](motion-cache-pure-c-review.md) removes register constraints and context-base arithmetic from peripheral bindings. Repeated cache/registry-mutation replay passes; other binding functions are unchanged. Imports are unchanged.
The [TWI packet/register/legacy C chain](twi-write-chain-c-review.md) now executes together through the SDK boundary. Legacy TX register bindings are removed; write and read replay pass, including the repaired length-80 buffer. Imports are unchanged.
The [TWI register-write C buffer repair](twi-register-write-pure-c-review.md) removes the remaining register/stack constraints from the adapter unit and fixes length-80 saved-R4 corruption with an explicit 81-byte buffer. Payload/status replay and four defect controls pass; imports are unchanged.
The [hardware TWI packet-write C status ABI](twi-write-pure-c-review.md) removes the remaining assembly and stack helpers from the packet-operations unit. Modeled and actual short-transmit replay pass; register-write length-80 handling remains separate work. Imports are unchanged.
The [TWI register-read C status ABI](twi-register-read-pure-c-review.md) removes read-adapter register and stack constraints. Direct, actual-transmit and packet-chain replay pass; write-adapter instruction sections remain unchanged. Imports are unchanged.
The [hardware TWI read C status ABI](twi-read-pure-c-review.md) removes read-wrapper register and stack constraints. Direct and register-adapter replay pass; packet-write instruction sections are unchanged. Imports are unchanged.
The [touch ready-reader C status ABI](touch-ready-pure-c-review.md) removes the remaining inline assembly and register bindings from the transport unit. Low-byte readiness and complete probe sequencing pass stock replay; imports are unchanged.
The [touch identity C status ABI](touch-probe-pure-c-review.md) removes the remaining register bindings and inline assembly from the probe. Polling, low-byte result and cleanup pass stock replay; imports are unchanged.
The [PMIC charger C ABI migration](pmic-pure-c-review.md) removes register bindings, stack helpers and inline assembly from charger decoding and byte commands. Charger decisions and transport byte/status behavior pass replay; imports are unchanged.
The [ship-mode GPIO C ABI migration](ship-pure-c-review.md) removes all fixed-register declarations, stack helpers and inline assembly from the GPIO/pulse unit. MMIO effects and delay order pass stock replay; scratch-register returns are retired. Imports are unchanged.
The [watchdog C sampling contract](watchdog-pure-c-review.md) removes the remaining fixed-register declarations and empty assembly from the manager. Actual sample-provider and list-helper replay passes; the BASEPRI compiler intrinsic remains. Imports are unchanged.
The [RTC open C ABI migration](rtc-open-pure-c-review.md) removes the remaining fixed-register declarations and empty assembly from the lifecycle unit. Status, configuration and typed-dispatch behavior pass replay; incidental scratch-register returns are no longer part of this C API. Imports are unchanged.
The [cached/flash authorization key reader](health-key-reader-c-review.md) now uses C through startup, resolving its import. Engine parameter setting and initialization remain unfinished.
The [health authorization coordinator](health-authorize-c-review.md) now uses C through lifecycle startup. Its import resolves, exposing the unfinished key reader and parameter setter. Engine initialization also remains unfinished.
The [device-ID shared cache flag](identity-shared-state-review.md) now uses the authorization state owner. Imports are unchanged.
The [cached health profile and validation](health-profile-c-review.md) now use C through lifecycle startup. The profile import resolves; authorization and engine initialization remain unfinished.
The [health key and previous-state recovery](health-storage-c-review.md) now uses C through lifecycle startup. The restore import resolves, with three lifecycle engine providers still unfinished.
The [health engine mode/profile activation](health-engine-modes-c-review.md) now uses C through lifecycle startup, resolving both activation imports and sharing the checked slot-transition implementation. Four lifecycle engine providers remain unfinished.
The [health backward-time adapter and force reinitialization](health-time-reset-c-review.md) now use shared C providers through the lifecycle coordinator. The event-adapter import resolves; six native engine boundaries remain unresolved.
The [health lifecycle coordinator](health-lifecycle-c-review.md) now has a C provider through startup. Its import resolves while seven lower native engine/event dependencies become explicit; the total application import count rises by six. Engine closure and hardware initialization remain unfinished.
The [retained health crash recovery helpers](crash-recovery-c-review.md) now have shared C providers, source-only subset linkage and stock lifecycle integration replay. Imports are unchanged; the lifecycle root now has the C provider reviewed above.
The [touch identity probe](touch-probe-c-review.md) now uses C control flow without fixed counter/register constraints, reducing its compiled frame by eight bytes. The real R3 boundary bindings remain; imports are unchanged.
The [touch read/write request wrappers](touch-request-pure-c-review.md) now use ordinary C without register-binding or empty inline assembly constraints. Transport and identity replay passes; imports are unchanged. The separate ready-reader R3 adapter remains.
The [accelerometer classifier root](gomore-accel-features-c-review.md) now has a C provider and its classifier subset links without native bindings. This removes the classifier import. Broader firmware and device validation remain unfinished.
The [native-ABI autocorrelation kernel and wrapper](gomore-autocorrelation-native-c-review.md) now have a shared C implementation and C lower utilities. The checked vendor API delegates to it. Imports are unchanged; the classifier root now has the C provider reviewed above.
The [autocorrelation C approximation corrections](gomore-autocorrelation-c-review.md) fix stock-derived threshold, sign and wrap behavior. The later native C provider reviewed above closes this algorithm subset; comparison-flag parity and complete firmware closure remain unfinished. Imports are unchanged.
The [accelerometer crossing-period estimator and byte comparator](gomore-accel-period-c-review.md) now use C, closing one application import. Its estimator subset links without native bindings or unresolved symbols; classifier and autocorrelation closure remain unfinished.
The [accelerometer integer IIR and transition accumulator](gomore-accel-period-helpers-c-review.md) now use C, with direct, live native-period and focused classifier replay. Targeted native-input search supplies initialization and initialized-update coverage; the parent period estimator now has the C provider reviewed above.
The [accelerometer crossing baseline and dispatcher](gomore-accel-crossing-c-review.md) now use C, preserving native period scratch addresses and entry depth. The native period estimator now resolves to C; autocorrelation and classifier closure remain unfinished.
The [accelerometer axis gate and fixed six-channel score](gomore-accel-axis-score-c-review.md) now use native-ABI C providers with direct and classifier replay. The crossing dispatcher now has the C provider reviewed above; autocorrelation and classifier closure remain unfinished.
The [accelerometer circular predicates and recent history](gomore-accel-ring-predicates-c-review.md) now use four shared C providers, checked wrappers and actual classifier replay. The classifier root and spectral dependencies remain unfinished.
The [accelerometer classifier mean, crossings and fixed linear decision](gomore-accel-class-helpers-c-review.md) now use C with direct tests and focused native-classifier replay. The classifier root and its remaining spectral dependencies stay unfinished.
The [accelerometer preprocessing stage](gomore-accel-stage-c-review.md) now has a C provider through the coordinator. Its stage import resolves and a classifier dependency at `0x67e4c` is now explicit; import count is unchanged. Classifier/spectral closure remains unfinished.
The [accelerometer feature collector](gomore-accel-collect-c-review.md) now has a C provider with native argument reloads, cursor/store order and provider frame, replayed directly and through the accelerometer stage. The stage root now has the C provider reviewed above; classifier/spectral closure remains unfinished.
The [signed-halfword statistics](gomore-i16-statistics-c-review.md) now have four C providers with wrapped signed arithmetic, native/C-sqrt replay and accelerometer-stage integration. The collector now has the C provider reviewed above; the stage root now has the C provider reviewed above; classifier/spectral closure remains unfinished.
The [motion floating-point conversion and ordered addition](motion-fp-c-review.md) now use C, removing the remaining inline assembly from the classifier and sampler/ring sources while preserving tested integer results, FPSCR and NaN precedence. Imports are unchanged.
The [accelerometer reset and history helpers](gomore-accel-history-c-review.md) now have shared native-ABI C providers, including the five reset sentinels and live cursor reloads. The accelerometer stage now has the C provider reviewed above.
The [Bosch direct-read frame wrapper](bma-c-read-frame-review.md) now uses C, preserving its published transport-buffer address and replacing the remaining inline assembly in that unit. Imports are unchanged.
The [optical estimator root](gomore-optical-root-c-review.md) now has a C provider with native public scratch addresses, direct replay and respiratory-caller replay. It closes `r1_gomore_optical_estimate_native`; fourteen other coordinator stage providers and the accelerometer classifier remain unresolved.
The [interval merger and derivative selector](gomore-interval-merge-c-review.md) now have C providers. Sequential replay also fixes the peak matcher's inherited stack-padding publication; complete record bytes now agree. The optical root now has a C candidate reviewed above.
The [IIR, percentile and confidence helpers](gomore-feature-helpers-c-review.md) now resolve all three lower reducer imports, with direct and complete reducer/optical-root replay through C providers.
The [locomotion feature reducer](gomore-feature-reduce-c-review.md) now has a tested C provider, including the native 96-byte frame/counter addresses and optical-root replay. Its three lower provider imports now resolve to C.
The [control extractor and interpolation helpers](gomore-control-extract-c-review.md) now have C providers with exact downstream stack addresses in optical-root replay. Its feature-reducer import now resolves to the new C provider.
The [optical peak matcher](gomore-peak-match-c-review.md) now has a tested C provider, including overlapping buffers, incoming argument aliases, encoded-double carry and optical-root replay; the optical root now has a C candidate reviewed above.
The [quantized valley selector](gomore-quantized-argmin-c-review.md) now has a C provider, tested directly and through the native peak matcher.
The [native subrange sort](gomore-sort-subrange-c-review.md) now has a tested C provider for the peak matcher.
The [native optical statistics and comparator](gomore-statistics-c-review.md) now have C providers, including native heavy-path and C-qsort integration; remaining numerical selectors remain unfinished.
The [moving-average extrema helper](gomore-extrema-c-review.md) now has a native-ABI C candidate, including actual optical heavy-path caller replay; remaining numerical selectors are unfinished.
The [shared special-value helpers](special-fp-c-review.md) now use C, retaining the double bodies and adding two qualified six-byte addition leaves to the canonical plan. Hybrid source-built executable coverage is now 4,381 bytes, with 641,779 stock executable bytes and 248 resource bytes.
The [tangent arithmetic and conversion](tanf-c-review.md) now use C in place of seven more inline-assembly helpers, with pole/exception checks and the remaining stack differences recorded.
The [sine arithmetic and conversion](sinf-c-review.md) now use C in place of seven more inline-assembly helpers, with tiny-input classifier/underflow behavior checked and frame differences recorded.
The [cosine arithmetic and conversion](cosf-c-review.md) now use C in place of seven inline-assembly helpers; its selected constant table remains unchanged, while native/C frame differences remain explicit.
The [bandpass coefficient generator](gomore-bandpass-c-review.md) now resolves the second native filter-setup dependency, with both generators executing through C configuration and reset callers.
The [low/high-pass coefficient generator](gomore-low-high-c-review.md) now resolves one native filter-setup dependency. Both coefficient generators now resolve.
The [optical reset and filter setup](gomore-optical-reset-c-review.md) now have tested C candidates. Its coefficient-generator imports now resolve.
The [optical window compactor](gomore-optical-compact-c-review.md) is now a tested C candidate with native optical gap/reset/warmup caller replay.
The [optical history append](gomore-optical-append-c-review.md) is now a tested C candidate; its optical-root consumer now has a C candidate.
The [respiratory root](gomore-respiratory-c-review.md) now runs in C, with the
coordinator frame adjusted to match published estimator pointers through the host.
Optical estimation now has a C candidate; fourteen other coordinator stage providers and the accelerometer classifier remain unresolved.
The [two-record clear](gomore-clear-two-c-review.md) now runs in C with exact
provider stack depths and checked-wrapper delegation. The experimental respiratory
root now uses this production helper.
The [respiratory statistics helpers](gomore-respiratory-stats-c-review.md) now
run in C, with checked utilities delegating to the shared native implementations.
Actual respiratory-caller replay passes; its root and estimator remain unresolved.
The [respiratory history helper](gomore-modulo-c-review.md) now runs in C,
including full counter/word behavior and actual respiratory-prefix replay. The
checked utility delegates to it; the full respiratory stage remains unresolved.
The [sixteen-stage coordinator](gomore-algorithm-c-review.md) now runs in C
with typed native interfaces and host-chain replay. Sixteen lower provider
imports are now explicit; full closure and stack equality remain open.
The [logger frame correction](gomore-log-object-c-review.md) makes suffix access
use the containing object representation; all compiled objects remain identical.
The [variadic logger](gomore-log-c-review.md) now runs in C with twelve
startup-verified configuration bytes, exact published pointers and actual stock
formatter replay. The coordinator now has a C provider; lower stage bodies and
whole-chain frame equality remain open.
The [interpolation provider](gomore-linear-c-review.md) now runs in C with
overlap-safe movement, signed boundary/FP replay and actual host-chain coverage.
The logger now has a C provider; final algorithm output and whole-chain stack
equality remain open.
The [IIR filter](gomore-filter-c-review.md) now runs in C with non-fused FP,
ordered live state updates and actual host-chain replay. Interpolation now has
a C provider; whole-chain stack differences remain open.
The [four-word kernel wrappers](gomore-kernels-c-review.md) now run in C with
consolidated ownership and actual host/resampler replay. The filter now has a C
provider; interpolation and kernel stack-depth differences remain open.
The [ACC/PPG resampling adapters](gomore-resample-c-review.md) now run in C,
including early FP exception visibility, NaN operand order and exact PPG scratch
pointers through the host caller. Their kernel wrappers now have C providers.
The [host-input adapter](gomore-host-input-c-review.md) now runs in C with
stock-relative scratch pointers, ordered payload/context reads and modeled lower
providers. The sensor-update caller still has an eight-byte frame difference;
whole-chain pointer equality remains unproven.
The [runtime validation and output-copy providers](gomore-lower-providers-c-review.md)
now run in C with the expanded output workspace and actual idle/update replay.
The [sensor-update coordinator](gomore-sensor-update-c-review.md) now runs in C,
including native diagnostic promotion, timestamp hysteresis and live sequence updates.
The [accelerometer/raw-HR adapters and readiness gate](gomore-stream-adapters-c-review.md)
now run in C with exhaustive signed-sample and shared-buffer replay.
The [GoMore idle callback](gomore-idle-c-review.md) now runs in C with live
failure accounting and a consolidated, startup-verified sensor workspace.
The [GoMore HR/HRV adapters](gomore-hr-adapters-c-review.md) now run in C,
including payload mutation/aliasing and actual authorization shutdown.
The [GoMore authorization dispatcher](gomore-authorization-c-review.md) now runs
in C with shared state ownership, exposing five lower sensor/timer callbacks.
The [hardware sqrt helper](sqrt-builtin-c-review.md) now uses a C builtin,
preserving FPSCR and explicit errno behavior through the RMSSD caller.
The [RMSSD diagnostic conversion](rmssd-conversion-c-review.md) now uses guarded
C with verified saturation and FPSCR behavior, removing RMSSD’s last inline assembly.
The [HRV producer conversion](hrv-conversion-c-review.md) now uses guarded C,
removing its last inline assembly while preserving saturation and FPSCR effects.
The [HRV producer comparison](hrv-positive-c-review.md) now uses strict GCC C,
preserving signaling NaN exceptions while removing one inline assembly boundary.
The [GoMore calendar converter](gomore-calendar-c-review.md) now runs in C,
closing the tested interval-engine graph without provider replacements. Its
full thirteen-byte record and month return match the independent date oracle.
The [GoMore interval build](gomore-interval-build-c-review.md) now runs in C
using GCC signaling comparisons, with history/FPSCR and calendar read boundaries
verified through compose and the engine. Calendar conversion now has a C implementation.
The [GoMore interval refinement](gomore-interval-refine-c-review.md) now runs
in C, preserving live reads, signed limits and early FP result/flag effects
through the compose and engine callers.
The [GoMore interval compose](gomore-interval-compose-c-review.md) now runs in C,
preserving metadata save points, wrapped rounding and the native memory-move
return. Interval build and refinement now have C implementations.
The [GoMore descriptor merge](gomore-descriptor-merge-c-review.md) now runs
in ordinary C, preserving aliased count reloads and separately rounded FP
results/flags through the engine and interval-update caller.
The [GoMore interval engine](gomore-interval-engine-c-review.md) now runs in C,
including its signed clamp, ordered unaligned policy loads and live controls.
Its compose and descriptor-merge providers now have C implementations.
The [GoMore packed-status propagation](gomore-propagate-c-review.md) now runs
in C, including exact-one pending clear and live time reloads through the
existing C packed accessors and interval-update caller.
The [GoMore interval-update wrapper](gomore-interval-update-c-review.md) now
runs in C, including live context reloads and output alias behavior through
the actual C memory-clear path. Its interval engine and propagation now have C implementations.
The [SpO2 sample callback](spo2-sample-c-review.md) now runs in ordinary C,
with fresh calibration inputs, event padding and unconditional handle cleanup
verified against stock. Both timing callbacks now have C implementations.
The [SpO2 timeout callback](spo2-timeout-c-review.md) now runs in C, including
verified timing-stream cleanup and the stock null-timer fault path.
The [SpO2 scheduler](spo2-scheduler-c-review.md) now runs in C with its raw
settings-record offset preserved by a C helper. Its sample and timeout dependencies now have C implementations.
The [SpO2 lifecycle callbacks](spo2-lifecycle-c-review.md) now run in ordinary
C with sixteen startup-verified bytes. Their timing scheduler now has a C implementation.
The [default activity-mode transition](health-default-mode-c-review.md) now
runs in ordinary C, with the shared byte's early clear and live publication
verified through the actual C GoMore wake path.
The [HR/HRV wear-change shutdown](health-hr-stop-c-review.md) now runs in
ordinary C, resolving another group-4 callback. Four HR stream handles add
sixteen startup-verified bytes; the existing shared HR timer field is reused.
The [activity-mode getter](activity-mode-c-review.md) now runs in ordinary C
and owns one startup-verified byte. Its actual C path passes the linked RMSSD
comparison corpus without adding imports.
The [RMSSD review](rmssd-c-review.md) adds C allocation, filtering, arithmetic,
logging and cleanup with a retained diagnostic conversion boundary. Its
activity-mode getter is the newly exposed native dependency.
The [HRV producer](hrv-producer-c-review.md) now uses C ring/state/event handling
with two required floating-point instruction boundaries. Its RMSSD provider
is the newly exposed native dependency.
The [HRV timeout callback](hrv-timeout-c-review.md) now runs in ordinary C,
including verified release/list cleanup and the stock null-timer fault path.
The [HRV scheduler review](hrv-scheduler-c-review.md) adds ordinary C scheduling
with its raw settings-record offset preserved by a C helper. Its timeout and
producer callbacks were exposed as dependencies; the timeout is now resolved.
The [HRV timing cleanup and restart review](hrv-timing-c-review.md) adds three
ordinary C routines and 228 startup-verified RAM bytes. Resolving the group-1
callback exposes its remaining native scheduling dependency.
The [hardware health status reports](health-status-reports-c-review.md) now run
in ordinary C, resolving the module's group-4 callback without new imports or RAM.
The [activity startup review](health-activity-c-review.md) adds C coordination,
eight startup-verified bytes and a required saved-word flag-getter boundary.
The boundary and empty C callback add 24 exact source-built bytes, reaching 4,369.
The [living-probe callback](wear-living-c-review.md) now runs in ordinary C and
passes direct comparisons plus actual C wear-off/callback/wear-off sequences.
The [wear-off decision](wear-off-c-review.md) now uses C scheduling/state/logging,
owns 11 startup-verified bytes and exposes the living-probe callback.
The [wear-on decision](wear-on-c-review.md) now uses C state/control/logging and
the existing range helper, retaining a signaling FP comparison boundary.
The [optical history range and active-FP followup](wear-range-c-review.md) adds the
deeper integer helper and verifies statistics/motion with FP context initialized
before FPSCR setup. No imports, RAM or exact-source regions are added.
The [wear motion statistics](wear-statistics-c-review.md) now run in ordinary C,
resolve the statistics dependency and add no RAM or native imports.
The [wear motion coordinator](wear-motion-c-review.md) now runs in C without new
RAM, exposing the deeper statistics and on/off decision routines.
The [ADT history sample and timeout](adt-data-c-review.md) now run in C, reuse the
canonical memory-move provider and own 20 startup-verified bytes. The timeout's
exact branch adds four source-built bytes, bringing coverage to 4,345.
The [wear ADT status and teardown](wear-adt-c-review.md) now run in C, owning 15
authenticated startup bytes and exposing the deeper sample/timeout callbacks.
The [wear sleep-status callback](wear-sleep-c-review.md) now runs in C, owns two
startup-verified bytes and resolves another health-module callback dependency.
The [stream timer rearm](timer-rearm-c-review.md) now runs in C, resolves the
raw-HR lifecycle's timer dependency and reuses the existing tick/wake providers.
The [wear raw-HR probe lifecycle](raw-hr-c-review.md) now runs in ordinary C,
owning eight startup-verified bytes and exposing native timer rearming. Its empty
sample callback adds two qualified bytes, bringing source-built coverage to 4,341.
The [health module startup](health-module-c-review.md) now runs in ordinary C,
reuses the Goodix setter and event context, and owns five startup-verified bytes.
Its top-level import is resolved while five deeper native dependencies are exposed.
The [motion classifier](motion-classifier-c-review.md) now runs in C with an
explicit native log-conversion instruction. Direct and integrated checks pass
4,897 paired cases; its four-byte callback cell has verified cold initialization.
The [motion-detection sampler and ring](motion-detection-c-review.md) now run in C
with two explicit floating-point boundaries, resolving detection setup.
The [GoMore accelerometer cache and callback adapter](gomore-accelerometer-c-review.md)
now runs in C, resolving the hardware handler-registration dependency and owning
155 startup-verified bytes.
The [health registration routines and temperature shutdown callback](health-registrations-c-review.md)
now run in C. Four startup imports are resolved and five deeper callback bodies
remain native.
The [sensor health startup coordinator](health-startup-c-review.md) now runs in C,
exposing nine deeper native initialization dependencies. Its empty hook adds two
qualified source bytes.
The [cached local-time provider](log-calendar-link-review.md) now participates
with C cache/copy logic and an explicit converter scratch-frame boundary.
The [daily cache initialization unit](daily-init-link-review.md) now participates,
resolving seven imports after consolidating the UTC getter and overlapping offset
fields. Its six exact initializer branches add 24 source-built bytes.
The [latest HR/HRV/SpO2 readers](health-latest-c-review.md) now use C clearing
and copy logic behind small saved-word frame bridges. Existing packed-provider
bodies remain unchanged in a separate source unit.
The [hourly sample accumulator](health-average-c-review.md) now uses C state and
arithmetic flow, retaining explicit calendar-frame and unsigned-conversion boundaries.
The [packed staging wrapper and word-store leaf](gomore-stage-c-review.md) now
supply record isolation and a qualified four-byte store. Exact source-built
coverage is 4,339 bytes after the [health service C replacements](health-service-c-review.md)
previously added 14 qualified bytes from two constant forwarders and a no-op. The [packed consumer](gomore-consume-c-review.md) now
supplies interval validation and output/scoring flow in C, retaining explicit raw
frame and signaling comparison boundaries. The [history shift and prefix marker](gomore-history-c-review.md) now run in C.
The corrected consumer forwards the signed adjustment to history, and the [timeline reader plus packed sample helpers](gomore-timeline-c-review.md)
now run in C. The [score coordinator](gomore-score-flow-c-review.md) also runs in C, exposing
three deeper native numerical providers. Table lookup and refinement remain
unresolved.
The [native interval dispatcher](gomore-dispatch-c-review.md) now supplies
selection/copy, context reload and payload-pointer restoration in C. The
selector remains unresolved; its packed-output wrapper is supplied by the
subsequent staging unit.
The [native Gomore wake flow](gomore-wake-c-review.md) now supplies allocation,
authorization gating, output setup and cleanup in C. Its lower native
interfaces are tracked separately as those controllers are reconstructed.
The [sleep wake controller](sleep-wake-c-review.md) now supplies wake-state
publication and timer operations in C with an explicit raw-word frame bridge.
The Gomore wake body is supplied by the subsequent C unit; its lower calls
remain unresolved.
The [temperature sleep-status controller](temperature-sleep-c-review.md) now
supplies capture initialization, mode restoration and timing-stream cleanup in
C. Its reporting wrapper retains an explicit stack and R3-residue difference.
The [temperature sampling and publication path](temperature-sample-c-review.md)
now supplies sample validation, consistency checks, five-sample publication and
the native unsigned-conversion ABI bridge, resolving two application imports.
The [temperature mode and periodic control](temperature-mode-c-review.md) now
supplies mode transitions, timer coordination and timing-stream startup in C.
Its measurement callback is supplied by the subsequent C unit; exact
qualification still rejects its three control bodies.
The [actual motion-to-BLE queue replay](motion-reply-queue-review.md) validates
heap copying, submission ownership and cleanup through linked C providers.
RTOS queue operations and physical delivery remain separate gates.
The [guarded byte event adapter](conditional-event-c-review.md) replaces one
more naked assembly body with C while matching full tested boundary state.
Its different instruction sequence remains outside exact qualification.
The [legacy sensor reply sender](legacy-reply-c-review.md) now supplies the
motion adapter's type-2 BLE dispatch wrapper in C, resolving one application
import. Exact qualification still rejects its current instruction bytes.
The [frontier binding repair](frontier-bindings-review.md) lets scoped
qualification bind known native callees without requiring their C providers.
At that stage, five forwarding callbacks added 22 qualified bytes, bringing
exact source-built coverage to 4,295 bytes. Callee implementation completeness remains separate.
The [event veneer C conversion](event-veneers-c-review.md) replaces six naked
assembly callbacks with ordinary C while preserving all allocated object
sections and relocations. Its empty callback added two qualified bytes; the subsequent binding repair
now qualifies the five forwarding bodies as well.
The [stream unregistration wrapper and body](stream-unregister-c-review.md)
now supply immediate unlink/free and deferred marking in C. Direct call depths
match stock in replay, and factory shutdown reaches the actual new providers.
The [factory temperature monitor and shutdown](factory-temperature-c-review.md)
now supply periodic sampling, counter persistence and mode teardown in C. The
monitor retains its reducer-buffer address; shutdown retains an eight-byte
frame difference; unregistration is supplied by the subsequent candidate.
The [factory motion event adapter](motion-adapter-c-review.md) now supplies
sequential axis caching and legacy reply construction in C. Its reply frame
retains a native/C pointer difference; the legacy sender is supplied by the subsequent C candidate.
The [factory aging threshold latch](threshold-latch-c-review.md) now caches
three sample words and updates configuration bits in C. It reuses the shared
factory-state owner and has matched getter/setter call depths in replay.
The [stream rate reducer](stream-rate-reduce-c-review.md) now scans remaining
listener rates, shrinks buffers and retimes streams in C. Its raw SDK logging
return remains explicit, alongside the architectural zero-divisor boundary.
The [deferred stream cleanup and object stop](stream-cleanup-c-review.md) now
remove marked listeners, release an empty object's buffer/timer and call the
driver stop callback in C. Tested cleanup/stop call depths match stock; rate
reduction is supplied by the subsequent candidate.
The [native stream timer dispatcher](stream-dispatch-c-review.md) now delivers
single samples and batches in C, preserving the timer-record ABI and 16-bit
batch lengths. Its cleanup continuation is supplied by the subsequent candidate,
and its 48-byte C frame differs from the native 40-byte frame.
The [append-based stream timer constructor](stream-timer-back-c-review.md)
resolves registration's back-constructor dependency with existing C list support.
Allocator-call frame identity remains unproven.
The [stream object-registration body](stream-register-object-c-review.md)
now supplies allocation, record setup, buffer conversion and timer decisions.
It retains a frame gap; raw logging return and zero-divisor dependencies remain explicit.
The [sensor sample-rate converter](stream-sample-rate-c-review.md) supplies
a C dependency for the remaining registration body, with native 32-bit math
and sequential overlapping copies. The subsequent registration body now calls it.
The [stream registration name wrapper](stream-register-name-c-review.md)
resolves name-based dispatch with a matched 32-byte frame and exposes the
deeper object-registration body, now supplied by the subsequent candidate.
The [stream/subscriber intrinsic conversion](runtime-intrinsics-c-review.md)
replaces four more BASEPRI statements while preserving every object and both
composition outputs. RTT probes were restored after instruction-order changes.
The [factory-mode activation](factory-mode-c-review.md) adds shared state,
configuration updates, timer replacement and stream-registration decisions.
Its 24-byte C frame retains a gap from the native 16 bytes.
The [factory boot gate](factory-boot-c-review.md) resolves the misleadingly
named startup import as configuration-driven delayed mode scheduling. Its two
raw-stack getters remain explicit; activation now exposes deeper writers,
registration and callbacks.
The [factory task lifecycle](factory-task-c-review.md) adds creator, stop and
worker behavior, with native dynamic-memory attributes and timer polling. Its record dispatcher remains explicit; the subsequent boot gate supplies
the startup call with deeper dependencies recorded separately.
The [factory receive enqueue](factory-rx-c-review.md) resolves the router
factory-message import with distinct factory thread/queue owners.
The [hardware task/watchdog intrinsic conversion](hardware-intrinsics-c-review.md)
removes two more handwritten BASEPRI statements with all 603 objects and both
composition outputs unchanged.
The [Cortex-M fault adapter](cortex-fault-c-review.md) resolves the RX failure
provider and replaces two existing handwritten BASEPRI statements with compiler
intrinsics, preserving their object bytes. Fault-register identity remains open.
The [BC receive thread creator](bae8-thread-c-review.md) supplies static
attributes, reservations and the create/stop prefix, referencing the C worker.
The [BC receive worker](bae8-worker-c-review.md) supplies queue startup and
flag-driven receive/suspend behavior. Its subsequent architectural fault adapter supplies C linkage with retained
exception-frame and instruction-identity gaps.
The [BC receive consumer](bae8-consumer-c-review.md) adds the drain, thread-stop
hook and connection setter. It exposes three deeper command imports and retains
a documented drain frame gap.
The [BC receive queue](bae8-rx-c-review.md) now constructs and transfers RX
messages in C, with separate RX thread/queue owners.
The [glasses role policy](glasses-role-c-review.md) now supplies decisions and
diagnostics in C; its architectural collision-fault transition remains explicit.
The [BAE8 router](bae8-route-c-review.md) is now a C behavior candidate with a
retained native/C frame gap. Its separate timeout leaf adds two qualified
bytes, taking exact source-built coverage to 4,271 bytes.
The [BAE8 transport startup](bae8-startup-c-review.md) calls the initializer
and creates both semaphore pools in C. Its event-route import is resolved,
while the later role and BC receive candidates resolve two of its four
lower receive/role dependencies.
The [BAE8 service initializer](bae8-service-c-review.md) now builds UUID and
characteristic records in C and is called by the transport startup unit.
The [BAE8 connection adapter](bae8-connect-c-review.md) supplies the dual-CCCD
connection path in C, reusing the existing architectural SVC173 gateway.
The [BAE8 write adapter](bae8-write-c-review.md) supplies the observer's write
handler in C, preserving notification flags and the escaping callback record.
The [BAE8 raw observer](bae8-observer-c-review.md) now dispatches events and
handles credits in C. Its two deeper handler imports are newly explicit,
so that observer step resolved one import and exposed two. The subsequent
write and connection adapters now resolve both deeper imports.
The [BAE8 shared service state](bae8-state-c-review.md) provides the service,
three-link descriptor and context pool used by the observer table and sender.
The [BAE8 link-context lookup](bae8-context-c-review.md) supplies the missing
sender dependency in C while preserving the native full-word handle checks.
The [connection-parameter policy](connection-parameters-c-review.md) supplies
the observer, interval classifier, flag slices and packed delayed callback in C.
The [peer-manager observer](peer-observer-review.md) exports the pinned SDK
callback to the reconstructed table while removing duplicate registration.
The [GATT context initializer](gatt-init-c-review.md) now provides the observed
three-link initialization API in the linked C unit; exact coverage is unchanged.
The [GATT disconnect link reset](gatt-link-c-review.md) closes a missing
provider and contributes 24 qualified C instruction bytes to the hybrid image.
The [RTT-only default logger initializer](rtt-default-c-review.md) removes two
unobserved UART dependencies using a scoped SDK configuration.
The [shared DFU SVCI state](dfu-state-owner-review.md) connects the SDK and
recovered backend to one allocation; 1,728 paired sequences check that link.
The [DFU bootloader vector handoff](dfu-vector-set-c-review.md) supplies the
missing C provider with 2,912 bounded comparisons; physical handoff is unproven.
The [generated-input qualification repair](generated-qualification-review.md)
lets hardware units such as the generated FAL owner reach compilation and
matching without a scoped path workaround. It adds no qualified bytes.
The [flash-read/FAL save frames](flash-read-frame-review.md) close the retained
partial-read counterexample in 1,920 strict native comparisons at controlled
native adapter placement. Normal byte qualification remains unproven.
The [sector/FAL integration](sector-fal-integration-review.md) restores native
header-call R6 and checks 1,920 cases through real C FAL providers. It retains
a stock/source helper-frame counterexample; full-chain stock equality is unproven.
The [sector C stepper](sector-stepper-c-review.md) moves dispatch, diagnostic
sequencing and result policy into C, retaining an 88-byte stack/ABI adapter.
Its 12,302 paired cases include native provider stack positions and mutations.
The [sector control extraction](sector-control-c-review.md) moves header decoding
and traversal arithmetic to C while protecting both native read views. Its
12,230 paired cases distinguish returns, assertions and bounded read prefixes.
The [FlashDB log reader](flash-tsl-c-review.md) moves the outer read/decode/update
control to C while retaining its native partial-read scratch frame. It passes
9,310 direct comparisons and 10,368 actual FAL-path comparisons.
The [event publisher frame](event-publisher-frame-review.md) preserves stock
queue-record residue through an explicit native frame, eliminating an
uninitialized C local; 2,886 direct paired cases check the entire record/frame.
The [subscriber multicast dispatcher](subscriber-multicast-c-review.md) moves
allocation, cache and thread routing to C, with 6,997 paired checks and 192
publisher-to-consumer integration cases. Native register adapters remain.
The [subscriber registration](subscriber-registration-c-review.md) moves list allocation,
duplicate detection and thread-cell binding to C, with 2,496 paired stock checks.
The [subscriber lock and consumer](subscriber-c-review.md) move mutex and drain
control to C and reuse the canonical CMSIS thread-ID provider.
The [Goodix stream provider and registration](goodix-stream-provider-c-review.md)
resolve sensor stream registration and add the three C provider operations.
The [Goodix stream callbacks](goodix-stream-callbacks-c-review.md) add 16 native
callback/setter C entry points and verify their 272 bytes of RW/ZI state.
The [sensor-stream bootstrap](stream-bootstrap-c-review.md) replaces four assembly
dispatch/bootstrap routines and checks actual C list/timer construction.
The [FlashDB traversal leaves](flash-traversal-c-review.md) replace four assembly
helpers with C while preserving unsigned boundaries and address wrapping.
The [FlashDB control interface](flash-control-c-review.md) now uses C for all
selectors, diagnostics and native return routes.
The [FlashDB query helpers](flash-query-leaves-c-review.md) replace the database
path and query-count callback assembly with checked C.
The [FlashDB read adapter and status scanner](flash-read-c-review.md) replace
two assembly functions and execute through the actual FAL read/cache path.
The [watchdog-aware task name](task-name-c-review.md) closes another crash
diagnostic dependency with actual watchdog-getter integration checks.
The [native task stack accessors](task-stack-accessors-c-review.md) resolve two
crash-diagnostic dependencies and qualify 24 stock-identical C bytes.
The [PPG packed accessors](ppg-packed-c-review.md) replace three assembly leaves
with checked C while retaining ordered unaligned cache/output accesses.
The [C task selector](context-selection-c-review.md) now has current ownership
and round-robin/stack-guard stock execution checks.
The [scheduler unblock checks](scheduler-unblock-c-review.md) extend that execution
through pending-ready draining and delayed-task wakeups.
The [scheduler-lock integration](task-scheduler-locks-c-review.md) executes actual
suspend/resume, critical nesting and pending-tick replay without function stubs.
The [allocator-to-ready-list integration](task-heap-ready-c-review.md) executes the
whole creation path and restores the stack builder's stock xPSR-word dependency.
The [ready-list handoff](task-ready-handoff-c-review.md) now has current source
ownership, standalone stock checks and constructor-path execution evidence.
The [public task constructors](task-create-api-c-review.md) now share the tested
native C bodies, resolving dynamic and static task creation imports.
The [public task allocation ABI](task-public-abi-review.md) now reserves native
112-byte controls and preserves 32-bit stack depths across all FreeRTOS consumers.
The [task-priority setter](task-priority-c-dependency-review.md) resolves its scheduler
dependency with inheritance, ready-list and PendSV checks.
The [event-item reset](event-reset-c-dependency-review.md) resolves its scheduler
dependency and adds 24 byte-identical C bytes to the source plan.
The [timer-service queue wait](queue-restricted-c-dependency-review.md) resolves its
restricted wait dependency with actual queue lock/unlock comparisons.
The [queue occupancy queries](queue-query-c-dependency-review.md) resolve task and
ISR count reads with critical-boundary mutation and stock instruction checks.
The [native allocator integration](native-heap-c-integration-review.md) selects the
stock-layout allocator after allocation/free and actual queue lifecycle comparisons.
The [queue deletion closure](queue-delete-c-dependency-review.md) resolves deletion
with ownership-byte and creation/deletion lifecycle comparisons.
The [task queue receive closure](queue-receive-c-dependency-review.md) resolves
receive waits, sender wakeups and the post-timeout data-arrival race.
The [task queue send closure](queue-send-c-dependency-review.md) resolves task
queue sends with timeout, blocking and unlock behavior checked against stock.
The [ISR queue send closure](queue-isr-send-c-dependency-review.md) resolves
interrupt-safe back/front/overwrite sends with the shared queue and copy providers.
The [ISR queue receive closure](queue-isr-receive-c-dependency-review.md) resolves
interrupt-safe queue receive with the shared queue and memory providers.
The [counting-semaphore dependency closure](counting-semaphore-c-dependency-review.md)
resolves static and dynamic semaphore constructors through the shared queue owner.
The [queue-creation dependency closure](queue-create-c-dependency-review.md)
resolves both static and dynamic queue constructors with the shared queue owner.
The [queue-reset dependency closure](queue-reset-c-dependency-review.md) resolves
`xQueueGenericReset` through the shared native queue layout.
The [software-TWI delay closure](twi-delay-tail-closure-review.md) resolves one
hardware timing import through an exact compiled wrapper and source primitive.
The [battery context closure](battery-context-closure-review.md) joins shared
status/ADC views under canonical C storage and resolves seven imports.
The [battery KV closure](battery-kv-closure-review.md) binds two cached-class
handles to their source-owned records and resolves two more imports.
The [status ring storage closure](status-ring-storage-review.md) removes a
duplicate publisher and resolves the four ring-storage imports.
The [paired temperature C conversion](temperature-c-pair-review.md) replaces
five assembly functions while preserving both import sets.
The [temperature conversion C body](temperature-c-convert-review.md) moves
the floating-point sample calculation into C with its native scratch bridge.
The [one-shot trigger C body](temperature-c-trigger-review.md) preserves the
command buffer and live log-mode decisions through a small frame bridge.
The [calibration reader C body](temperature-c-calibration-review.md) retains
native rejected-read scratch bytes and ordered output accesses.
The [cached NV storage closure](nv-storage-closure-review.md) resolves three
handles and replaces the placement-sensitive health settings setter with C.
The [health change detector C conversion](health-c-change-review.md) preserves
the byte thresholds, live read order and reinitialization tail call.
The [YHM2710 status frame repair](yhm-c-status-frame-review.md) restores the
native saved-word pointer around the existing C status logic.
The [YHM2710 system-track frame conversion](yhm-c-track-frame-review.md)
preserves byte-only updates and the existing qualified initialize wrapper.
The [ADC close/read-order repair](adc-c-close-read-order-review.md) preserves
live name lookup and native channel/driver shutdown decisions.
The [ADC open frame repair](adc-c-open-frame-review.md) restores the native
configuration word and uses the evidenced cycle-delay provider directly.
The [ST25 delay binding](st25-c-delay-binding-review.md) also uses its native
cycle-delay handoff and removes the seam's unresolved wrapper dependency.
The [STACMD GPIO callback repair](stacmd-c-gpio-callback-review.md) uses void
callback types with an explicit raw-R0 ABI gateway and checked NOP counts.
The [STACMD receive frame repair](stacmd-c-receive-frame-review.md) restores
the native saved-word buffer and adapter result/register behavior.
The [STACMD read-frame repair](stacmd-c-read-frame-review.md) preserves separate
ACK/data scratch words, partial failure stores and live output parity reloads.
The [STACMD write-frame repair](stacmd-c-write-frame-review.md) preserves the
native ACK seed/restoration and fresh payload/parity reads.
The [critical-section closure](rtos-critical-closure-review.md),
[RTC1 tick closure](rtc1-tick-closure-review.md),
[TWI leaf closure](twi-leaf-closure-review.md) and
[tickless-idle closure](rtc1-tickless-closure-review.md) and
[kernel queries](rtos-query-closure-review.md) and
[current-task storage/getter](current-task-closure-review.md) resolve the latest
hardware/port dependencies. The history below records earlier snapshots.

Both R1 payloads now configure GNU `arm-none-eabi-ld -r` in `sources.json`.
The build uses exactly the existing participating objects: 436 application
objects and 74 bootloader objects. No candidate's link eligibility changed,
and no aliases, absolute addresses or warning-suppression flags were added.

The complete build compiles all 560 units and successfully composes both
payloads. The remaining undefined sets are exactly the sets from the prior
isolated FlashDB diagnostic: 253 application imports and 34 bootloader
imports. Mixed enum-size warnings remain visible in the application link
report; relocatable link success does not prove ABI compatibility. Future
composition failures now fail the normal build instead of escaping a
compile-only check.

The initial report is `build/sources-goal-r1-composed/report.json`. The later
[i2c_5 callback repair](twi-delay-review.md) adds one explicit application
import, `r1_twi_i2c5_delay_noop`, for the distinct excluded provider. The current
report after that repair was `build/sources-goal-r1-twi-delay/report.json`.
The subsequent [GPIO closure](twi-gpio-review.md) resolves six imports and adds
one compilation unit by splitting the existing provider. The later
[LIS transport closure](lis-transport-closure.md) removes eighteen superseded
wrappers and resolves four more imports. Checked
[hardware-TWI registration](hw-twi-registration-review.md) resolves the two
control-record imports. Checked
[output-GPIO registration](output-gpio-registration-review.md) resolves its
configuration import. The RTC IRQ snapshot report
is `build/sources-goal-r1-rtc-irq/report.json`: 238 application imports and 34
bootloader imports, with 487 application units and 74 bootloader units.
The subsequent [C transport conversion](lis-c-transports-review.md) preserves
both import sets while replacing two inline-assembly candidate bodies.
The [Nordic SVC binding](nordic-svc-binding-review.md) also preserves both
import sets while replacing the product gateway copy with the SDK body.
Checked [PMIC state-command registration](stacmd-registration-review.md)
resolves its record import without changing the provider's C or object bytes.
Checked [RTC cached lookup](rtc-cache-kernel-review.md) resolves its function
import. Checked [RTC device closure](rtc-device-closure.md) includes the device
record/operations and resolves the memory adapter. Checked
[RTC lifecycle](rtc-lifecycle-review.md) includes the C driver bridges and
removes a duplicate error logger; physical driver execution remains separate.
The [RTC2 IRQ review](rtc-irq-review.md) includes its vector reference after
modeled dispatcher comparison; physical exception delivery remains separate.
The [snapshot sampling-order repair](rtc-snapshot-order-review.md) changes
an initially excluded candidate, preserving both import sets at that stage.
Report hashes, manifest identity and import consumers are retained in
[source-composition-review.json](source-composition-review.json). That evidence
also lists same-name providers among excluded, compiled candidate objects.
These are lookup candidates, not qualified providers: names alone do not
establish stock identity, compatible interfaces or permission to link them.
In particular, the list exposes existing GPIO, TWI, RTC and LIS2DW12 source
boundaries for subsequent native review without adding another implementation.

Run `python3 tools/build/sources.py build --device r1 --out build/NEW-DIRECTORY`
to repeat the complete check. This creates partial relocatable objects,
not runnable firmware. Final memory placement, linker-defined symbols,
runtime/private dependencies, source qualification, original-compiler byte
identity and physical hardware behavior remain open. No G2 workflow gate changed. The R1 source plan includes the qualified
regions documented in the linked reviews.

The latest write-adapter frame correction and generated GCC-provider fingerprint check are recorded in [flash-write-frame-review.md](flash-write-frame-review.md).

The [hardware C qualification sweep](hardware-c-qualification-review.md) admits four exact Goodix/touch power wrappers (24 bytes). The canonical application now has 3,945 source-built bytes, 642,215 stock fallback bytes and 248 resource bytes; full source completeness remains unproven.

The [Goodix software-reset configuration](goodix-soft-reset-config-review.md) matches four mapped stock reset callsites and removes the two vendor hard-reset pin-hook dependencies. Full initialization and physical sensor behavior remain unverified.

The [Goodix polling configuration](goodix-polling-config-review.md) matches the native initialized mode byte and 240 bounded IRQ-entry comparisons. The prior normal-interrupt configuration diverges in 48 cases; full ISR and physical behavior remain unverified.

The [Goodix interrupt-trigger native binding](goodix-trigger-native-binding-review.md) replaces a superseded callback/context abstraction with the stock no-argument upstream C function and admits its complete 28-byte body. Canonical coverage is 3,933 source-built bytes, 642,227 fallback bytes and 248 resource bytes.

The [pinned PPG timestamp hooks](goodix-ppg-timestamp-hooks-review.md) resolve two dependencies with the stock no-work behavior and admit four exact C bytes. Current canonical coverage is 3,937 source-built bytes, 642,223 fallback bytes and 248 resource bytes.

The [timestamp dependency closure](goodix-timestamp-closure-review.md) resolves three more hardware-path imports using native call identities and pinned C, removes a superseded constant helper, and admits eight new C bytes. Current canonical coverage is 3,945 source-built bytes, 642,215 fallback bytes and 248 resource bytes.

The [accelerometer start/stop HAL binding](goodix-cache-start-c-binding-review.md) connects both HAL names to checked native C policy. It passes 416 paired cases; the new start body remains outside exact-byte selection.

The [frame-hook C correction](goodix-frame-hook-c-review.md) removes a nonstock raw notification, preserves the opaque dispatcher tail call and passes 384 paired wrapper cases. The dispatcher body remains separate reconstruction debt.

The [remaining I/O-dispatch analysis](goodix-io-dispatch-analysis.md) records the native callback/logging policy and a strict 216-versus-232-byte frame counterexample for a C probe. That probe is not integrated; production sources and the exact plan remain unchanged.

The [native-frame I/O dispatcher](goodix-io-dispatch-c-review.md) implements callback routing, result gates, pairwise minima and logging preparation in C with a fixed-frame transfer adapter. It passes 492 strict unit and 432 real-cache integration cases under both Clang and GCC9. Byte qualification remains unproven and canonical byte coverage is unchanged.

The [stock wear-event policy](goodix-wear-event-c-review.md) replaces the demo notification dependency with callback slot 3, native living-object stop routing and ordinary multi-sensor wear events. The bounded C candidate preserves repeated log-mode reads and provider stack depths.

The [polling hook closure](goodix-polling-hook-closure-review.md) guards the unused external-interrupt initializer, restores the native empty raw-data hook, and qualifies four registered empty callbacks as eight C-built bytes.

The [configuration-stop query order](goodix-config-stop-order-review.md) makes temperature, capacitance and gsensor reads explicit before the sensor-enable tail call. Actual native and C flag getters and the state setter pass the bounded integration fixture.

The [sensor-flag qualification](goodix-sensor-flags-review.md) admits the pinned capacitance/temperature getters as eight exact C-built bytes and retires their two superseded generic implementations. The sensor-state setter and gsensor getter remain unqualified.

The [battery timestamp binding](battery-timestamp-binding-review.md) supplies the legacy dependency name as an alias of the checked backend timestamp body. It adds no second clock implementation or executable bytes.

The [RTC timestamp frame review](rtc-timestamp-frame-review.md) preserves native active R4-R11 at clear/dispatch boundaries in the recorded C build. It retains a 72-byte frame and existing memory/registry C providers; no exact region is admitted.

The [RTC tick C conversion](rtc-tick-c-review.md) removes the handwritten tick frame bridge and preserves the native calendar pointer and provider depth. Both recorded Clang and a scoped GCC9 profile pass direct and real-converter fixtures; the other two RTC lifecycle bridges remain.

The [RTC epoch C conversion](rtc-epoch-c-review.md) replaces the epoch-initialization assembly bridge and private worker with a direct C body. Recorded Clang and scoped GCC9 profiles preserve native provider depth, scratch address, statuses and shared-memory order. The subsequent [RTC open C conversion](rtc-open-c-review.md) removes the last executed assembly bridge in the lifecycle module; two empty compiler register constraints remain.

The [direct C watchdog checker](watchdog-check-c-review.md) replaces its naked bridge and private worker while preserving the sampled R3 word and native 16-byte provider depth in the recorded Clang/GCC9 profiles. BASEPRI remains an architectural instruction. Both compiler fixtures pass 6,912 paired direct cases plus 1,024 actual-list-helper cases. No exact regions are admitted; imports remain 164 application / 34 bootloader.

The [direct C STACMD receive adapter](stacmd-adapter-c-review.md) replaces its naked bridge and private worker while preserving the 16-byte reader frame and overlapping-copy R1/R3 behavior in recorded Clang/GCC9 profiles. Both pass 2,304 direct and 219 protocol-integration paired cases. No exact regions are admitted; imports remain 164 application / 34 bootloader.

The [direct C STACMD write frame](stacmd-write-c-review.md) replaces its naked bridge and private worker while preserving the ACK word and native 24-byte provider depth in recorded Clang/GCC9 profiles. Both pass 3,824 direct and 219 protocol-integration paired cases. Read framing remains unchanged. No exact regions are admitted; imports remain 164 application / 34 bootloader.

The [direct C STACMD read frame](stacmd-read-c-review.md) replaces the final naked bridge and private worker in the frame module while preserving distinct ACK/data words, R12 and native 48-byte provider depth. Recorded Clang/GCC9 each pass 1,764 direct and 219 protocol-integration paired cases. Three empty register constraints remain across read/write framing. No exact regions are admitted; imports remain 164 application / 34 bootloader.

The [RTC exact-provider review](clock-provider-exact-review.md) admits three official-qualifier regions totaling 38 bytes: callback-binding request and both backend wrappers. Out-of-line requests and empty R4 constraints retain native wrapper frames. The canonical R1 application now has 3,999 source-built bytes, 642,161 fallback bytes and 248 resource bytes, with locked hash unchanged. Full source completeness remains false; normal imports remain 164 application / 34 bootloader.

The [RTC write-request frame review](clock-write-frame-review.md) uses the standard memset result to preserve native active R6 and the R4/R5 input carriers in the normal Clang profile. All 480 paired actual-clear/registry cases pass at native SP-80, including status and null-path behavior. Existing exact RTC regions remain valid; the 3,999-byte source-built total and 164/34 imports are unchanged.

The [RTC 64-bit read-frame review](clock-read64-frame-review.md) removes the memcpy temporary and retained R4 request pointer, reaching native SP-72 and full R0/R1 result behavior in recorded Clang. All 320 paired actual-clear/registry cases pass, including partial 64-bit responses and null paths. The function-local extent is now indexed; backend-table association remains outside this review. Existing exact RTC regions, 3,999-byte source-built total and 164/34 imports are unchanged.

The [default RTC backend binding review](clock-default-binding-review.md) confirms getter 0x5a988, table 0x99c8c and slot-12 veneer 0x50d82 leading to 0x51494. The C table now uses the corresponding C tail veneer. Five official-qualifier regions add 24 exact bytes; canonical totals are 4,023 source-built, 642,137 fallback and 248 resource bytes with locked hash unchanged. All 240 paired table/callback cases pass; full source completeness remains false.

The [direct C UTC adapter](calendar-utc-direct-review.md) replaces its fourteen-byte bridge and private helper with a single C function at native SP-48. Recorded Clang/GCC9 adapters each pass 4,950 modeled-converter and 770 actual-converter paired cases, including ordered access widths and output aliases. Removing the retired bridge unit reduces the normal census to 575 without changing the 164/34 imports or 4,023-byte exact source-built total. Calendar callback candidates remain excluded pending their own validation.

The [calendar provider composition review](clock-calendar-composition-review.md) enables three existing units and nine providers: calendar read/write, selected inverse conversion and RTC requests/backend wrappers. The write callback now uses the existing volatile UTC-offset accessor. Validation passes 640 callback, 3,610 actual inverse-converter and 408 integrated C-chain paired cases. Normal imports remain 164/34; no new exact regions are admitted. Bootstrap initialization remains compile-only.

The [clock binding C review](clock-binding-c-review.md) moves snapshot and bind to one linked C owner and removes the live snapshot assembly definition. Both compilers pass 11,802 direct helper and 9,216 live-parent paired cases. The other 573 objects remain unchanged. Imports remain 164/34; no exact regions are added, and initialization remains compile-only.

The [clock constructor C review](clock-constructor-c-review.md) repairs callback-visible pointer reloads, configuration aliases and the normal Clang 24-byte frame. Its 4,400 stock/C paired cases pass; GCC compiles but fails the frame contract. Bootstrap remains compile-only, normal composed payloads are identical and the exact source plan is unchanged.

The [pending flag C review](time-pending-c-review.md) removes the setter's executed inline assembly and qualifies 12 exact Clang bytes. Empty register constraints remain. Normal Clang passes 4,096 full-register paired cases; GCC has an additional R3 clobber and is not qualified. Canonical source-built bytes increase to 4,035, including assembly/data; imports remain 164/34 and bootstrap remains compile-only.

The [time-update C review](time-update-c-review.md) replaces the remaining clock-update adapter assembly with C and empty provider-register constraints. Clang and GCC parent objects each pass 9,552 modeled-clear and 9,552 actual-clear paired cases, including callback-mutated exposed slots and 32 matched faults per mode. The 56-byte provider frame and R4-R11 values match stock; source-plan bytes remain 4,035 and imports remain 164/34. Bootstrap remains compile-only.

The [legacy TWI TX C review](twi-legacy-tx-c-review.md) adds typed SDK-backed providers for the two native transmit wrappers. Normal Clang and a GCC diagnostic probe each pass 11,520 paired cases; strict GCC qualification remains blocked by SDK unused-parameter diagnostics. Existing 576 objects and callers remain unchanged, imports remain 164/34, and no exact regions are added.

The [TWI read C review](twi-read-c-review.md) replaces both register-read assembly bridges and helper kernels with C using the actual 40-byte frame. Normal Clang passes 18,396 direct and 18,396 actual-legacy-wrapper paired cases, including returned R2/R3 and stack aliases. GCC diagnostic frames fail. The other 576 objects, write paths, manifest, imports 164/34 and exact source plan are unchanged.

The [TWI packet-write C review](twi-packet-write-c-review.md) replaces both write operation bridges and their helper kernels with C preserving the 16-byte frame. Normal Clang passes 26,064 direct and 26,064 actual-short-TX-wrapper pairs, including saved-word and request/input aliases. Read code, register-transfer adapters and other 576 objects are unchanged. Imports remain 164/34; no exact regions are added, and GCC probes fail the frame contract.

The [shared SP observation review](native-stack-c-review.md) removes unsafe GCC reserved-SP outputs from the TWI consumers and centralizes compiler-specific reads. All 577 normal Clang objects and composed payloads remain identical. Standalone Clang/GCC probes pass 384 cases each across leaf/framed callers and thread MSP/PSP; the old GCC pattern changes SP and is rejected. GCC consumer frame qualification remains incomplete, with imports 164/34 and the exact source plan unchanged.

The [YHM2710 tracking review](yhm-track-c-review.md) replaces the charger tracking assembly bridge with C while preserving its exposed 16-byte frame. All 577 R1 units compile, the 576 unrelated objects are unchanged, imports remain 164/34 and the existing four-byte initializer still qualifies exactly. No new exact source regions are claimed.

The [YHM2710 clear-tracking review](yhm-clear-c-review.md) adds the native clear path and qualifies its four-byte dispatch tail. All 577 R1 units compile, the 576 unrelated objects and existing setter functions are unchanged, and imports remain 164/34. The locked hybrid image now contains 4,039 selected source bytes and 642,121 fallback bytes; complete source-only firmware remains unproven.

The [YHM2710 ladder review](yhm-ladder-c-review.md) adds the native 40-byte-frame selection/update path and its four-byte exact dispatch tail. All 578 R1 units compile, all 577 existing objects are unchanged, and imports remain 164/34. The locked hybrid contains 4,043 selected source bytes and 642,117 fallback bytes. Its actual C math-provider integration passes 23,872 stock comparisons across 32 FPSCR configurations; GCC register/status differences remain unqualified.

The [native VBAT read review](vbat-read-c-review.md) adds the separate three-sample signed acquisition and integer conversion at 0x506a4. All 579 R1 units compile, all 578 existing objects remain unchanged and imports stay 164/34. Its 10,240 native comparisons preserve the 24-byte frame, upper saved-word bytes, dynamic ADC handle reloads and callback effects. No exact source regions are added.

The [VPMIC context correction](vpmic-binding-c-review.md) repairs the 0x506a4 reader: it uses YHM vpmic_isns_adc at 0x2000687c+16, not the separate vbat_adc runtime field at 0x20006890+16. The earlier one-context fixture masked this owner error. Both contexts now coexist in 10,240 direct and 6,656 actual-initializer comparisons; the previous object fails at its first open. All 579 R1 units compile and the 578 unrelated objects are unchanged.

The [direct battery-filter C root](battery-filter-root-c-review.md) removes the retained 48-byte assembly bridge and separately framed helper at 0x91184. Its product object matches the native 48-byte provider depth, live R4-R11 and scratch access oracle in 4,620 paired cases. The old bridge fails at 80 bytes. All 579 units compile, the 578 unrelated objects and imports remain unchanged, and GCC retains an extra-write counterexample. No exact source regions are added.

The [direct recovery C root](battery-recovery-root-c-review.md) removes the stuck-charge assembly bridge and separate kernel. Natural outgoing log words preserve its saved-R1/R2/R3 overlay, 40-byte provider frame and live R4-R11 in 4,288 comparisons, including mutation and three saved-word timestamp aliases. Old bridge/GCC depths remain retained counterexamples. All 579 units compile, the 578 unrelated objects and imports remain unchanged; no exact source regions are added.

The [C negation dependency review](abs-negate-c-review.md) replaces explicit VNEG assembly with unary C negation while retaining the NaN-sensitive compare. Clang and GCC each pass 66,112 isolated stock comparisons, and the actual charger-ladder C chain passes 23,872. All 579 units compile, the 578 unrelated objects and every other math function/data section are unchanged, and the existing source plan is preserved.

The [direct TWI register-write roots](twi-register-write-c-review.md) remove both assembly bridges/private kernels while preserving the native 104-byte frame and length-80 saved-R4 overlap. Direct and actual C legacy-wrapper suites each pass 14,580 pairs; the actual bulk packet/register/wrapper chain passes 9,000 at native SDK depth 136, plus 24 null-input boundary cases. All 579 units compile, the 578 unrelated objects and existing read sections are unchanged, and imports remain 164/34. No exact source regions are added.

The [SAADC IRQ C source-route review](saadc-irq-c-review.md) connects stock
`0x317cc` to the existing SDK C handler after 13,056 stock/C pairs. Firmware
sources, object hashes, unresolved sets and source-plan bytes are unchanged.

The [RTC2 IRQ C source-route review](rtc2-irq-c-review.md) validates the existing
SDK handler through 21,504 paired IRQ invocations and corrects the working stub
span from 162 to ten code bytes. Firmware source/object hashes and imports are
unchanged; no new exact regions are selected.

The [GPIOTE IRQ and PORT C source-route review](gpiote-irq-c-review.md) validates
the existing SDK paths across 137,594 paired IRQ invocations. The PORT helper is
inlined in the compiled C IRQ. Firmware sources, normal object hashes, imports
and the source plan remain unchanged; no exact regions are added.

The [SPIM2 completion IRQ C source-route review](spim2-irq-c-review.md) validates
the existing SDK completion path across 5,760 paired IRQ invocations. It also
corrects the adjacent TWIM1 stub span without claiming dispatcher validation.
Firmware source/object hashes, imports and the source plan remain unchanged.

The [TWIM IRQ C source-route review](twim-irq-c-review.md) adds both bus entries,
the common dispatcher and completeness helper after 174,080 paired IRQ
invocations. The [observer review](irq-observer-review.md) records a global-hook
execution artifact and full bounded-hook replays of the four earlier IRQ matrices.
Firmware sources, object hashes, imports and exact-source selections are unchanged.

The [PWM C driver review](pwm-c-review.md) adds the missing three-instance SDK
driver with local recovered configuration. All 590 R1 units compile; prior 589
objects and the 164/34 import sets are unchanged. IRQ behavior passes 25,056
paired invocations; playback/init APIs still need behavior qualification.

The [PDM microphone IRQ C source-route review](pdm-irq-c-review.md) validates
existing SDK buffer handoff, overflow and stop-release paths across 10,656 paired
IRQ invocations. Firmware sources, the 590 normal object hashes, import sets and
source-plan selections are unchanged.

The [TIMER2/4 IRQ C source-route review](timer-irq-c-review.md) validates both
SDK entry points and their common dispatcher across 98,704 paired IRQ invocations.
It corrects TIMER4's working span and reproduces an existing eight-byte timer-clear
admission; no new exact regions or firmware source changes are introduced.

The [NFCT/TIMER4 C integration review](nfct-irq-c-review.md) validates the NFC
IRQ, field/check/delay helpers and actual TIMER4 clear/enable calls across 162,544
paired IRQ invocations. Native timer-workaround initialization matches C. Firmware
sources, 590 normal object hashes, imports and source-plan selections are unchanged.

The [GoMore authorization dispatcher](gomore-authorization-c-review.md) now
consolidates the device-ID once-status and wake-flag fields into shared ownership.
Host-input update, logging, output lifecycle and lifecycle
initialization remain dependencies.

The [full-range EUS transport review](eus-range-c-review.md) fixes delivery of4,063 through4,096 bytes with a4,096-byte assembly cap. All1,355 compatible stock/C comparisons,34 extended lengths,16 safety cases,36 stock queue comparisons,272 extended queue cases and five allocation-failure cases pass. Actual C queue delivery preserves payload after assembly cleanup. All841 other nongenerated objects are unchanged; the import set remains66 application and 22 bootloader symbols.

The [ordinary C send registration](send-registration-c-review.md) removes fixed-register assembly constraints from the callback setter. All 1,620 stock/C comparisons pass; all 841 other nongenerated objects and both import sets remain unchanged.

The [ordinary C send-hook dispatcher](send-hook-c-review.md) removes its remaining register constraint and corrects the callback type to the registered three-argument C sender. All 2,144 direct comparisons and the actual-dispatch transport replay pass; all 841 other nongenerated objects and both import sets remain unchanged. The [remaining FlashDB C dependencies](flash-partial-read-c-dependencies.md) identify coupled partial-read and iterator requirements.

The [FAL read completion repair](fal-read-completion-c-review.md) prevents16-bit provider truncation and propagates device failures.36 compatible request comparisons,10 actual C large-read cases,36 injected failures,three uninitialized-provider cases and two count guards pass; two compiled defects are rejected. All841 other nongenerated objects and both import sets remain unchanged.

The [defined C FlashDB read path](flash-defined-c-review.md) removes TSL/sector assembly bridges and read-adapter/FAL-read register constraints. Exact byte-count admission and iterator unlock exits stop incomplete-read decoding.3,549 successful stock/C comparisons,190 C-only error cases,9,216 FAL regressions and16 iterator exits pass; four compiled defects are rejected. All839 other nongenerated objects and both import sets remain unchanged.

The [C FlashDB time-range iterator](flash-iterator-c-review.md) removes its remaining assembly implementation.9,903 normal-entry stock/C comparisons cover all392 main instruction bytes and all three read sites;211 C-only error cases and13,944 helper regressions pass. Four compiled defects are rejected. All841 other nongenerated objects and both import sets remain unchanged.

The [ordinary C FlashDB write adapter](flash-write-c-review.md) removes its fixed-register constraints after the read path gained defined buffers.3,282 direct comparisons and1,728 actual FAL/cache comparisons pass; two compiled defects are rejected. All842 nongenerated objects, ten other utility bodies, data and both import sets remain unchanged.

The [overflow-safe FAL partition checks](fal-bounds-c-review.md) reject wrapped read/write/erase ranges before device lookup.24,681 compatible stock comparisons and2,895 overflow rejections pass; three reverted guards are rejected. All842 nongenerated objects, other FAL functions, data and both import sets remain unchanged.

The [C compiled calibration restore](nv-default-restore-c-review.md) closes the NV restore event import using the existing cached ring/battery classes.2,829 stock/C comparisons cover all494 native instruction bytes;724 actual cached-class cases and nine initialized-read failure cases pass. Four compiled defects are rejected. All842 prior nongenerated objects remain unchanged; imports are65 application and 22 bootloader symbols.

The [C NV recovery report path](nv-recovery-report-c-review.md) closes its report import.1,356 comparisons cover all686 native instruction bytes;774 actual cached-class cases and two initialized-failure cases pass. Four compiled defects are rejected. Reporter return values are deliberately defined in C rather than inherited from void provider registers. All843 prior nongenerated objects remain unchanged; imports are64 application and 22 bootloader symbols.

The [C fill-only NV recovery merge](nv-recovery-merge-c-review.md) closes its merge import.3,666 trace comparisons cover all984 native instruction bytes;440 actual cached-class cases and14 fail-closed cases pass. Six compiled defects are rejected. All844 prior nongenerated objects remain unchanged; imports are63 application and 22 bootloader symbols.

The [C module/NV recovery route](nv-recovery-route-c-review.md) connects the existing envelope handler, removes module/query assembly and bounds below-minimum lookup.2,721 module and25 query comparisons cover all198 native bytes;288 complete C recovery-route cases and6,378 touch regressions pass. Five compiled defects are rejected. All843 other nongenerated objects remain unchanged; imports are62 application and 22 bootloader symbols.
