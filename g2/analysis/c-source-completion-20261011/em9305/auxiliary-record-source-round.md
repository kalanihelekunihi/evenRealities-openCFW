# Auxiliary record source round

Reduced native 0x304360..0x30436a callback installer, 0x312d80..0x312da4 record initializer, and 0x30c1d4..0x30c1e8 registration wrapper to C in controller_init.c. Native ARC objdump uses authenticated official record 3 at base 0x302400. The delay-slot handler byte write precedes callback installation. The initializer clears 36 bytes at 0x805f04, stores the handler at +1, and installs a relocated source callback pointer at 0x801640.

Callback bodies 0x312ca0 and 0x333a00 remain unresolved source contracts; callback ABI, absolute placement and hardware behavior remain unqualified. Target build em-auxiliary-record-round is pending. Previous em-ll-lower-regions-round and ll-regions-codec-closure-integrated-round completed selected candidate compilation/linking successfully; strict completion returns exit 2 because source_complete remains false. Full-source components complete: 0/6.

The initial auxiliary record target build passed selected compilation/linking. Added completion and idle ring callbacks 0x333a00..0x333a60 after inspecting their native bodies. These use four-entry wrapping (BMSK bit 1), gated state bytes, and the existing event-post provider. The 0x312ca0 handler remains unreduced. A fresh target build is pending for these callbacks.

## Auxiliary event-handler reduction

Reduced native 0x312ca0..0x312d80 to C: four-entry event ring drain, state/event dispatch, descriptor callbacks, timer disarm, completion/idle event reinsertion, object rechecks after callbacks and halfword maximum elapsed accounting. Eight newly exposed child code contracts remain (303f8c,303ef0,303f50,303f68,304394,333780,333690,3339cc); they are external source symbols rather than jumps to stock code. Ambient argument-register behavior, native equivalence and runtime remain unqualified. Target build em-auxiliary-handler-round is running. Full-source component completion remains 0/6.

## Small child source round

The auxiliary handler selected target compilation/link passed. Reduced four child bodies from authenticated native ARC disassembly: 303f8c wrapping subtraction followed by signed MAX zero;303f50 byte flag read ignoring incoming object;303f68 current-object pointer read;304394 conditional byte flag set with native zero/address return. Corrected prepare303ef0 call signature to pass object, matching the delay-slot MOV R0,R14 at312d00. Four of the original eight auxiliary child bodies remain unreduced:303ef0,333780,333690,3339cc. Target em-auxiliary-small-children-round is running. These observations do not prove native runtime equivalence, layout or hardware behavior.

## Expiry callback round

Small-child selected ARC compilation/link passed. Reduced 3339cc..333a00 expiry callback to C: unsigned state-minus-one gate accepts only states1/2, disarms channel0, writes event2 to four-entry ring and posts handler event1. Remaining original child bodies:303ef0,333780,333690. Inspection of333780 extended the body through333804 and exposes a further callback333a60; that full list-removal/reinsertion body is not yet source-owned. No native runtime equivalence claim. Fresh target em-auxiliary-expiry-round pending.

## Prepare provider round

Reduced303ef0..303f50 to C, preserving installed-object write, flags, old-provider callback and optional selection, re-read product identifier, and object prepare callback. Native30fd2c is J[blink] with no side effects and was not replaced with an inferred hardware action. One new genuine child contract314d94 (provider selector) is exposed. Indirect callback ABI remains unqualified; the old-provider callback retains the native callback address in R0. Original unreduced auxiliary children now333780/333690, with downstream333a60 and314d94 also open. Target em-auxiliary-prepare-round is running; native/runtime equivalence remains unproven.

## Provider selector round

Reduced314d94..314db8 selector: calls the selected product callback at80164c+index*24 with native R0 retained as callback address, writes selector byte8016bc then active byte8016bd, returns index.30fd6c confirmed J[blink] no-op. No new code import; product callback registration/ABI remains unqualified. Original333780/333690 and downstream333a60 remain unreduced. Target em-auxiliary-selector-round running.

## Transition callback and integration

Selector selected target build passed. Reduced333a60..333a94 transition callback to C: accepts states0/1, disarms only state1, enqueues event3 and posts existing handler event1; returns state when gate rejects. Original333780 and333690 remain unreduced. Added Audio short formatter exact-source DP FPU override in its auto-glob builder, matching worker native VFP findings. All-six target integration auxiliary-transition-audio-formatter-integrated-round is running. Full-source completion remains0/6.

## List transition reduction

Reduced333780..333804 list transition and303f80..303f8c guard-interval getter. The source removes the current object, repairs head/tail, updates deferred deadline, handles expiry callback, conditionally inserts before next object with the native BN subtraction-sign condition, and emits transition event through source-owned333a60. The native return register differs across branches and selected callers discard it; this source uses void and retains a native ABI gate. Remaining original auxiliary child333690 (timer arming) is unreduced. Target em-auxiliary-list-transition-round running. Six-image integration auxiliary-transition-audio-formatter-integrated-round still live at last poll.

## Auxiliary timer arm source

Reduced333690..3336d8 and310110..310128 to C, closing the original eight child bodies exposed by312ca0. Preserved head load before critical enter (delay slot), current/guard sampling, signed-clamped difference, unsigned guard+25 comparison, callback/deadline install, channel0 enable and critical exit before boolean return. The closure is a selected C call-graph milestone, not full binary/source or runtime equivalence. Callback ABI, native instruction behavior, product configuration and placement remain unqualified. Target em-auxiliary-timer-arm-round is running. Other LL/common/radio bodies remain unreduced, full-source0/6.

## Common initializer source round

Auxiliary timer selected target build passed. Reduced common initializer30c038..30c074 ordered thirteen-provider chain, registry314538..314548 and four child initializers302e90/302ea4/302ec8/302ed8 to C. Nine common child bodies and seven source callbacks remain explicit imports; no raw stock function addresses substituted. Callback ABI remains unqualified. Target em-common-callback-registration-round began before final common wrapper append; receipt hash must be checked and wrapper rebuilt if mismatched. Full-source0/6.

## More common callback providers

Reduced302ff4,303008,303d18 from authenticated native branch-delay argument setup. Each installs a relocated source callback pair in slots4/5/2 respectively. Six original common children and thirteen callbacks remain open in this selected graph; source callback signatures remain ABI-unqualified. Fresh target em-common-pair-providers-round running.

## Common reset and paired provider round

All-six auxiliary-transition-audio-formatter-integrated-round completed selected compilation/link successfully; full source_complete false throughout. The earlier common registry build also passed selected ARC compile/link. Reduced303f94 reset132-byte record after authenticated no-op30fd38, and303d2c ordered pair slots0/1 with shared secondary. Four original common child bodies remain (3032cc,3102fc,303650,302f80), sixteen callback bodies remain explicit source imports. Target em-common-reset-pair-round running. These counts apply only to this selected common graph, not whole-image completeness.

## Common slots9/13/15

Reduced302f80 slot13 plus shared-record reset, and303650 ordered slots9/15 to C from native disassembly. Two original common children remain (3032cc,3102fc), twenty callbacks remain explicit source imports. Build em-common-last-small-providers-round running. Selected compile/link closure is still not full-image source completeness.

## Common mask and provider registry source

Reduced3102fc ordered two halfword mask stores and native return address,30436c four-callback registry in reverse native store order,304384 extra callback registry. One original common child3032cc remains unreduced; its native inspection exposes actual lower31028c via30fae4, rather than a no-op. Current registry build pending.

## Common initializer child closure

