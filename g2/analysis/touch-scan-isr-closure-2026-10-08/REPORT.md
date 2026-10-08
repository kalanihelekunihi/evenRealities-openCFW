# Scan ISR, FIFO transfer, continuation and actual project dispatch

Independent source: `g2/components/touch/scan_isr_offline/isr.c,h`. **1,636 original-instruction comparisons pass**:72 active transfers,864 low-power transfers,144 slot loaders,512 ISR paths,24 preparation/ISR compositions,12 dispatch-wrapper cases and8 actual project-entry calls using reset-copied pointers. No function-entry stubs. External callbacks are null or compiled synthetic ABI/order probes, not invented vendor callback implementations.

## Concrete entry and interface

Static startup0x38e0 passes the interrupt configuration at ROM0xb0f0 (IRQ8, priority3) and callback0x3949 to0xa2a8, then writes NVIC enable bit8 before calling the enable flow. Project wrapper0x3948 supplies hardware0x40290000 and global context0x200004ec to0x5c98. That wrapper supplies channel0 to0x5fba, which ignores the channel and invokes internal-context callback+16 with the context argument. The hardware argument to0x5c98 is unused; hardware comes from context->common->channel configuration. Neither dispatcher checks a null registered callback.

The locked reset-copied context contains common config0xb2a8, common runtime0x20000528, internal runtime0x20000c50, widget config0xb0f8, widget runtime0x20000548, active frame buffer0x20000aac, LP frame buffer0x200009fc, active slot descriptors0x20000818, LP descriptors0x20000808 and LP history pointer0x2000065e. These are observed pointer values, not a claim of full history-buffer capacity. Tests follow the reset tables exactly: copy0xc0 vector bytes toRAM0x20000400, copy0xf1 words fromROM0xb58c toRAM0x200004c0, and zero0x1ac words atRAM0x200008a8. Other guest SRAM begins synthetic-zero; state/IRQ/FIFO inputs are then supplied explicitly. They call the entry directly; NVIC delivery and the timing of enabling IRQ versus assigning the internal ISR remain unverified.

## ISR0x6780

Read INTR_LP(HW+0x120) and INTR_LP_MASK(+0x128). If their AND contains mask0x10000, take active-frame path; otherwise take the low-power path, including when an active-frame bit is masked. No additional pending-source guard is inferred.

Active path: acknowledge all LP interrupts; transfer completed slots; add numSlots(internalu16+70) to currentSlot(internalu16+52), truncating16 bits. If current<=endSlot(u16+54), clear AOS wake-timer low16, clear first-subframe flagbyte97 and load remaining slots. Otherwise disable CTL bit31, issue MRSS_STOP0x100, increment common active scan counteru16+4 with wrap, then clear busy and signal completion.

LP path: signal-detection bit0 sets common status mask0x400. When commonu16+22 contains mask1, transfer history and increment byte27 with wrap. Disable CTL, acknowledge LP interrupts, issue MRSS_STOP, clear busy and signal completion. If LP processing is disabled, no history transfer/counter increment occurs.

Completion0x614c clears common status masks0x01 then0x80 and calls EOS callback with **NULL**, if registered. The callback sees those flags cleared and the terminal block disabled. A continued active subframe does not call EOS.

## Active transfer0x6462

Active descriptors are(widgetId,sensorId), two16-bit values, stride4. Widget stride144; sensor context stride10. For enabled widgets(runtime status mask6==6), read FIFO+0x3200, store rawlow16, and set/clear sensor statusbyte6 mask4 from FIFO bit16. Disabled widgets neither read FIFO nor write sensor/frame results.

Frame stride28; word6 retains its upper coefficient byte. If internalbyte118 is nonzero, replace low24 with hardware sensor-data word3 from a44-byte-per-slot buffer beginning HW+0x2000; otherwise replace low24 with raw<<8. Both frame and hardware-buffer positions advance for disabled slots. Frame feedback is in-place; a later scan loader consumes it. This is reconstructed software state, not a validated analog filter response.

