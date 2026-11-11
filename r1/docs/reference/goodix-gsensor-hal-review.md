# Goodix public accelerometer HAL bound to stock C consumer

The normal source build now routes `hal_gsensor_drv_get_fifo_data` through the
checked `r1_goodix_gsensor_sample` consumer. Application imports fall from 199
to 197: `gh3026_gsensor_data_get` and `GH3X2X_TimestampSyncFillAccSyncBuffer`
are resolved without new imports. Stock `0x6f920` calls the confirmed BX-LR sink
at `0x2adfc`; the SDK algorithm synchronization entry was not a stock-equivalent
provider for that call. This binding uses the evidenced no-op rather than
inventing algorithm behavior.

`stock_gsensor_hal.c` uses the SDK's actual anonymous sample struct and public
prototype. Static assertions verify its six-byte extent, signed halfword axes,
X/Y/Z offsets 0/2/4 and two-byte count word. It casts the sample storage for the
underlying hardware consumer. The kernel configuration header is pinned before
the SDK inner header, matching the generated demo unit's configuration choice.
The hardware consumer itself remains independent of SDK headers.

The public adapter is an ordinary typed C call. Clang rejects `musttail` between
the distinct struct-pointer and halfword-pointer signatures, so no forced-tail
attribute is used. The compiled artifact is explicitly checked to contain a
four-byte direct B.W to the consumer, with no added frame. Compiler or flag
changes require this check again. The public entry is an adapter to the single
hardware implementation, not a second sample-processing body.

`sources.json` removes exactly the superseded SDK sample HAL definition from
`gh_demo_user_r1.c`; pinned upstream files are unmodified. All 24 other nonempty
executable sections of that generated demo object remain byte-for-byte equal
to the preceding build. Consumer and sink object hashes are also unchanged,
retaining their registration/stop regressions and count-snapshot negative control.

The public HAL passes 448 paired stock comparisons (896 executions), including
live callback count changes, signed axes, Z/Y/X access order, callback R0/R1,
return/nonreturn and preserved ABI state. The adapter is exercised in the linked
probe, with actual C consumer and sink bodies. Board callback behavior and
optional sink mutations are controlled probe boundaries.

`build/sources-goal-r1-goodix-gsensor-hal-final/report.json` compiles all 568 R1
units without failures or duplicate strong symbols; application imports are
197 and bootloader imports remain 34. `make sources-check` and diff whitespace
checks pass. [Machine evidence](goodix-gsensor-hal-review.json) binds the build,
generated source, section/import audit, public probe and adapter disassembly.
Earlier failed build attempts remain under ignored build directories; only the
final report represents this validated manifest.

The canonical source plan and G2 gates are unchanged. This is source integration,
not byte qualification. Private frames/caller-clobbered flags, arbitrary aliases
or target faults, concrete callback identities, startup placement, concurrency,
physical accelerometer behavior and complete source-only byte identity remain
unverified. Existing mixed-enum link warnings remain visible; this adapter uses
only pointers and fixed-width words across its boundary.