Reduced3032cc..303340 ordered hardware init, provider slots1/2/3, extra callback slot1, and176-byte registry reset. All thirteen original common initializer children are now C bodies. This exposes actual hardware lower31028c and eight provider callbacks; those remain source contracts. There are28 common/provider callback contracts total in this selected graph. This milestone does not close the whole controller graph or binary census. Target em-common-provider-init-round running.

## Hardware common init lower

Reduced31028c..3102fc ordered record clear, ROM facade, radio mask, delay-slot MMIO writes before interrupt-mask calls, timer-mask, calibration and final limit setup. Five genuine source lowers remain312094/310ba4/310bd0/311ffc/310314; resident ROM ABI remains unresolved. Native reference inspected directly from authenticated record. Target em-common-hardware-init-round running.

## IRQ/timer mask bodies

Reduced310ba4 and310bd0 native shift/mask, CLRI/SYNC, MMIO read/modify/write, SETI and native return semantics. Native IRQ disable return retains shift mask, while enable returns merged byte; timer returns merged word. Three hardware lowers remain312094/311ffc/310314. Target em-common-mask-providers-round running. ARC instruction/IRQ runtime remains unqualified.

## Radio mask and packet-limit wrapper

Common hardware init selected target build passed. Reduced312094 nine-bit BMSK plus halfword store and310314 packet-limit wrapper byte store with original full result return. Exposed lower3047fc remains unreduced. Calibration311ffc inspected; XB FU and VPACK2HL semantics must be established before a faithful C/adapter reduction. This is an evidence question, not an external blocker: native tooling remains available. Target em-common-radio-mask-limit-round running.

## Packet limit full body

Reduced3047fc..30482c to C with three real lower contracts30f31c/30f65c/3119b0, zeroed revision byte, failure-path revision result, special revision10 default result, low-byte clamp6 and final signed-byte extension. No default fallback substituted for failed revision read. Native stack-pointer/child ABI remains unqualified. IRQ/timer-mask target build passed. Target em-common-packet-limit-round running.

Provider crosscheck found30f31c already source-owned as controller_available_level; packet limit now reuses it. Only30f65c/3119b0 are new genuine lower contracts. Target build began before this binding correction: receipt source hash must be checked and final corrected source rebuilt.

## Packet default table provider

Reduced30f65c..30f668 index truncation and signed byte lookup to C. Product table at3344e0 remains typed external data: exact extent and classification need qualification before ownership; no adjacent binary bytes copied speculatively. Packet revision3119b0 remains unreduced and uses XBFU plus bounded68-entry search. Corrected30f31c binding remains current source. Target em-packet-default-provider-round running.

## Revision search and attributable table

Reduced3119b0..3119f0 reverse68-record search to C with native XBFU176 retained inline, signed table-key bytes, match-only output mutation and native equality return. Extracted exactly204 data bytes at333ff0 from authenticated record3 inspection, extent established by native68*3 lookup, source SHA comment retained. No executable code copied into source. Packet-limit code child graph now source-owned; default lookup table product and instruction runtime remain unqualified. Target em-packet-revision-provider-round running.

## Calibration reduction

Reduced311ffc..312094 table selection, MMIO samples, wrapping offsets, unsigned and signed validity checks, conditional MMIO write and boolean result to C. Retained native XBFU40 and VPACK2HL inline rather than guessing arithmetic; indexed table remains product RAM pointer80fd54. All five hardware init lowers now have selected C bodies, with downstream product/native runtime gates preserved. Packet-default target selected build passed. Target em-common-calibration-round running.

## Common callback tail entries

Reduced3151cc/3151d0/314728 native tail entries through30fab4 to actual310580 activation lower. Preserve R0 argument/return in typed C; no no-op substitution. Twenty-five original common/provider callbacks remain, activation310580 exposed as genuine lower. Target em-common-callback-tail-round running.

## Shared activation body

Calibration selected ARC compilation/link passed, including retained XBFU and VPACK2HL instructions. Reduced310580..3105b8 to C: active-state short circuit, timer mask disable, restore lower, ordered two-byte flags read, optional radio control and active byte write. Native branch return retained (one on alreadyactive, second flag byte when no control call, control result otherwise). Two real lowers312410/311f90 remain. Target em-common-activation-provider-round running.

## Activation lower closure

Reduced311f90 control-word bit augmentation and312410 MMIO/AUX restore to C. Preserved original first input bits, nonzero second as bits1/3; AUX1666 writes4 then8 and recordflag set after both. Activation selected code graph now source-owned with original native ROM/product/runtime gates intact. Target em-common-activation-lowers-round running.

## Pending/completion callbacks

Reduced31472c and3151d4 activation/pending/completion bodies plus314754 activation tail to C. Original R0 saved across activation, pendingcell8015e0 cleared beforecallback, offsets112/104 and116/108 retained. Native dynamic callback ABI beyond explicit arguments remains unqualified. Twenty-two original common/provider callbacks remain. Target em-common-completion-callbacks-round running.

## Provider dispatch and no-op tail

Activation-lower target selected compile/link passed. Reduced3143f4 record-indexed secondary dispatcher with native R0/R1/R2 preservation, and314580 authenticated no-op tail preserving R0. No absent behavior inferred from an unresolved provider. Twenty original common/provider callbacks remain unreduced; dynamic ABI beyond explicit registers remains gated. Target em-common-dispatch-callback-round running.

## Authenticated no-op callbacks

Reduced31446c input-preserving no-op tail and314584 zero-return callback after tracing30fabc and30fae0 to authenticated J[blink] bodies30fae8/31055c. No inferred provider behavior; exact native return distinctions retained. Eighteen original common/provider callbacks remain unreduced. Target em-common-noop-callback-round running.

## Channel constructor callback

Dispatcher target selected ARC build passed. Reduced3152bc channel constructor: source-relocated callback pointers, ordered word/byte configuration, record channel read, explicit four-register start call and conditional signalling. Seventeen original common/provider callbacks remain; three actual channel lowers314ea4/314fa4/314db8 exposed. Callback ABI/native runtime remains unqualified. Target em-common-channel-constructor-round running.

## Product descriptor notification callback

Reduced31537c..3153bc preparation, relocated handler bind, timestamp write, product callback with delay-slot state clear, and conditional finish to C. Path-dependent native return intentionally gated with void consumer ABI; wider callback arguments remain unqualified. Sixteen original common/provider callbacks remain, four actual lower contracts exposed. Target em-common-notification-callback-round running.

## Radio bind record

Channel constructor selected build passed. Reduced30fc10 exact16-byte record copy to existing source-owned memcpy, preserving native destination return805cf4. Preparation30fb4c remains larger actual hardware routine; its native first three child calls310450/310474/310570 inspected. Target em-radio-bind-record-round running.

## Radio prepare lower entries

Notification callback target selected compile/link passed. Reduced310450 setup tail,310474 exactMMIO word store,310570 product-flag-gated mode tail to C. Two genuine lower bodies31230c/312290 remain. Native source used to establish gates/returns, not guessed product behavior. Preparation30fb4c still requires full reduction before these enter its selected graph. Target em-radio-prepare-lower-round running.

## Full radio preparation

Reduced30fb4c..30fc10 full configuration branching, ordered byte/halfword product writes, setup/timestamp/mode calls, status mutation, transform and final hook. Four actual lower bodies3104d8/310284/33322c/310454 remain explicit; earlier setup/mode tails retain their two lower contracts. No guessed product descriptor values. Target em-radio-preparation-full-round running.

## Radio status/default query

Reduced3119f0 default mapping via existing source providers,311a00 fresh/stored signed byte status,310284 zero-argument status tail to C. Product80fd44 record and default table remain unresolved data contracts. Native control and sign extensions preserved. Target em-radio-status-query-round running.

## Mode indexing and product record update