## Low-power history transfer0x6530

FIFO used count is low11 of HW+0x3410. HW+0x3414 bit31 selects commonbyte28=1(reset) versus3(reset|valid). Store first slotbyte24, countbyte25 and `(used/count)` truncated to8 bits in byte26. The function requires nonzero count in the supported test contract; no extra software buffer-bound check exists here.

For each complete cycle and slot, consume FIFOlow16 even for disabled widgets. Every consumed slot advances the history pointer by2 bytes. Enabled methods2/10 store maxRaw-raw when raw<maxRaw, otherwise0; method1 stores raw directly. Disabled slots leave their positions unwritten. **The history is positional, not compacted by enabled widgets.** Sparse-mask tests specifically cover disabled positions before enabled ones; they corrected an initial reconstruction mistake that contiguous enabled masks had missed. Quotient256 truncates to0, producing no transfer; this is tested machine behavior, not a recommended history size.

Apps/CFW consumers must interpret byte26/25 counts, slot descriptors, baseline-validity flags and enabled masks together. Do not parse disabled positions as fresh samples, assume raw CSX/ISX polarity, or infer history allocation from the FIFO's nominal capacity. Actual generated history capacity remains unproven.

## Slot loader0x664c and callbacks

Stores min(requestedCount,21) into internalnumSlots; count0 returns without MMIO or callbacks. For nonzero count it disables CTL, chooses MRSS operation from status bit24, and may wait441 iterations with target2. **The wait return is discarded**, including the tested static-status timeout.

Each loaded slot becomes eleven hardware words: coefficient low4, two zero words, feedback low24, another zero word and six scan words. Mark final scan control mask4, clear selected initialization/offset bits, and set hardware scan offset256-numSlots. First-subframe flag97==1 permits SS callback with **active-scan-context pointer**, notNULL. The flag is reread after the callback; the compiled probe can clear it and suppress the follow-up MRSS status action. It then enables CTL and issues FRAME_CMD1. The locked project generates five active slots; capacity21 tests use a separate21-frame synthetic allocation and do not imply21 configured project slots.

## Preparation composition and source attribution

The additive offline binding calls closed preparation then replaces stock ISR metadata with the native ISR address. Comparisons normalize only this logical entry-address field; all other state/MMIO stays exact. This tests source composition, not firmware byte equality or a production pointer patch. Dispatcher tests confirm channel/hardware arguments do not affect the selected stored ISR.

Verbatim public Cy_CapSense_ClrBusyFlags from pinned CapSense247a9a0f79eb976f144f5fbeb29488c1c2606517 compiles to the exact36-byte stock body at0x614c with Arm GNU13.3 -Og and -O1, no relocations, one full-byte match in the locked image. Translation-unit type offsets/macros are explicitly synthesized and statically asserted; this is a selected public body, not a full SDK build. Combined with prior208 PDL and42 clock-helper bytes, demonstrated distinct compiled-source attribution is286 bytes. No unique producer/compiler identification or complete-image equality follows.

## Boundaries and next source leads

Synthetic FIFO/MMIO/factory trim, direct function calls and compiled probe callbacks do not prove physical interrupt delivery, analog response, FIFO peripheral side effects, elapsed timing, or interrupt reentrancy. Coherent stable pointers and allocated buffers are required. Initialization source already clears SS/EOS callbacks by default; these tests exercise optional callback interfaces, not a claim that stock initialization installs unknown bodies. User callback bodies if registered, actual LP-history capacity and real interrupt scheduling remain separate unknowns.

Next actionable software lead is the LP history consumer/processing path that interprets commonbyte28 reset/valid bits and histories from0x2000065e; it can be investigated from the existing firmware and pinned LP-processing source. Source inference is not exhausted. Historical symbol labels can disagree with these addresses, so the evidence here is the locked bytes and executed call chain. No shared symbol/campaign file was changed.
