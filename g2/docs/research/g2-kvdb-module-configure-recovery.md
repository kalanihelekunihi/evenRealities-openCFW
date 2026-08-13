# G2 module-configuration KVDB recovery

Status: complete binary census and host/Thumb-qualified clean-room candidate;
not production-routed. Run addresses use
`run = file_offset + 0x00437FE0`.

## Result

The retained first-party path
`platform\service\flashDB\kv\service_kvdb_module_configure.c` owns six
functions:

| Function | Stock span | Bytes | Role |
|---|---:|---:|---|
| language reader | `[0x4922F8,0x49240E)` | 278 | validate/import a one-byte language |
| language writer | `[0x49240E,0x492422)` | 20 | persist one language byte |
| dashboard reader | `[0x492422,0x4924F6)` | 212 | conditionally import/default a word |
| dashboard writer | `[0x4924F6,0x492508)` | 18 | persist the dashboard word |
| menu reader | `[0x492508,0x49292E)` | 1,062 | import the packed menu record |
| menu writer | `[0x49292E,0x492BE6)` | 696 | compare/rebuild/persist the menu record |

The complete interval is `[0x004922F8,0x00492CB4)`, 2,492 bytes, SHA-256
`0d6e8a631baccc0090004a182331d60bf1e697e11a1b0b0337ad751bfdd958e7`.
The bodies contribute 2,286 bytes with concatenated SHA-256
`b0d452d61f46d4f3135d76b9249a481ed3a71c050ea7d3700caa61a35f4662eb`;
the 206-byte remainder is alignment and a single complete literal pool.

Three direct calls root the writer entries and three stored Thumb pointers at
`0x00746D24...0x00746D2C` root the readers. The bodies contain 115 direct
provider/internal calls. No `BL` or `B.W` targets a strict body interior.
Seven raw interior-looking words begin at odd byte offsets. The sole aligned
one, at `0x58ECC8`, begins at the second halfword of the valid 32-bit Thumb
instruction `vmov s3, r2` spanning `[0x58ECC6,0x58ECCA)`. None is pointer
data or legitimate ingress.

## Scalar records

`kvSystemLanguage` persists one byte but updates a 32-bit live global at
`0x20000030`. Stored values zero through seven are accepted. A missing value
or a value of eight or greater resets the global to zero. The writer persists
one byte and discards the backend result.

`kvDashboardAutoCloseValue` persists a 32-bit value at `0x20000038`, whose
authenticated initialized value is ten. When the mode provider returns two,
the reader performs no database access and leaves the global untouched.
Otherwise a successful read imports the word and a missing read restores ten.
Its writer likewise discards the backend result.

## Menu record and runtime ABI

The `kvMenuConfigureValue` record at `0x2006D43C` is exactly 888 bytes:

| Offset | Bytes | Meaning |
|---:|---:|---|
| 0 | 4 | magic `0x5555AAAA` |
| 4 | 1 | item count |
| 5 | 3 | padding |
| 8 | 880 | twenty 44-byte stored items |

Each stored item contains icon byte at +0, three padding bytes, `app_type` at
+4, 32 text bytes at +8, and `app_id` at +40. The runtime array begins at
`0x2006AD0C` with a 52-byte stride: resource +0, text +4, page value +36,
icon +40, `app_type` +44, and `app_id` +48. External-menu enabled/count
globals are at `0x200746FC` and `0x20074700`.

The reader first zeros the packed record. Missing data or bad magic returns
success without changing the selection globals. For icon zero it resolves a
built-in item by `app_id`; lookup failure returns minus one before committing
the globals. A custom item forces page value `0xFFE`, icon one, and resource
`0x0076B7BC`, then copies exactly `strlen(stored_text)` bytes. It does not add
a terminator or import the stored `app_type`. After every item succeeds it
sets the enabled flag and publishes the stored count.

The writer rejects any state other than enabled==1 and count>=1. A valid
stored record with equal count and byte/string-equivalent items is left
untouched. Otherwise it zeros the record, brackets the runtime snapshot with
the two stock synchronization providers, writes magic/count and every item,
then returns the database result. The stock reader and writer contain no
count<=20 or text<=32 clamp; the candidate preserves that observable contract
rather than inventing validation absent from the image.

## Reconstruction boundary

`components/apollo_main/core_overlay/kvdb_module_configure.c` is an
independently authored six-entry candidate (11,893 bytes, SHA-256
`9eb84180d0b211f168b64d8aaa5acc762e815236c17b7955ce432b94447ab1db`).
Host tests cover every scalar branch, mode-two bypass, missing/bad menu data,
built-in and custom import, lookup failure, readiness rejection, identical
write suppression, record rebuild, synchronization, and backend propagation.
Freestanding compilation exposes exactly six global Thumb text symbols. The
analyzer and manifests pin every body, literal, ingress edge, raw-overlap
qualification, initialized scalar, and packed ABI offset.

The exact historical source revision is unresolved and provider/diagnostic
names remain abstract. The candidate is absent from `overlay.json`; placement,
redirects, provider binding, and package verification remain pending, so it
claims zero package ownership bytes.