Full radio-preparation target selected compile/link passed. Reduced311a20 signed clamp/min/range-byte algorithm and312290 product mode/default/index/revision fields to C. Source uses existing attributable204-byte revision data; valid native index domain remains a product input gate, no out-of-range fallback added. Target em-radio-mode-provider-round running.

## Radio setup MMIO

Reduced31230c setup word/control test/alternating byte marker, preserving branch-delay test on original input before R0 overwrite; reduced neighboring312330 enable-bit MMIO with original R0 return. These bodies are C, not hardware-validated. Radio configure3104d8 inspected through310528; remaining tail still needs reduction. Target em-radio-setup-mmio-round running.

## Radio configuration full tail

Mode-provider selected ARC build passed. Reduced3104d8..31055c full original-input byte stores, mode mapping, halfword baseline, selected encoded word and tail argument order. Native second mode4 shares mode2 path (branch delay R0 overwrite checked), not default mode0. Genuine apply lower3120a0 remains. Target em-radio-configuration-full-round running.

## Radio finish wrapper

Setup-MMIO selected ARC build passed. Reduced310454 original selector preservation, ordered probe/apply, product-flag boolean and final two-register mode child. Three actual child bodies311958/3122c0/312344 remain. Target em-radio-finish-provider-round running.

Reduced311958 unsigned channel remap to C from native conditional increments and special37/38 cases. Only3122c0/312344 remain in finish lower graph. Build started before remap append; receipt source hash requires current-source verification/rebuild.

## Radio finish apply

Configuration and finish-wrapper selected ARC builds passed. Reduced3122c0 signedMIN39 product lookup, nibble encode and ordered MMIO clear to C; product table pointer80fd4c and valid input domain remain gated. Last finish lower312344 contains unrecognized raw instruction382f000e, requiring instruction qualification/preserved adapter before reduction. Target em-radio-finish-apply-round running.

## Radio transform

Reduced33322c flags, record rechecks and optional data/byte transform;310498 ordered flag stores and swapped truth-value control args;310560 exact16-byte copy. Three actual transform lower bodies3104bc/31048c/3104b0 remain. Target em-radio-transform-round running.

## Transform lower closure

Finish-apply selected target build passed. Reduced31048c/3104b0 byte stores preserving untruncated R0, and3104bc exact8-byte copy to existing source-owned memcpy. Transform selected code graph now source-owned; product record/ABI/native runtime still unqualified. Target em-radio-transform-lowers-round running.

## Alternate channel binding callback

Radio-transform selected target build passed. Reduced3153bc alternate binding callback with native input preservation, source-relocated handler pair, timestamp/context fields, exact record copy and state clear before indirect callback. Fifteen original common/provider callbacks remain; two actual channel callbacks3151fc/315260 exposed. Dynamic ABI/native runtime remains unqualified. Target em-common-alternate-bind-round running.

## Radio registry callback round

Completed C reduction of native callbacks 0x314548, 0x314558 and 0x314568, ordered setup 0x30fac0, callback stores 0x310340/0x31034c and enable store 0x310480. Native ARC disassembly confirms delayed stores and calls. Callback addresses now use source relocations; real 0x333268/0x3330d8 callback bodies remain explicit imports. Registry ABI is void; incidental native return-register effects are unqualified. The final 0x30fae0 tail in 0x314568 reaches authenticated no-op 0x31055c.

Remaining original common/provider callbacks: 12 of the original 28, plus newly exposed descendants, product data and runtime/layout gates. This count is local graph progress, not image coverage. Build receipt: `g2/build/c-firmware/20261011/em-radio-registry-callback-round/receipt.json` Target C compilation and selected relocatable link PASS; strict build exits 2 because `source_complete` remains false.

## Stack descriptor callback round

Completed native C reduction for 0x31481c and its 0x30fc28 copy/MMIO helper. Ordered callback registration, context and timestamp stores, conditional 20-byte template/zero descriptor, bind copy, and selector 257 request follow authenticated ARC instructions, including delay slots. The template at 0x3343f8 remains an explicit typed product data import; callback bodies 0x3146a4/0x3146c4 and request lower 0x30faec remain real imports. No placeholder behavior added. Original common/provider callback remainder: 11, excluding exposed descendants. Source return uses native R0; registry ABI still requires broader runtime qualification. Target build: `em-radio-stack-descriptor-lower-round`.

## Secondary notification callback round

Native 0x314888..0x3148cc is now C: radio prepare, preserved root primary callback, source secondary callback, timestamp/context stores, bind-copy, delayed byte clear before descriptor notification and conditional auxiliary finish. Source callback 0x3146d4 remains a true imported body. Native return register is path dependent and current registry consumer discards it. Original common/provider remainder is 10, excluding newly exposed descendants. Previous stack descriptor lower round target C compilation PASS with source completeness false. New target receipt: `em-radio-secondary-notification-round/receipt.json`.

Secondary notification round verification: ARC target compilation PASS, relocatable link PASS; strict completeness gate remains false. Native next descendant 0x3146d4 inspected: its indirect callback retains callback address as R3 and existing current-object/argument registers, requiring a typed four-argument callback contract. Pending source reduction preserves this ABI requirement rather than substituting a generic callback.

## Radio completion child round

Native 0x3146d4..0x314728 reduced to C with four-argument callback ABI, counter increment before current-object query, second current-object query, pending field clear, descriptor stores, callback address as native R3, optional second callback, and conditional activation/finish. Incoming R2 is dead; no source implementation fabricated. All child calls reuse existing selected source providers. Target build `em-radio-completion-child-round`; bounded native execution remains unqualified. Original callback remainder stays 10: this is an exposed descendant.

## Fixed context callback round

Native 0x3148cc..0x314908 reduced to C with prepared input preserved, fixed context four, timestamp copy, two source callback relocations and descriptor callback ABI. Exposed 0x314758/0x3147b4 remain real source gaps. Original callback remainder: nine. Native instruction reduction, no ARC execution qualification. Build receipt `em-radio-fixed-context-round/receipt.json`.

Completion-child round verified: ARC target compilation and selected relocatable link PASS; source completeness remains false. Fixed-context callback target build is pending.

## Five-input radio completion child

Native 0x314758..0x3147b4 reduced to C. Preserves descriptor bytes 125/124, conditional root counter, pending clear, required/optional four-register callback calls, auxiliary query and unsigned first-input <7 / 0x51 bit test. Native delayed assignment means non-activation finish receives 0x51, preserved explicitly. All child providers source-owned; no native null guard was invented. This is an exposed child; original remainder stays nine. Target build `em-radio-five-input-completion-round`. Native ARC execution remains unqualified.

Five-input completion child verification: target C compilation and selected relocatable link PASS; source completeness false.

## Runtime primary callback descriptor

Native 0x314908..0x31497c reduced to C: runtime callback cell sampled twice, secondary source relocation, context at descriptor+108, timestamp, bind copy, 20-byte conditional template/zero descriptor and request object 0x8016f8 selector257. Data template and secondary 0x314a88 body remain honest imports; no raw executable code copied. Original callback remainder eight. Build `em-radio-runtime-primary-round`; native execution unqualified.

## Temporary descriptor preparation callback

Native 0x31497c..0x3149d4 reduced to C, preserving repeated object+44 loads, transient descriptor field replacement/restoration, STB.AB old-base write, runtime primary pointer, zeroed 20-byte stack descriptor and ADD1 record+120 request. Real request 0x30fc68 remains imported. Original callback remainder seven. Native-disassembly-derived source; target build pending `em-radio-temporary-descriptor-round`.

Runtime-primary callback round verified: ARC target compilation and selected relocatable link PASS; full source/payload remain incomplete.

