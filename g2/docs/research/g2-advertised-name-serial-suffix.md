# G2 advertised-name serial-suffix patch

## Result

The Apollo-main CFW overlay rewrites only the final six characters of the
stock 19-byte G2 local name at the stock builder's final suffix copy. For
example, a paired serial of
`S211GCBC300403` produces:

- `Even G2_32_L_300403`
- `Even G2_32_R_300403`

The local-name AD element type, length, model/revision text, lens side, and
all other advertising elements remain unchanged. The hook writes only the
existing six-byte destination after first preserving the stock copy.

## Stock evidence and cold-start-safe hook boundary

The reviewed `g2-2.2.6.10` Apollo image builds manufacturer data from the pair
serial at `0x0046DD78`, then copies the six-character BLE-address tail into the
local name at `0x0046DDA8`. The original instruction bytes at that final copy
are `cb f7 1c ff`, a Thumb `BL` to the public memcpy entry at `0x00439BE4`.
The overlay replaces only that final call with a `BL` to
`open_cfw_copy_advertised_name_pair_suffix`.

The hook ABI remains the memcpy call ABI:

```c
void copy_suffix(uint8_t *destination,
                 const uint8_t *stock_mac_suffix,
                 unsigned int length);
```

The hook first performs the stock copy unconditionally. It then reads the same
initialized serial-record pointer that the immediately preceding stock
PSN-to-manufacturer-data call uses, skips the record's leading version byte,
and replaces the copied tail only when all 14 serial characters and the NUL
terminator validate. Live advertising captures show the same pair serial on
both temples, while the stock final six local-name characters differ because
they are derived from each temple's BLE address.

The previous Cordio-boundary implementation scanned already-installed
advertising slots while the local-name payload was being submitted. On cold
startup the serial slot was not necessarily available yet, so it forwarded the
MAC-suffixed name; pairing rebuilt advertising after the serial became visible
and made the name appear to change. An earlier direct PSN hook has the opposite
ordering problem: stock firmware copies the MAC suffix after that hook returns.
Interposing on the final copy removes both ordering dependencies.

## Fail-open policy

The stock call and original payload are preserved when any of these conditions
holds:

- the copy length is not exactly six bytes;
- the destination is null;
- the initialized serial-record pointer is null;
- any of the 14 serial characters is not alphanumeric;
- the serial is not NUL-terminated after 14 characters.

The leaf has no relocations and no writable global state. It remains an
independently compiled overlay leaf; the reviewed Apple Clang placement and
the following placement-sensitive leaves are repinned in `overlay.json`.

## Verification

`tests/test_ble_advertised_name.py` compiles the target source into a host
harness and verifies cold-start rewriting at the final copy, left/right
convergence, exact stock fallback, malformed serial behavior, non-suffix copy
preservation, the stock callsite bytes, and the public memcpy/serial-record
bindings.
