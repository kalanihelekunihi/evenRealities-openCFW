# EasyLogger setter reconstruction

Verified candidate SHA256 `9affaa59fb648834327b08181849cc02787cacc3044c90e86692790e10a1bac6`; all seven exact-image cases PASS (normal2, malformed3, interruption/reboot2). Prior `ca59e916...` remains preserved.
Locked bootloader SHA256 `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`, load `00410000`.

Source: `g2/components/bootloader/initializer_callbacks/elog_setters.c/h`; runner `verify_elog_setters.py`. Reconstructed stock C, not imported EasyLogger upstream. No unverified upstream version/config/license assumption.

| Stock address | ABI / behavior | destination |
|---|---|---|
|4173ca..417438|output enabled; low-byte 0/1 validation|200267f1 byte|
|417438..4174a6|text color enabled; low-byte 0/1 validation|200267f5 byte|
|4174a6..417510|format for low-byte level, nominal 0..5|200267d8 +4*level word|
|417510..417570|filter low-byte level, nominal 0..5|20026700 byte|

All validate only the low byte. 256/257 become 0/1; callback-return assertions still perform the invalid store. In particular format level255 writes outside the logger structure. The C intentionally retains this stock behavior; it is not an app-facing validated API.

Assertion callback word `200270e4`, ABI `(condition,function,line)`; lines278/290/321/347. Null callback calls output4176ce with severity0, tag`elog`, authenticated source-path string, original format and duplicated condition/function/line variadic fields, then requests architectural reset through41ac8a→41a700. Source reproduces DSB/AIRCR write `(old & 0x700)|0x05fa0004` and spin. No firmware/device reset performed.

192 original-instruction/source cases PASS, comparing all1280 bytes of logger/sentinel SRAM plus callback/logger arguments and AIRCR write. Setter instruction bytes visited:108+108+104+94=414/422. The remaining eight bytes are four reset-retry branches (41741a/417488/4174ec/417554); they are not reached because the test stops at the first AIRCR reset-request write. 425 source Thumb mappings PASS.

Logging4176ce is an injected sink in this focused suite. Callback is injected and returns; reset test stops at AIRCR write. Original setter bytes are verified against locked image in receipt. Source machine has ELF executable segments only. No actual callback execution, formatter correctness, physical reset, task scheduling or firmware source completeness claim.

Affected native comparisons on this same candidate: mutex516, persistent sequences2, block-boundary4, ISR1480, public ISR62, deferred FIFO1, service records112 PASS. See per-suite JSON. Seven-case integration and post-run628-input/158-object integrity PASS; see `../same-image-validation-9affaa.json`.

Borrowed ISR event pointer ownership is unchanged: copied queue records do not retain pointed objects, and queue reset discards callbacks without object release. No new drain/delete guarantee.

## Concrete next boundaries

Logger4176ce uses shared1024-byte buffer200258d0, output/filter/tag formatting and IAR formatter41e47a via41b218/41b25c. Plain console415fae is a separate formatter415bf6 and callback200270cc, static output20024cd0. These are not interchangeable sinks and remain unresolved source boundaries.

Thread API416200 is termination, not generic startup: context guard→-6, null→-4, state4→-3, otherwise delete417f0a→0. Native deletion removes intrusive state/event items; current-task deletion defers cleanup, other-task deletion invokes418ae8. Scheduler execution/deferred reclamation still require further recovery.

Startup41fa50 calls conditional41fa98,41c4b4,41c86c(0,0),41ca2c(stack,25.0f), copies20-byte record433a9c, calls422416, then4222a0(4,0,0) and(5,0,0), ignoring statuses. Conditional41fa98 runs only when byte20027198==1; nonzero423d20 or423dd0 spins before flag clear, otherwise41583c(0),41d92c(0x1c,word434154), flag=0. These are statically traced, not newly validated source.

Correction to older record prose: each33-byte tag record has level at+31h, tag bytes+32h..50h, and active flag at+51h. The tag lookup41760a checks active flag==1 and compares30 bytes. Record reset C already clears these bytes correctly; +51h is not merely a string terminator.

## Recovered logger transport behavior (static instructions)

4176ce→41a692→41b854→41f918 selects UART row1 (`41b85a movs r0,#1`); severity is discarded by41b854. 41f918 initializes a56-byte stack descriptor, stores borrowed output pointer and length at+0/+4, zeroes fields+c/+10/+34, clears row completion byte+19, and submits through4233e8 using handle at row+4. Rows are28 bytes, selected low byte must be<4 and initialized byte+18 must equal1. Submission status is saved; wrapper then polls completion byte at most1000 iterations with41f9e6(10) between polls. Return is1 iff submission status nonzero, otherwise0, **even when polling exhausts without completion**. Delay argument units are not established here.41b854/41a692 ignore this result; logger unlock follows. No proof that async hardware has stopped reading shared200258d0 buffer at unlock. This is an ownership boundary for further source recovery, not a demonstrated hardware failure.

```c
// Behavioral pseudocode of41f918; child submit/delay and callback are unresolved.
int uart_log_send(uint32_t row, const void *borrowed, uint32_t length) {
    struct descriptor56 desc = {0};
    row = (uint8_t)row;
    if (row >= 4 || uart_rows[row].initialized != 1) return 1;
    desc.buffer = borrowed; desc.length = length;
    uart_rows[row].completion = 0;
    int status = uart_submit_4233e8(uart_rows[row].handle, &desc);
    for (unsigned i = 0; i < 1000 && uart_rows[row].completion != 1; ++i)
        delay_41f9e6(10);
    return status != 0;
}
// Not evidence of buffer release, physical TX completion, or safe unlock.
```

No commits/staging, device writes/flashing, IAR authentication, or campaign state/gate edits. All offline heavy jobs for this batch have completed. Logging output and startup source recovery are further recoverable work, not claimed external-input blockers.