## Timing-adjusted scheduling callback

Native 0x3149d4..0x314a88 is now C: current time, signed-clamped elapsed query, fallback timestamp+guard adjustment, prior timestamp capture, optional descriptor notification, schedule result branch, record binding, conditional product template and final descriptor request. Real scheduler 0x314370, secondary callbacks 0x314c04/0x314d18 and exact 20-byte template 0x3343a8 remain explicit source/data imports. Original callback remainder six; this does not measure full image coverage. Build `em-radio-scheduled-prepare-round` running. Previous temporary descriptor callback target C compilation and selected relocatable link PASS. Native execution equality remains unqualified.

## Conditional descriptor callback

Native 0x3152fc..0x31537c reduced to C with callback registration, old-base STH.AB, auxiliary gate, optional descriptor+160 callback preserving callback pointer R2, preparation/binding and descriptor+100 request. Source callbacks 0x315000/0x315108 and exact20-byte product template 0x33440c remain imported. Original remainder five. Timing-adjusted prepare round target compilation and selected relocatable link PASS; source completeness false. New target `em-radio-conditional-descriptor-round` running.

## Expanded conditional descriptor callback

Native 0x3153fc..0x315490 reduced to C, including secondary enable field at record+232, ADD2 record+160 callback and conditional timestamp writes +236/+240. Preserves original load/write order and no synthesized defaults. Original remainder four. Real callback/request bodies and data template still imported. Build `em-radio-expanded-descriptor-round` running; native execution unqualified.

Conditional descriptor round target C compilation and selected relocatable link PASS; source completeness false.

## Fixed product descriptor callback

Native 0x315490..0x3154e0 reduced to C: metadata writes before prepare, source callbacks, exact 16-byte bind and 20-byte template, descriptor pointer +108 and halfword selector +112. Two real callback bodies and product template remain imported. Original remainder three. Build `em-radio-fixed-product-descriptor-round`; native execution unqualified.

## Zero descriptor and shared finish callbacks

Native 0x3154e0..0x315534 and 0x315534..0x315544 reduced to C. Preserves root context, zero-descriptor copy before stack reuse, halfword+word request record, selector1 and activation-result forwarding. Original callback remainder one (0x314408), with exposed descendants and product inputs still open. Expanded-descriptor target compilation and selected link PASS; fixed-product descriptor build still pending. New target `em-radio-original-callback-final-pair-round`.

## Original callback inventory C reduction completed

Native primary dispatcher 0x314408..0x31441c is now C, with byte index scaled eight, null returning original object and tail callback retaining record R1/address R2. This completes C reduction of the original 28 common/provider callback inventory; exposed child callbacks, lower providers, product data and whole-image bodies remain open. Fixed-product descriptor round target compile/link PASS; final-pair round still running. New target `em-radio-original-callback-inventory-round`. This inventory completion is not source completeness for EM9305.

Original callback inventory round ARC target compilation and selected relocatable link PASS. Sixteen named channel callbacks/start providers remain in the current lexical source frontier; other lower/data/ROM/layout obligations also remain. Fresh Boot candidate compilation PASS; Touch rebuild running.

## Channel completion bridge pair

Native 0x3146a4..0x3146c4 and 0x3146c4..0x3146d4 reduced to C. Five original inputs plus sampled current object forwarded as six registers, and input/current completion pair preserve delay slots. Actual larger providers 0x303fb8/0x304140 remain typed imports. Named channel/start frontier falls16→14, exposing two real provider bodies. Build `em-radio-channel-completion-bridge-round`; no native runtime qualification.

## Descriptor product data reduction

Four exact 20-byte descriptor templates at 0x3343a8,0x3343f8,0x33440c,0x334434 now source-owned constant C arrays, with SHA256 comments. Authenticated native copy length establishes extent; byte patterns are mode1/mode3 plus nineteen zero bytes. These are data, not embedded executable bodies. No neighboring data inferred. Source graph removes four template imports. Target build `em-radio-descriptor-templates-round` running.

## Descriptor completion child

Native 0x3151a0..0x3151cc reduced to C: modulo256 count increment before current-object query, required descriptor+104 callback with own address R2, auxiliary gate and optional activation/finish. No native null guard invented. All lower code providers already selected C. Named channel/start frontier14→13. Build `em-radio-descriptor-completion-child-round`; native execution unqualified.

Channel completion bridge target C compilation and selected relocatable link PASS. Fresh all-six experimental candidate build launched as `radio-callback-inventory-all-six-round`; strict completeness remains open independently of candidate compilation.

## Follow-up and counter completion child

Native 0x315544..0x3155c4 reduced to C, including null current-object return, descriptor callback ABI/R3=self, BSET(first,2)==4 branch, typed follow-up provider and four counter offsets. Native final R0 counter base preserved. Real follow-up 0x30fb3c remains imported; template source-owned. Channel/start frontier13→12. Build `em-radio-followup-counter-round`; native execution unqualified.

Descriptor completion child target compile/link PASS. Follow-up provider 0x30fb3c inspected: stores selector halfword805d38 and wrapping first+1 word805d34 before native tail310374. This larger lower must be reduced next; no noop or guessed return introduced. All-six build remains live under root session82040.

## Follow-up driver

Native 0x310374..0x3103e0 and tail wrapper 0x30fb3c..0x30fb4c reduced to C: stack output parameters, mode-conditioned bit byte, driver children, mask and source callback scheduling. Actual adjust/bit/commit/schedule bodies and callback0x333480 remain real imports. No lower is stubbed. Target `em-radio-followup-driver-round` running. Prior follow-up/counter target compile/link PASS; source completeness false.

## Radio byte commit providers

Native 0x311fb0..0x311fcc and 0x311fcc..0x311ffc reduced to C: five descending byte writes and16 ascending/13 descending byte writes, preserving LD.AB/ST.AB old-address accesses and native return R0. Volatile accesses preserve copy/write sequence. No embedded executable bytes. Two real provider imports removed; adjustment, scheduler and callback still open. Build `em-radio-byte-providers-round`. All-six source candidate build currently passed Codec/EM9305/Touch/CASE and is processing Boot.

Follow-up driver target compilation/selected link PASS. Fresh all-six candidate build finished: all six candidate compilations PASS, all six source_complete false/full_payload_linked false. Durable receipt path `radio-callback-inventory-all-six-round/receipt.json`; latest provider edits postdate this snapshot.

## Follow-up first-parameter store ABI correction

Direct native recovery of 0x3101f4 shows it stores R0 to805ec8 and returns R0. Caller-supplied R2/R3 stack pointers and R1 are ignored; earlier typed output-provider contract was overly broad. Caller now uses one live input and retains its initialized stack values; source store implemented. No output mutation invented. Byte providers target compile/link PASS. New build `em-radio-followup-store-round`.

## Activate and zero-descriptor completion child

Native 0x3155c4..0x315640 reduced to C: source activation, required descriptor callback, zero-input/result-dependent follow-up, timestamp increment, zero template copy before stack request reuse, counters +12/+16 and native counter-base return. Native no-null-guard behavior retained. Existing lower source contracts reused; no new providers fabricated. Channel/start frontier12→11. Build `em-radio-activate-descriptor-completion-round`.

## Counter-gated completion provider

Native 0x304140..0x304184 reduced to C with modulo256 store, original-count==1 gate, finish argument count+1 (incoming R0 overwritten), explicit boolean result and zero-descriptor follow-up. Every lower is already selected source-owned C. No native return guessed. Build `em-radio-counter-gated-completion-round`; native execution remains unqualified.

Activation/descriptor completion child target compile and selected relocatable link PASS, source completeness false. Codec worker reports typed data byte oracle744 nonpointer bytes and pointer relocations pending final placement; these remain separate from root EM source evidence.

