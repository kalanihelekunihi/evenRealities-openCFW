# CapSense mode guards, CPU setup and initialization fields

Independent source in `../../components/touch/mode_offline/` reconstructs `0x6ac0`, `0x685c`, `0x6a80`, `0x6608` and the initialization fields at `0x4c84..0x4d8e`. Capture and regular-mode composition have separate validation reports. Native waits reuse sealed independent delay-cycle source, with calibration byte `0x20000870`. Physical timing remains unverified.

## Mode guards

Current mode is internal-context byte +85; repeat-scan enable is byte +115. Requesting the current mode returns success without clearing repeat-scan enable, including equal values 3, 4, 8 and 255. A different request clears repeat-scan enable first. Previous states 0, 1, 2, 5, 6 and 7 permit transition; other previous states return error 1.

Requests 0/1 install the state; 2 configures regular pins/base frame; 3 configures BIST pins; 5 configures saturation; 6 configures CPU operation; 7 invokes auto-dither preparation. Request 4 or values above 7 fail. Regular PDL configuration failure returns `0x40` and retains the previous mode, despite earlier pin/common-state changes.

## CPU and saturation setup

`0x685c` disables CTL bit 31 and the pump. If MRSS status at HW+`0x180`, bit 0, is clear, it writes MRSS command 1 and waits up to 315 iterations. **The wait status is discarded.** It then enables CTL, disables processing and interrupt masks, acknowledges LP/active interrupts, sets internal operating mode +113 to zero, clears CTL bits 16/17 and sets scan-control bit 28.

`0x6a80` additionally clears global function 0 at HW+`0x400`, then sets three mode records at +`0x608`/+`0x60c`, stride 64, to `0x03000000`/`0x00101000`.

MRSS wait `0x6608` waits for a masked value to **change** from the comparison value. Targets 2/3 select IMO bit 24 and the target's low bit; other targets compare bit 0 directly. It returns 4 at budget exhaustion. Each wait step invokes delay argument 1 using the calibration byte; synthetic execution does not establish microseconds.

## Initialization and validation

Initialization enables all three widget contexts and adds maximum-count request bit 8 when column maximum is zero, bit 16 when row maximum is zero. It preserves existing request bits when maxima are nonzero.

Passed: 200 mode comparisons, 80 actual MRSS/delay comparisons and 9 initialization-slice comparisons. Regular/BIST/dither dependencies were explicitly stubbed in the mode-core tests. CPU/saturation paths have no function-entry stubs. Later composition reports remove regular and saturated helper cuts. Peripherals remain synthetic; no physical-time or IRQ-concurrency claim.
