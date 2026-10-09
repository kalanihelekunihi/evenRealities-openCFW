# UART TX ownership and stock configuration

**The stock logger uses UART1 with no software TX queue. Its blocking HAL path consumes caller bytes into the hardware FIFO before successful return; that does not establish that bytes have left the pin.** The asynchronous HAL path separately retains the source pointer while unconsumed bytes remain. A TX-consumed callback, the wrapper's completion flag, and physical output are distinct.

## Exact source and validation

[Eleven selected pinned SDK bodies](../../components/audio/uart_tx_offline/README.md) retain unchanged function text and BSD3 notices: initialize/buffer configuration, transaction save, blocking/nonblocking TX, TX state machine, FIFO write, queue drain/init/add/get. A sparse stock ABI adapter binds56byte transfer,284byte handle,24byte queue and one-byte enum fields. Source-family revision text release_sdk5p1p0-366b80e084 and exact body/file hashes are recorded in [source-reference.json](source-reference.json). Matching these bodies does not prove the producing compiler/SDK version or whole-driver equality.

**650 direct comparisons PASS** against the final [receipt-bound ELF](reproduction-receipt.json), plus6 logger-to-HAL compositions,4 interrupt-marker compositions,3 controlled lifetime compositions,1 actual initialized-channel composition, and1 whole initialized-SRAM decode check. Total665 author-validated cases, with664 involving the native TX ELF and the decoder case testing original instructions separately. Counts are not unique-function/byte coverage or independent review.

Native reached code is guarded in direct/lifetime and sink-composition tests. The only original executable alias in this ELF is delay0x4807A0; tests explicitly synthesize its returns/readiness changes. FIFO readiness, callback invocation and interrupt-status fixtures are synthetic. Initialization composition additionally stubs GPIO/power/configure/NVIC/IRQ enable; it verifies default state/arguments, not hardware setup. No physical UART, DMA path, delivered exception, concurrency, full scheduler or device trace is established.

The full initialized SRAM record matches136529 unchanged instruction steps of original decoder0x43A11E:10864compressed bytes→17752 initialized bytes, decodedSHA256df1a1fdf7b2792a7c4ef7a2c5cc6d1423bc7833b556fdfcedb8d6d927fbbb743. Whole reset/scatter remains outside scope. Logger compositions likewise use unchanged instruction steps because continuous Unicorn's ThumbIT execution in the memzero tail0x4D555C was inconclusive; no opcodes or flags substituted. Raw payload identity remains19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701 at0x438000, wrapped36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863.

## What changed in understanding

- The actual initialized channel1 descriptor selects module1, pin table0x786060 and configuration0x20000CCC. TX queue fields are0/0. Original init composition confirms both queue enable flags stay0 for this channel. Channel3 differs:1024byteTX queue at0x200BA420. Do not generalize logger configuration to all UART consumers.
- The channel1 config encodes921600baud and8N1 according to the pinned enum definitions; clock enum0/HFRC and threshold enums2/2. This is requested configuration, not measured bitrate. Logical TX/RX indexes12/14 have raw config5; physical pad behavior unverified.
- Transaction-save copies the pointer and metadata, not payload. Queue-add copies payload synchronously; FIFO-write reads caller bytes synchronously. Partial nonblocking return retains a borrow on the remaining bytes. Three deliberate mutation tests make that boundary concrete.
- Blocking success clears writing after all requested bytes were consumed. Copied bytes can still occupy software/hardware queues. In the default logger branch, no software queue is present; hardware acceptance still differs from transmission complete.
- Timeout0 does not mean immediate timeout in this stock body: after each service/delay, the incremented uint32 counter is compared for equality. Tests cut a stalled zero/forever case after five synthetic delays; no infinite-progress/hardware claim. Positive timeouts can return4 after partial consumption and clearwriting. Transaction metadata/pointer remain stale after completion but the active flag controls subsequent reading.
- Six complete logger compositions return0 after consuming0/3/205byte payloads even when channel completion remains0 through all1000wrapper delays. With a deliberately injected marker after firstdelay, only1wait occurs. A successful wrapper return alone does not confirm its marker or physical output.
- Four manually entered original interrupt wrappers show statusbit0 sets both HAL lastTXcomplete and channel completion; bit5 services inactive TX without setting them. Status/clear/service instructions execute original bytes, but no actual IRQ delivery is simulated.
- Original initialization wrapper configures eligible channels, then shuts them down. Static caller0x5093AC subsequently enables channel1 via0x55E5BC. Peripheral configure/power/NVIC have remaining source leads; the default structural state is verified, not physical activation.

[Lifetime table and pseudocode](pseudocode.md), [direct cases](results.json), [sink compositions](sink-composition-results.json), [mutation ownership tests](lifetime-results.json), [IRQ marker tests](irq-composition-results.json), [SRAM initializer](initializer-results.json), [driver initializer composition](driver-init-results.json).

## Remaining useful leads

The selected synchronous-copy/borrow boundary is now source-backed through its tested providers. Shared formatter buffer reentrancy and preemption between formatting and HAL submission remain unproven; no patch-safety or live race claim. Actual IRQ/vector routing and RX callback/stream ownership, UART configure0x58E09E, power0x58DBB8 and DMA paths remain actionable pinned-source leads. UART channel3's enabled queue makes it a separate useful app-facing target. No external input is yet required to investigate these static source paths, and whole-project source searches are not exhausted.

No prior source/seal was edited, no staging/commits/campaign gates changed, and no device writes performed. [Preservation evidence](preservation.json).