## Extended five-input completion

Native 0x3151fc..0x315260 reduced to C with byte133/132 stores, counter-zero conditional fourth-input context store, pending clear and exact callback ABI, native unsigned first<7/0x51 gate and delay-slot finish argument. Every lower selected source C; no null guard invented. Channel/start frontier11→10. Counter-gated completion target compile/link PASS. New target `em-radio-extended-completion-round` running. Native execution unqualified.

Next native channel body0x314fa4 inspected: null-current path explicitly reads pointer at absolute0x2c before counter handling, rather than guarding or treating current==0 as idle. This requires preserving native memory-map/descriptor interpretation in subsequent source recovery; no speculative null fallback introduced.

## Counter-selected channel restart completion

Native 0x314fa4..0x315000 reduced to C with direct architectural0x2c read in zero-current path, counter branch, exact20-byte template and typed restart lower. Product template source-owned with exact hash/extent. No invented null fallback. Channel/start frontier10→9; native memory-map and execution qualification remain open. Build `em-radio-channel-restart-completion-round`.

## Deferred channel phase completion

Native 0x315108..0x3151a0 reduced to C with counter0/2/3 phases, mode2 timestamp computation, direct architectural descriptor access, exact template, deferred runtime callback ABI/R2=self and source activation/finish. Real timing312b88 and continuation314f54 remain imports. Channel/start frontier9→8; memory-map/runtime qualification open. Build `em-radio-deferred-channel-phase-round`.

Restart callback build failed Werror=array-bounds on architectural address0x2c read. Corrected both native zero-current reads to explicit ARC LD inline assembly with memory clobber, retaining identical native address and avoiding C low-address object bounds inference. No null fallback or suppressed warning. Repair build `em-radio-low-address-native-load-round`.

## Descriptor continuation provider

Native 0x314f54..0x314fa4 reduced to C: optional callback160 with explicit R2=self, callback adjustment, preparation via object+44, timestamp increment before bind-copy, zero20-byte descriptor, ADD2 record+136 request and inverted zero-success result. Selected source providers reused. Timing312b88 native opcode301c0040 disassembler class is guessed; its mode3 arithmetic remains a real unresolved provider rather than invented multiply. Build `em-radio-descriptor-continuation-round`.

Low-address native-load repair target compilation and selected relocatable link PASS. This restores successful target compilation for both restart and deferred-phase callbacks while preserving actual native LD access; runtime mapping remains unqualified.

## Pending completion and retry callback

Native 0x314d18..0x314d94 reduced to C: conditional pending callback140, byte148/word132 clears, original-count gate with finish inputcount, required callback124, zero descriptor follow-up39 and retry314594. Native first input preserved independently of current object, indirect R2=self. Retry body remains real import. Channel/start frontier8→7. Build `em-radio-pending-retry-callback-round`.

## Radio channel3 scheduling provider

Native 0x311e60..0x311ee0 reduced to C: descriptor stores, wrapping end/encoded timing arithmetic, ST.AB old MMIO address and four-word stack descriptor, five explicit resident ROM calls, final1 return. ROM calls remain genuine typed ABI contracts, not invented implementations. Descriptor continuation target compile/link PASS. New build `em-radio-channel3-scheduler-round`. Native ROM/runtime/layout qualification open.

## Elapsed retry scheduler provider

Native 0x314594..0x314640 reduced to C, preserving original object, wrapping accumulation164, current-time capture, guard scheduling, four-register descriptor callback136, actual object descriptor148 flag and conditional template request39. Scheduler314370 remains honest code import. Pending retry callback target compile/link PASS. New build `em-radio-elapsed-retry-provider-round`; runtime qualification open.

## Channel cycle and submission

Native 0x314db8..0x314ea4 reduced to C with channel mask iteration, signed-byte stop/cycle, request timestamp branches, delay config303f74, descriptor callback and stack request. Timing312b88/custom opcode and timingadjust312c5c remain true imports. Channel/start frontier7→6. Native MMIO/memory-map execution open. Scheduler311e60 target compile/link PASS. New build `em-radio-channel-cycle-round`.

## Request critical-section providers

Native 0x310678..0x31069c and0x31069c..0x3106bc reduced to C with native CLRI/SYNC/SETI, depth re-read, modulo256 stores and path-specific return values. No underflow guard invented. Request30fc68 remains unowned because its multiply opcode301c0040 needs architectural classification. Channel-cycle target compile/link PASS. New build `em-radio-request-critical-round`.

## Request deadline/state providers

Native333450,3123d0,310600 and310640 reduced to C: nested critical deadline wrapping sign test, channel1 timer arm, optional control-mode register/trigger, state callback and base-store tail. Source callback preserves pointer R1 and no deadline arithmetic is saturated. All lower providers source-owned. Build `em-radio-request-state-deadline-round`. Critical providers build pending; native execution unqualified.

## Channel2 request and completion round

Native 0x311ef0..0x311f6e and 0x3105b8..0x310600 reduced to C. Channel2 preserves descriptor ordering `{encoded,end,F04058,0}`, MMIO ST.AB original address F04080, mode6/channel2 resident ROM calls, and optional bit preparation. Target compile and candidate relocatable link PASS in `em-radio-channel2-request-round`; strict exit2 reflects source incompleteness.

Native callback 0x33354c..0x333582 now source-owned, including the authenticated hook3101ec, activation path, captured timestamp plus halfword lead, and indirect callback register contracts. Build `em-radio-channel2-callback-round` pending. Five resident ROM ABI providers remain dependencies for this scheduler; native execution and whole-image placement remain unqualified. Six original channel/start frontier callbacks and the custom timing opcode contracts remain open. Deadline/state round target compile/link PASS. Full component completion remains 0/6.

## Pending channel completion

Channel2 completion target compile/link PASS. Native3147b4..31481a reduced to C, retaining required first callback108, record dereference prior to zero-current branch, pending clear/callback112, exact template3343bc, followup and finish branches, optional callback120. Native cancellation30fab8 is authenticated unconditional tail branch310580 and now source-owned. Five original channel/start callbacks remain. Build `em-radio-pending-channel-closed-round` running; runtime qualification remains open.

## Five-register completion state machine

Pending-channel/cancellation closed round target compile/link PASS. Native314a88..314c02 reduced to C with five input registers, original-byte LDB.AB state read, descriptor138/139/140/144/148 stores, two phase-specific callbacks, submit/bind path, hook branches and original activation/finish distinctions. Corrected its previous no-argument declaration to the instruction-backed five-register ABI. Native31199c..3119a8 byte flag setter is also C, returning the native address. Four original channel/start callbacks remain after this body reduction; no whole-image coverage percentage inferred. Build `em-radio-five-register-state-flag-round` running; native equivalence unverified.

## Packet completion callback

Five-register state and flag setter target compile/link PASS. Native314c04..314d16 reduced to C: six-register pending callback and successful clear, count increment before branch, status3/4 paths, packet check with native +76/+168 descriptor pointers, exact byte/word stores, callback116 result gate, 8-byte request fields and separate20-byte template, optional callback120, activation/retry/finish. Its earlier no-argument declaration is now the native five-register ABI. Packet check303404 and request30fcd8 remain explicit imports; three original channel/start callbacks remain. Build `em-radio-packet-completion-round` pending; runtime equivalence and whole-image closure open.

## Count-gated channel recycle

Packet-completion target compile/link PASS. Native314ea4..314f52 reduced to C with four-register callback ABI, count increment, nonzero status recycle, packet-check branch, callback116 gate, descriptor request fields, optional callback120, preserved checked/recycled value and activation/finish. Packet parser303404 entry inspected; full parser remains genuine import. Two original channel/start callbacks remain. Build `em-radio-count-recycle-round` running, native behavior unqualified.

