# Board pin initializer candidate

The routine at package 0xfe2c..0xfe94 / runtime 0x102068a0 is reconstructed in
runtime_gx8002_board_pin_initialize.c. The native macOS C-SKY build emits 104
bytes, fitting the original slot. It is unregistered and not behavior-qualified.

It calls padmux_init with the 13-entry table at 0x1020ad30, then reads each
pin/function pair and calls padmux_check. A nonzero check prints the pin error
at 0x1020ad97 and does not abort iteration. When function equals zero for pin 2
or one for other pins, it calls gpio_set_direction(pin,0). After all entries,
it invokes board_pin_setup and writes one to 0x20027b4c only if that call returns.
The C preserves the table reads and cached per-entry values across helper calls.

Next work: authenticate the SDK header used in this builder, qualify decoded
stock/source call and data traces including setup nonreturn, compose the source
table and actual helpers, and reconstruct the per-pin error diagnostic. Build
fit alone does not establish board or hardware completion.

Initializer builder now authenticates gx_padmux.h and gx_gpio.h against
NationalChip commit 8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5, recording Git
blob and SHA-256 identities. The C GPIO prototype now matches the recovered
implementation and upstream GX_GPIO_DIRECTION enum; direction zero is named
GX_GPIO_DIRECTION_INPUT. Native compilation remains 104 bytes with unchanged
code SHA-256 55cfa58578b79d4a14bb295ac596892a8a9cd304edbbc7d5d9060578f5f36753.
Decoded qualification remains next. Integration 58083 was confirmed live;
the full source-only goal remains active.

Initializer decoded comparison passes 240 cases and three tests on macOS,
covering table variations, error-bit branches and setup return/nonreturn.
The initialized flag is absent from nonreturn traces. Helpers and nonreturn
are modeled at call boundaries; actual helper composition remains pending.
Integration 58083 was confirmed live; full source-only goal remains active.

Initializer now consumes the decoded setup terminal path in 2,048
stock/source combinations across all 256 guard failure masks and diagnostic
branches. Setup self-loop prevents the initialized flag write. Four initializer
tests pass, including a hook overriding an assumed return. Lower helpers remain
modeled in this composition and frames are separate. Integration 58083 was
confirmed live; complete source-only firmware remains the active goal.

Initializer source-table composition passes 60 cases with exact compiled-data
read order. Initializer/GPIO composition passes 24 stock/source combinations
with shared register words and 52 ordered accesses per case, preserving
unrelated bits and setting input policy for pins 0..12. Other helpers remain
modeled in these finite compositions; initializer remains unregistered.
Full source-only firmware goal stays active.

Initializer per-pin diagnostic now passes 144 decoded formatter/output
combinations through scripted UART transmission. Initializer/printf forwarding
passes 180 cases across per-entry error masks and return values; processing
continues after diagnostics. Seven initializer/data tests pass on macOS.
Other initializer helpers and physical hardware remain unqualified in this
composition; aggregate admission is pending and full goal remains active.

Initializer pin checks now execute decoded checker/getter bodies in 32
stock/source combinations. Diagnostic decisions follow decoded register
readback; ordered reads cover all 13 pins. Eight initializer/data tests pass,
including hook-driven diagnostic selection. Post-init padmux words and other
helpers remain modeled; padmux initialization composition remains next.
The full source-only goal stays active.

Board/padmux initialization composition passes 24 decoded combinations.
The 13-entry override table feeds all 32 default-pin setter calls, with
non-board pins defaulting to function zero. Nine initializer/data tests pass,
including initialization argument forwarding and ignored helper error. Setter
bodies remain modeled in this particular composition; other reviewed helper
proofs remain separate. Full source-only admission/firmware remains pending.

Board/padmux initialization now includes decoded setter bodies and shared
register words in 96 combinations. All 32 writes are checked and final words
match the board/default policy from both zero/all-one initial states. Setter
checker and other board helpers remain modeled in this composition; decoded
checker composition is independently established. Full goal remains active.
