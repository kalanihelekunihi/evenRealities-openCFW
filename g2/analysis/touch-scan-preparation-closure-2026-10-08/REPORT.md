# Stock scan preparation, dither-scale measurement and error flow

Independent source: `g2/components/touch/scan_preparation_offline/prepare.c`, composed with closed clock/base/all-slot/mode/GPIO/scan/watchdog/max-raw source and public pinned PDL. **348 fresh comparisons pass**:96 preparation-field slices,96 dither-scale calls,96 full preparation calls,28 threshold cases,24 measurement-loop cases and8 callback ABI/order probes. No function-entry stubs or retained executable dependency on the independent side. Synthetic completion/FIFO and factory trims limit hardware conclusions.

## Actual preparation call chain0x71c8

1. InitializeSourceSenseClk0x6384, save its status.
2. Clear current sense method (active contextbyte21) and scanSingleSlot(internal82). Copy inactive CSD/CSX/ISX states from common41/42/43 to internal116/117/76.
3. GenerateBaseConfig0x5378 and OR its return; generate active and low-power slot arrays **regardless of clock status**.
4. Store stock ISR callback address0x6781 at internalu32+16 and wake timer count at internalu32+40 using0x5d70, inputinternalu32+36. Address storage is reconstructed metadata; ISR body is not implemented by this module.
5. Invoke nonnull end-of-init callback at internal+20, passing context. It has no returned-status contract. A compiled synthetic void-callback changes prepared data and leavesR0=0xdeadbeef; traced original/native calls both ignore that residue. This validates ABI/order only, not an unknown vendor/user callback body.
6. Only while status remains0, switch mode1 then mode2, then calculate dither scale0x7064.
7. For each of three enabled widgets, run maximum-raw initialization0x5cac **even after prior error**, ORing its status.

An earlier clock failure therefore does not suppress frame mutation, callback invocation or requested maximum measurement. PDL configuration or subsequent modes can alter state before returning errors. No rollback is inferred.

## Dither scale0x7064 and measurement0x69c4

The dither-scale function requests mode7 and retains its status, but does not skip its widget loop on failure. Enabled means contiguous runtime statusbyte35 contains both bits2/4 (mask6==6). A widget is sampled only if configbyte138==2 and methodbyte122!=10. Regular scan words come from activeframe+firstslot128*28; widgettype7 selects LPframe+firstslot124*44+20. Dither measurement accepts strides7/11 words, copies six scan words, overrides scan control to0x00ff0063, CDAC to0x00400064 and clock control to `(old & 0xc000ffca) | 0x00ff0004`.

For each declared sensoru16config+56 it starts a frame and polls with argument1753. Successful polls read FIFOlow16 and retain the maximum; exhausted polls set error4 and do not read FIFO. Iteration continues. The argument is a software watchdog input, not an observed1753-microsecond duration. Completion state and FIFO samples are synthetic.

The maximum selects runtimebyte51 (dither scale index):<=32->6,33..55->5,56..111->4,112..337->3,338..563->2,564..1127->1,>=1128->0. Even timeout/error with no samples selects6 from maximum0. It then regenerates both slot arrays and calls public PDL Configure. Final PDL failure returns0x40, replacing accumulated earlier statuses; success returns the accumulated status. Dither timeout therefore does not roll back scale/frame changes.

## Scope and practical implications

Full tests use coherent synthetic widgettypes2/6, saturated-scan mode0, null callback except the documented compiled probe, syntheticGPIO/MSCLP/SFLASH and controlled completion. Dedicated measurement tests cover0/1/2 sensors and active/LP strides. Maximum-raw saturation still excludes widgettype7's alternate ABI. Existing field-slice tests stop original execution at0x7228 and compare liveR6 status; they are not mislabeled full calls. Original and independent bus order, state, frames, maximum and returns match.

For CFW diagnostics, record mode, mutated frames, dither scales and request flags alongside returned status: errors do not imply that setup or sampling was skipped. Software success and installed mode remain separate from physical scan correctness. These sources are offline reconstructions, not a firmware patch.

The pinned Infineon semantic source matches the previously cached6.10 release byte-for-byte (sdk-source-receipt.json). The existing3.0.1 CapSense gitlink remains unchanged; the earlier separate6.10 reference proposal still applies. Public PDL35f171... Configure is behaviorally validated, with its recorded24-byte loop-layout mismatch. Exact compiler/generatedcycfg and complete image-source equality remain unproven.

## Remaining actionable leads

The stored ISR0x6780 calls FIFO/context extraction0x6462, result processing0x6530, scan continuation0x664c and completion0x614c. They are readable software leads, not blocked by missing hardware inputs. The type7 saturated-scan branch and unknown external callback bodies are additional boundaries. Hardware evidence or a validated peripheral model is needed to establish actual analog response, factory trim/timing and interrupt interleavings. SDK/source inference is therefore not exhausted.