## Extended descriptor completion

Count-recycle target compile/link PASS. Native315000..315108 reduced to C: five-input callback ABI, count1 gate, flag260 branches, byte227/177 and word180 stores, indexed entry208, callbacks152/156, optional hooks805c1c/805c20, zero descriptor and request2, native status-bit activation and finish. Native review corrected status-derived R0, single hook read, and retained indexed-pointer return path. One original channel/start callback remains; source body claims are not behavioral qualification. Earlier pre-review builds53794/22383 retain their snapshots; next fresh build must include final indexed-pointer repair.

## Original channel frontier inventory closed in source

Native315260..3152bc reduced to C with required callback112, pending clear/callback116, exact20-byte data template3343e4, followup versus activation/finish. Current lexical audit finds definitions for all16 names in the original channel/start frontier, in addition to all28 original common/provider callbacks. This is an inventory result only, not whole-image coverage or equivalence. Build `em-radio-original-channel-frontier-round` running. Extended-descriptor final reviewed build PASS.

Inspected request30fcd8: native custom opcode311c0001 remains unresolved (objdump guessed mpywhl). Inspected connected333064 descriptor flattening provider through3330d8: two-halfword branch, two header-byte prepend and chained copies; source recovery remains next work. No unsupported multiply semantics substituted.

## Descriptor flattening provider

Original16-channel frontier fresh target compile/link PASS. Native333064..3330d8 now C: selector1 first-buffer return, halfword2 header prepend with original store order, optional low-byte tail copy plus scratch state, and general chained header/body copies. All lower copy code source-owned; no opaque code arrays added. Build `em-radio-descriptor-flatten-round` running. Fresh all-six integration build `channel-frontier-closed-all-six-round` running to include current worker sources; whole source complete remains false.

## Address filter providers

Descriptor flatten target compile/link PASS. Native303df8..303e38 packed address lookup,303e38 reset,303e50 status and303e5c mode getter now C. Lookup retains byte count, eight-byte rows, high-kind OR, original load order, early-match/last-row result; reset returns the native second-byte address. These close identified lower parser contracts when303404 is source-owned; parser body itself remains open. Build `em-radio-address-filter-round` running. All-six build session46644 remains live, no restart.

## Address removal and provider release

Address filter target compile/link PASS. Native303e68..303ec0 removal now C, preserving high-first row reads/stores, final-row replacement and byte-count decrement. Native303ec0 mode-disable and303ecc..303ef0 auxiliary release now C; release clears current before optional indexed provider callback and preserves R1 callback address. Build `em-radio-address-release-round` running. Packet parser303404, timing custom opcode and whole layout remain open.

## Address classification provider

Release-provider target compile/link PASS. Native314470..314538 now C with address kind/high-word classification, resolve/no-resolve branches and conditional identity checks. Five lower native address providers remain distinct imports. Reviewed mode-zero identity-call R0=2 and post-call kind-byte return gate; mode-nonzero uses identity-call result. High-word then low-word load order retained. Final build `em-radio-address-classification-final-round` running; prior intermediate snapshots superseded for this body. All-six session46644 still running Main after five selected component compilation passes; whole source complete false.

## Identity lookup providers

Final reviewed classification build target compile/link PASS. Native31441c lookup,31445c existence,303954 conditional identity output,30396c status and303978 four-row exclusion lookup now C; original high-first loads, full kind shift16 versus boolean kind normalization and exclusion return polarity preserved. Two classification children now source-owned, three remain distinct imports. Build `em-radio-identity-lookup-round` running. Fresh all-six receipt `channel-frontier-closed-all-six-round/receipt.json` reports all six selected candidates compile and zero complete source payloads; checkpoint updated from receipt.

## Identity kind and accessors

Identity lookup target compile/link PASS. Native303a18 kind now source-owned, plus3039f0 sibling kind,303a40/303a60 nonzero pair copies,3039d0 consume-once flag. Original high-first word reads and conditional output writes preserved. Two classifier resolver children303bdc/303890 remain true imports; full parser303404 and timing/layout remain open. Build `em-radio-identity-accessors-round` running.

## Identity comparison and resolver instruction boundary

Identity accessors target compile/link PASS. Native3039a0..3039d0 five-register comparison now C, flag65 check and row56/60 comparison after identity lookup; build `em-radio-identity-comparison-round` running. Resolver303bdc native inspection exposes guessed multiply opcodes311c2f8d,309c0201,319c2201; do not substitute row-index multiplication without authenticated architectural semantics. Existing QPC opcode report concerns a different undecoded opcode and does not settle these instructions. Two resolver providers remain open.

## Identity setters

Five-register identity comparison target compile/link PASS. Native303c9c control word setter,303ca8 matching byte67 setter and303cc0 peer pair setter now C; original input return, conditional writes and high-first pair access order retained. Build `em-radio-identity-setters-round` running. Two resolver providers and larger parser remain open; these setters do not resolve custom multiply semantics.

## Request entry and address insertion

Identity setter target compile/link PASS. Native303cd8 request-start,303d58 current-request routing,303da4 deduplicated address insert and303dec mode-enable now C. Request-start pending fields stored before object query; current-request captures type/phase before template setup and selects true30fc68/30fcd8 imports. Exact20-byte template334420 source-owned. Address insert publishes byte count before high/low row writes and retains kind packing/capacity behavior. Build `em-radio-request-address-insert-round` running; custom multiply, resolvers and parser remain open.

## Private address wrapper and decoder boundary

Native31467c..3146a4 random/address wrapper reduced to C with native22-bit mask/bit22,24-bit low composition and R0/R1 return represented as uint64_t. Random310038 and hash314640 remain genuine imports; hash VPACK2HL semantics are not invented. Build `em-radio-private-address-wrapper-round` running. Inspected303a80 refresh; its guessed multiply opcodes remain unresolved. Tried objdump-Mmpy: option unrecognized; actual retained option list provides DSP/FP classes, not a producing-core configuration. No semantic claim made from guessed class.

## Random byte provider

Native310038..310088 now C, resident ROM10a7f8 ABI explicit, reverse chunk order and byte-truncated done/remaining arithmetic preserved, initial do-loop for zero length and native TRAP0 on ROM error retained. This trap is instruction-backed fatal behavior, not a placeholder. Lengths beyond byte counter range are not silently bounded. Build `em-radio-random-byte-provider-round` running; resident ROM behavior and hash314640 semantics remain unqualified. Codec worker now76source bodies with<=66potential body gaps in image-A retained raw-label census; this is separate from whole-image closure.

## Cipher wrapper

Random-byte provider target compile/link PASS. Native30ff0c..30ff70 encryption wrapper now C with48-byte scratch roles, key/input reversal, nested critical enter/exit, two explicit resident ROM contracts1009c0/10090c, output reversal and incidental stack-relative integer R0. Native stack placement/return and ROM execution remain unqualified; no hardware claim. Build `em-radio-cipher-provider-round` running. Refreshed local lexical source/declaration frontier for subsequent actual link/native audits; local declarations are not automatically missing graph providers.

## Common completion and address serialization

Cipher provider target compile/link PASS. Native3045c0 shared completion now C: dead incomingR0, optional provider callback24 after index*24, required controller callback after flag130/current clear, self address in R0. Native3045e8 six-byte serializer and304604 fixed6-byte forward copy now C, serializer store order4/0/5/3/2/1 retained. This closes shared completion import for the previously recovered callback graph, while indirect callback/memory-map execution remains unqualified. Build `em-radio-finish-provider-round` running.

