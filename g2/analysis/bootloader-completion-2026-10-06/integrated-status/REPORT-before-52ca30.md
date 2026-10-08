# Bootloader source integration status

Latest verified image: **19ff0c9366ae316f2671dfd13462c1383ca37696734f2da68427d7c75185afb8**. All seven cases PASS: normal2, malformed3, interruption/reboot2. Recorded573 input files and142 linked objects remain unchanged. [Same-image evidence](same-image-validation-19ff0c.json).

The seven-case deduplicated original instruction-byte numerator is **35,392 /148,599 =23.81712%**. This is observed modeled execution, not source-completeness percentage. Six FP64 effects remain emulated. The partial source ownership ledger maps13 IOM functions/2242 original body bytes; compiled ELF sizes are a separate inventory.

## Newly closed paths

Native configuration42cc34, enable42c538, retry43048e, interface selection42c034, clock helpers42c222/42c256/42c26a and CQ initialize/enable/disable42c3e2/42c420/42c44e now join native claim42c4c6, transaction42c988 and interrupt42c63a. Readable implementations are in `initializer_callbacks/context_{claim,transaction,instance,clock,queue,retry}.c` and `context_claim.h`. Generic queue flag stores were corrected to preserve their original separate write sequence.

740 child-function comparisons,496 claim/transaction comparisons and52 interrupt comparisons PASS on this image. Two additional stable-subtype comparisons PASS with explicitly conditional MMIO behavior. [Source ownership](iom-source-ownership-19ff0c.json); [linked inventory](implementation-inventory-19ff0c.json). Numeric bindings decreased73→67; this is linkage accounting, not completion.

Configuration supports I2C100k/400k/1MHz and SPI clock/mode fields. Shared startup uses modules2/5/7 at400k without CQ and module4 at1MHz with2048-word/8192-byte CQ. Native startup calls configuration/enable/retry four times, but does not reach CQ enable/disable or SPI clock helpers; direct tests cover those paths. Retry allows1000 attempts and delays after every failed attempt, including the final one. Delay argument10 has no established time unit here.

Failed enable can leave generic CQ claimed. Under explicitly preserved subtype bits, repeated initialization returns busy7 and clears the IOM CQ-handle slot; plain-RAM I2C modeling returns9 earlier because subtype bits are overwritten. Neither test establishes silicon behavior or authorizes speculative cleanup. Powerdown retains IOM claim; no release/uninitialize implementation has been invented.

## Native NVIC provider

Wrapper430470..43048e now executes original/source instructions in shared startup and issues the matching ordered register write for IRQ10. [Readable behavior](context-nvic-REPORT.md), [30-byte ownership](context-nvic-ownership-19ff0c.json) and [196608 direct comparisons](context-nvic-19ff0c.json). The guard checks signed low16 bits only; positive invalid IRQ numbers are not hardware-safe just because the wrapper accepts them. Tests compare issued stores, not physical NVIC W1S behavior or interrupt delivery.740 IOM child and2 conditional cleanup comparisons also PASS on this new image. Alignment347 mappings PASS; known bad image rejected. Prior496 claim and52 IRQ receipts remain explicitly bound to d98328, not relabeled to this image.

## Still open

Semaphore creation416762, descriptor registration430280 and ADC/service children remain boundaries. Asynchronous IOM service42c6f8 and descriptor publication42c45a are not closed by CQ lifecycle tests. Whole-system scheduling, cancellation/resource release, startup alternatives, lower mutex/kernel and logger/fatal paths remain incomplete. [Provider checklist](remaining-providers-dceae3-worklist.md).

MMIO, scheduler/IRQ, ADC and resident-ROM storage remain synthetic. Atomic interruption/reboot tests do not prove physical partial writes, hardware recovery or application execution. The relocated image links prepared objects; it is not a clean whole-payload build, source-complete firmware or byte-identical artifact. Earlier checkpoints and [prior report](REPORT-before-d98328.md) remain preserved. No commits, flashes or IAR authentication occurred.
