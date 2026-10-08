# Independent review — P2-21459

Status: partial; accepted: false.

Fresh replay/extraction passed against the locked input SHA-256 `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`. The exact 88-byte interval 0x4849A4..0x4849FC was re-extracted and `bytes.json` matches the candidate. All 22 little-endian words decode as follows:

- `0x004849A4` → `0x2006F690`; cited range consumers: 21818, 21834, 21836
- `0x004849A8` → `0x2006F548`; cited range consumers: 21818, 21828, 21834, 21836, 21850, 21854
- `0x004849AC` → `0x007865F0`; cited range consumers: 21818, 21820, 21844
- `0x004849B0` → `0x0077FBE4`; cited range consumers: 21818
- `0x004849B4` → `0x00760A70`; cited range consumers: 21818, 21820, 21840, 21842, 21844
- `0x004849B8` → `0x0077FBD0`; cited range consumers: 21818
- `0x004849BC` → `0x006E859C`; cited range consumers: 21818, 21820, 21826, 21840, 21842, 21844, 21850, 21854
- `0x004849C0` → `0x0077FC0C`; cited range consumers: 21820
- `0x004849C4` → `0x0077FBF8`; cited range consumers: 21820
- `0x004849C8` → `0x2006F684`; cited range consumers: 21824
- `0x004849CC` → `0x0073F4D0`; cited range consumers: 21826
- `0x004849D0` → `0x00760A90`; cited range consumers: 21826
- `0x004849D4` → `0x00786620`; cited range consumers: 21840, 21842
- `0x004849D8` → `0x00786610`; cited range consumers: 21840, 21842
- `0x004849DC` → `0x00786600`; cited range consumers: 21840
- `0x004849E0` → `0x00786630`; cited range consumers: 21842
- `0x004849E4` → `0x0077FC20`; cited range consumers: 21844
- `0x004849E8` → `0x007780BC`; cited range consumers: 21844
- `0x004849EC` → `0x0073F4FC`; cited range consumers: 21850
- `0x004849F0` → `0x007780D4`; cited range consumers: 21850
- `0x004849F4` → `0x0074A834`; cited range consumers: 21854
- `0x004849F8` → `0x00786640`; cited range consumers: 21854

Every word has at least one literal consumer record among maps 21818–21856. I also found additional consumer records in earlier maps (16546 and 179xx); the listed current-range consumer evidence is valid but not exhaustive. This verifies raw words and PC-relative consumer records, not RAM contents, pointed-to flash payloads, target ownership, or whole-image coverage. Review remains partial/unaccepted.
