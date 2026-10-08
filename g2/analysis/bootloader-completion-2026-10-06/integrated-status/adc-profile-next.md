Superseded by [native profile/apply and650 original/source comparisons](adc-profile/REPORT.md), with all seven cases PASS on checkpointff5313. Required user15 power/clock children reused natively; original static note follows.

# Next retained ADC profile/power boundary

Locked original SHA f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5. Next unclosed startup cuts: profile-transfer42f020..42f14e(302 instruction bytes) and apply-profile42ea68..42eaf6(142 bytes). Static disassembly establishes this bounded dependency scope; no reconstruction or dynamic completion claim yet.

Transfer truncates operation and save/restore argument to8 bits. Operation0 optionally restores a previously saved context image: if restore requested but saved-validbyte context+0xc is0, returns7 before power action. It calls power-mode enter41bf84(user15), and when restoring calls clock_request4222f0(4,15); a clock request error returns immediately without invented rollback. It restores eight slot words from context+14..30, timer/window/interrupt words+34..40, config+10 (ADC-enablebit0 programmed last in two writes), then clears saved-validbyte.

Operations1/2 share a branch: optional snapshot copies the same registers into context+10..40 and sets saved-validbyte1, then **always** calls clock_release422364(4,15) and power-mode leave41c17a(user15), ignoring their status. Stock caller currently uses operation0,arg0 before configuring, and operation2,arg0 after deactivation/reset preparation. Unsupported operation returns6; invalid context2. Reads context+4 before null/magic check, consistent with other raw ADC entries.

Apply-profile accepts only first clock-selection byte2 or returns6, requests clock(4,15) and propagates failure before config write. It packs the7-byte profile fields into ADC CFG40038000, forcing bit12 while clearing bit0. Stock profile02010007010001 is available as authenticated original/static data. Reused clock dispatcher/class4 already has native source; required power-mode enter41bf84/leave41c17a must be traced/reused or reconstructed explicitly. Do not retain success stubs or claim lifecycle power closure by closing only these two ADC wrappers.

Next source batch should cover these two ADC providers and the bootloader-reachable power-mode children, with tests for save/restore/cached flag, register order, low8 truncation, clock request errors and absence of implicit rollback/drain. Factory/ROM/peripheral/IRQ/task models remain explicit. No hardware/power shutdown or source-complete firmware conclusion follows from this static note.
