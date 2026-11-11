# Stock Goodix upload hook in C

Normal composition now owns `Gh2x2xUploadDataToMaster` in
`application/goodix/stock_upload.c`. This is the stock disabled hook at
`0x2d66c`, not a replacement upload protocol. Its complete compiled body
matches stock's two-byte return instruction. The typed signature uses the
pinned public `STGh3x2xFrameInfo`, `GU16` and `GU8` declarations.

Identity is supported by the matched `GH3x2xGetFrameDataAndProcess` caller,
not the non-unique return instruction alone. At `0x2c5c2`, that function
calls `GH3x2xHandleFrameData`. At `0x2c5ce` it calls the upload hook with the
frame pointer, frame count, frame number and tag-array pointer. It then
increments the frame counter and copies the low four bits of each channel's
AGC value into the last-gain array. That sequence and argument roles match
the pinned driver's non-ZIP upload branch. The pinned `gh_uprotocol.c`
disabled-upload definition ignores exactly those four inputs.

REA byte windows authenticate the hook and call-site fragment against the
locked application. 512 paired direct executions verify register/mask/flag
preservation and no data accesses, including null and invalid pointers.
Another 90 paired executions run the actual stock fragment through the
hook and count/gain continuation, once with stock and once redirected to C.
They cover zero through 32 channels, zero/one/maximum frame counts and
numbers, and counter wraparound. Frame processing is modeled at its entry.
Two compiled defects that access tag/frame memory fail behavioral assertions.

All 802 R1 units compile with no failures or duplicate strong symbols.
Application imports decrease from 92 to 91, with no new imports. All 799
other prior object hashes are unchanged; the two generated boot objects
retain source hashes, allocated bytes and relocation identities. The only
manifest change is the new unit. Strict GNU bootloader linking and R1 source
checks pass. The global check retains the unrelated unlisted G2
`resident_rom_thumb_set.S` failure. No source-plan selection changes.

This closes the existing hardware-frame dependency without implementing the
PC-tool transport. Physical sampling, timing, full frame-dispatch execution
and complete application final linking remain unverified. The
[machine-readable receipt](goodix-upload-c-review.json) records exact source,
upstream, REA, build and probe hashes.