## RX/TX trigger controls

Shared finish provider target compile/link PASS. Native312360..312390 receive trigger and312390..3123d0 transmit trigger now C, optional control-mode RAM/MMIO updates and unconditional trigger-byte writes retained, path-specific R0 returns preserved. Build `em-radio-rx-tx-trigger-round` running. Native312344 mode provider begins undecoded382f000e and remains genuine import;3120a0 larger apply body inspected but not substituted with a partial implementation.

## Apply register providers

Native312598 indexed MMIO halfword store and311990 masked13-bit timing store now C, retaining address/masked returns. These are complete small native children of the larger apply/control path, not substitutes for3120a0. Apply continuation inspection shows table writes and calibration;31197c VPACK2HL and312344 undecoded382f000e remain architectural gaps. Build `em-radio-apply-register-providers-round` running.

## Full mode apply outer body

Apply register providers target compile/link PASS. Native3120a0..312290 now full C outer body: ordered MMIO sequence with old-address ST.AB, config selection,600/600 calibration, three register records for mode0..3, signed-halfword timing offsets for mode0/1, secondary-mode register/control, pending flag clear or channel conversion/store. Original source table and root cells remain native contracts; packed timing31197c and channel convert311878 remain genuine lower imports. Build `em-radio-mode-apply-round` running. This closes outer configure3104d8 apply edge, not hardware qualification or full provider graph.

## Channel conversion

Mode apply target compile/link PASS. Native311878..311958 conversion now C, reuses source-owned level selection/default/index and revision table, native RAM/control update order and drive-strength thresholds. Channel prepare3124e4 remains explicit lower code provider. Build `em-radio-channel-conversion-round` running; native execution and timing packing unqualified.

## Channel preparation and control refresh

Channel conversion target compile/link PASS. Native3124e4 table threshold/mode preparation and31252c gated control refresh now C. Signed table bytes, optional bit14 clear, flag/control publish order, status double read, selector-dependent bit8/9 branch and path-specific R0 retained. Builds `em-radio-channel-prepare-round` and `em-radio-control-refresh-round` running. Mode apply's channel conversion chain is now source-owned; packed timing, mode opcode and wider graph remain unresolved.

## Packed timing and address hash

Channel preparation and control refresh target compile/link PASS. Native31197c timing pair and314640 address hash now C with the decoded native `vpack2hl` instruction preserved as inline ISA, matching the existing calibration approach. The hash retains three-byte store order, thirteen-byte zero tail, in-place cipher and halfword-then-byte loads; its scratch buffer explicitly has four-byte alignment. `em-radio-packed-timing-hash-round` target compile/link PASS; alignment refresh runs as `em-radio-packed-aligned-round`. This closes these two code providers without asserting arithmetic emulation, resident ROM execution, final placement or hardware qualification. Undecoded312344 and multiply-dependent providers remain unresolved. Whole component completion remains 0/6.

## Special mode and queued event routing

Aligned packed timing/hash and `em-special-mode-message-round` target compile/link PASS. Native30cb7c allocates its four-byte command, writes two0xff halfwords in native order, reads product handler and invokes source-owned31404c task enqueue/event-post body. Native30a484 complete queued routing now C: decoder output, link bounds, decoded unsigned912-byte stride, inactive/reject ownership release, length limits, protected count decrement, pending queue, process/post and indirect reject callback. Header32dae4 also C with sparse output stores and native `xbfu` inline ISA. `em-queued-event-routing-round` and `em-queued-header-decode-round` in progress. Two genuine processing children32d4b0/32d380 and product RAM/indirect callback contracts remain explicit; this is source reduction, not bounded native comparison or whole-image completion.

## Segment construction descendants

Queued routing, header decode and capacity32d4b0 target compile/link PASS. Capacity retains literal native additions, shifts, halfword truncation and min/max; no signed simplification of encoded constants. Native32d380 segmentation now C with queue ownership, protected rejection count, packet descriptors, mutable decoded fields, byte-truncated segment index, callback headers/flags and post-loop enqueue. Its `em-event-segment-process-round` target compile/link PASS. Native323d70 compact header encoder now C, including return length2/3 and native read/store order. `em-segment-header-round` in progress. Notify3181b4 and error32322c remain genuine descendants; no native runtime equivalence or final layout claim.

## Segment rejection callback

Compact header encoder target compile/link PASS. Native32322c five-byte error event and30e79c optional callback tail now source-defined, preserving initialized byte/store order and callback address in R1. The unused stack save area is not an event field. `em-segment-error-round` is running. Notify3181b4 remains a genuine code frontier; indirect callback execution and broader image closure remain unqualified.

## Segment notify and scheduler unlink

Error-event target compile/link PASS. Native3181b4 conditional notify now C, including scaled halfword offsets260/266, decoded unsigned1250 multiplier, native elapsed argument order and incidental path returns. `em-segment-notify-round` target compile/link PASS. Scheduler313354 remains explicit: the existing333780 stop C intentionally has void ABI, so its incidental R0 cannot be fabricated for the new caller. Native333804 list unlink is now C, including second next-pointer load and unchanged object return on the tail branch; `em-scheduler-unlink-round` running. No new runtime equivalence claim.

## Scheduler return ABI closure

Native333780 path returns were traced directly: absent deferred object returns the loaded next pointer; expired deferred object returns zero or callback R0; negative-order pending path returns reloaded pending pointer; remaining paths return333a60 transition R0. Its C ABI now preserves these returns and callback self address in R1. Native313354 scheduler cancellation now full C, retaining list scan, head-state branches, non-head unlink, post-stop callback and incidental result. `em-scheduler-notify-closure-round` running. This closes the remaining named descendant of the queued segment chain at source level; full native execution, product layout and whole EM9305 provider coverage remain open. Earlier void-return rationale is superseded by this newly identified consumer and instruction trace.

## Received routing and header descendants

Scheduler unlink and scheduler-notify closure target compile/link PASS. Native30a564 received routing now C: decoded length/availability checks, resize/redecode, link and stream lookup, capacities, pending queues, protected counter decrement, processing children, rejection callback and ownership release. Native31bc7c decoder now C with sparse stores, old-address LD.AB semantics, native `xbfu`, optional timestamp and extended fields, and returned header length4/8/12. Native31ab14 active stream lookup and31ab88 link lookup now C, preserving256/656-byte strides and native load/test order. `em-received-routing-round` and `em-received-decode-lookup-round` running. Genuine resize3048b0, readiness31825c and processing317680/318740 descendants remain explicit. No stock execution or whole-image completion claim.

Received routing and decode/lookups target compile/link PASS. Fresh unified `segment-descendants-all-six-round/receipt.json` captured2026-10-11T08:32:08Z passes candidate compilation for all six, but source_complete/full_payload_linked false for all; complete_source_payloads0. Main selected link1147defined/428unresolved/0duplicate, SHA034c338de73d92af7e80aaeaf3d6696f6749b959f6d926a5024fac2e728b470f. Snapshot predates subsequent source edits; use exact receipt scope only.

## Received readiness and fragment ownership

Native31825c readiness lookup and31b750 active-state/readiness flag now C. Native3048b0 fragment retention/assembly and304a98 release/clear now C: native count/kind branches, count publication before row store, dynamic count rereads, sixteen-bit allocation/offset truncation, first header copy plus subsequent payloads, original release and fragment cleanup. Decoder scratch outputs remain sparse and caller-owned; no zero-filled substitute. Builds `em-received-link-ready-round` and `em-received-fragment-round` running. Processing317680/318740 remain true code providers, and native execution/final whole payload remain unqualified.

Received readiness and fragment target compile/link PASS. Inspected317680 processing body: undecoded321c0302 at317718 remains an architectural arithmetic gap, so no partial processing replacement was emitted. Five complete connected leaves now C:316e5c pool dequeue,3175d0 compact stream header,316f50 header field wrapper,3175f0 gated prefixed allocation,31761c release. `em-stream-header-buffer-round` running. Source-owned leaves do not close the unrecovered parent body or its other children.

Stream header/buffer target compile/link PASS. Live Ghidra-MCP list_instances returned no running instances; pinned objdump/native evidence remains available. Received descendant checkpoint records nine new native bodies, the three passing builds and undecoded317718 arithmetic separately from execution qualification. Goal remains active, whole source completion0/6.

## Received link processing

Native318740..318878 link segmentation now full C: capacity/decoded length, pool allocation, one mandatory initial segment even for zero length, native13-byte stride and byte-truncated index, mutable decoded length, exact callback source/descriptor addresses, successful queue publication, failure optional callback and protected counter restoration/error event. Header318708 now C with native field masks and return2. `em-received-link-segment-round` running. This closes the link-processing branch of30a564 at source level; stream317680 remains open due to undecoded317718 arithmetic and other genuine children. Runtime callback, concurrency and final product placement remain unqualified.

Initial link-segment build failed solely on missing forward declaration for the already-defined32322c error helper. Added its exact uint32_t(uint32_t) declaration before the new caller; corrected build `em-received-link-segment-declared-round` running. No signature, native control flow or provider placeholder was changed.

Corrected link-segment target compile/link PASS. Native32fc88 zero-return hook and32fc8c pending-link release/restart or dispatch/event-kick now C; corrected their earlier void declarations to native uint32_t return. Native308614 protected byte-counter increment now C and returns critical-exit R0, not the stored counter. `em-link-pending-dispatch-round` and `em-link-counter-round` running. Pending lookup30858c contains undecoded309c040a and remains genuine, as does331d94 dispatch; no speculative stride multiplication was substituted.

Pending dispatch and counter target compile/link PASS. Local controller lexical census400definitions/112explicit extern declarations without local definition is refreshed; it is not a linker import total, native body census or full image coverage. All six whole-source completion gates remain open.

## Link accounting and pending packet child

Native331d94 now C: snapshot enable, packet byte2, packet/byte counter load/store order, conditional ownership release/restart, original enable boolean return. Native31ba54 pending packet child now C: old-address state byte read, state0/1 gate and queue removal at state+4, handler scratch unchanged on empty queue. Builds `em-link-accounting-round` and `em-pending-packet-take-round` running. Pending lookup30858c remains unrecovered because of undecoded arithmetic; its recovered queue child does not close the parent or establish runtime equivalence.

Link accounting and pending packet target compile/link PASS. Retained startup-hook receipt also records that Ghidra ARCompact misdecodes ARCEM startup operations; do not promote it to an independent oracle for undecoded ARCEM arithmetic. The current source and native listings remain the evidence for these two bodies. Whole source completion remains0/6.

## Primary dispatch and generated packets

Native32e3bc primary pending/accounting or event-kick and32e3e0 primary send/fallback five-byte event now C with corrected callback signatures, counters and old-address ST.AB payload order. Native331d60 primary16-bit byte accounting and308570 protected credit increment now C. Native32f794 fixed259-byte packet burst now C, preserving busy/zero-count returns, byte-truncated count-minus-one, native `xbfu` field operation, payload fill byte counter, allocation failure and unconditional busy clear. Builds `em-primary-dispatch-account-round` and `em-primary-packet-burst-round` running. Primary pending30853c contains undecoded308558 arithmetic and remains explicit; source reduction does not establish runtime execution or final payload layout.

Primary dispatch/accounting and packet burst target compile/link PASS. Fresh unified `primary-dispatch-crt-all-six-round` running to capture actual current provider graph. CASE worker semantically attributes all420 CRT bytes (exact native RAM comparison), but ambient selector/layout/body coverage remain open. Codec startup now selected with genuine imports and vector relocation identities, rather than isolated zero-import appearance; candidate body reduction is not whole source completion.

Unified primary-dispatch/CRT round settled: all6candidate_compilation_passed true; all6source_complete/full_payload_linked false, complete_source_payloads0. Selected relocatable defined/unresolved: Codec169/10, EM9305507/79, Touch215/0, CASE70/3, Boot908/3, Main1174/458. CASE selected graph still old command/format imports, whereas worker's independently composed graph now has zero imports; requested explicit integration rather than equating those scopes. Counts are selected graph symbols, not remaining native-body totals.

## Received packet burst and paired response

Native32f7f8..32f85c now full C: received-event packet burst using busy805848 and sequence805849, fixed259-byte allocation, byte-truncated loop count, native xbfu, native payload fill and busy clear. `link-packet-burst-round` target compile/link PASS. Native32fccc..32fd18 paired halfword response now C with exact byte-sized allocation length, first count byte, native read/store order and four-byte cursor advance; corrected callback declaration to its three-argument ABI. Unified `command-startup-font-clock-round` is running with explicit CASE combined startup and standalone experimental ELF artifacts. No execution or final product image claim.

Native32e428 response allocator and32fd18 link-test command processor now C: exact five-byte event header, handled command controls, generated packet call, response status, live word/halfword/byte counter load widths/order and native consumed/ignored return. Native303278/303284 now source-owned exact28-byte information copies from live RAM801518/8016c0 through selected memcpy. No snapshot data or unknown arithmetic substitution. The target build is running; execution equivalence is unqualified.

Link command response and information copies target compile/link PASS (`link-command-response-round`, `link-command-information-round`). Native32fe3c..32fea4 dynamic35-handler dispatch/fallback now C: old-address advancing handler table, first handled exit, type1 initialization and four-byte event, type0 one-byte event with native ST.AB advanced send address, unknown type0return. Corrected callback ABI and preserved initializer R0=1. `dynamic-handler-fallback-round` running. No current native execution proof; these are source reductions, not whole-image coverage.

Dynamic handler/fallback target compile/link PASS. Fresh all-six `command-startup-font-clock-round/receipt.json` passes all six selected candidate compilation gates, complete_source_payloads0. Snapshot defined/unresolved: Codec172/7, EM513/78, Touch215/0, selected CASE70/3 plus separately integrated zero-import standalone CASE ELF SHA7101280f..., Boot908/3, Main1194/466. Workers continued editing after snapshot; recorded hashes define evidence scope. Root local lexical census414definitions/108externswithoutlocalbody is not native coverage or final linker gate.

## Controller-associated record command closure

Native31b71c pending scan,31aa98 id lookup,31aad0 association lookup,31b248 free stream count,316a8c record allocator,331bf8 command status event,307664 full record configuration and30b0a4 validation envelope now C. Native3077b8 release-request/error and322f08 six-byte callback now C, and32fea4 command conversion owns only native consumed fields (padding remains untouched). Both `record-configure-round` and `record-command-closure-round` target compile/link PASS. The configuration callback322618 remains a genuine address-only native provider; source recovery does not establish execution or full product layout.

Native32ff20..3300c8 controller event encoder now C: four native encodings, exact feature gates, allocation truncation, native32-bit/halfword rereads, dynamic pair-count reread, special kind50 consumed failures and outstanding-counter publication. `controller-event-encoding-round` running. Whole source component completeness remains unproved.

Controller-event encoding and record callback closure target compile/link PASS. Native322618 now C with true index argument, association detach and lookup-pointer return. Root local lexical census427 definitions/106 remaining extern declarations without local body (see current JSON for exact count); no native-body coverage claim. The entire recovered206b/206c command/record path, including native information/status events, is now source-defined apart from product hardware/runtime qualification.
