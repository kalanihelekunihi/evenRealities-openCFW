# G2 service ANCC dependency boundary

Status: complete fail-closed object and dependency audit. Authenticated against
G2 2.2.6.10 only; production routing remains disabled.

The retained path `platform\service\message_notify\service_ancc.c` resolves to
a contiguous candidate object `[0x0049729C,0x00497DE6)`. Twelve recovered
functions account for 2,340 body bytes / 875 instructions inside 2,890 physical
bytes. Six functions / 2,250 bytes are baseline retained-path anchors; five
small leading helpers and one trailing helper are restored by source order and
call topology.

The dependency result is closed:

- 85 direct calls are EasyLogger diagnostics at the admitted `a596b264…`
  baseline.
- 17 calls are exact CMSIS-FreeRTOS v10.5.1 mutex new/acquire/release wrappers
  at `d213f261…`.
- 10 calls are bounded IAR memcpy/memset/strlen routines.
- The remaining 17 calls terminate at already closed G2 display, role, sync,
  settings, and message-callback providers.
- No direct call reaches the copied Ambiq ANCC profile object, and no upstream
  ANCC implementation body is embedded here.

Thus the admitted AmbiqSuite ANCC source snapshot remains the entire reusable
ANCC implementation boundary. This object is Even's message database, mutex,
role/sync dispatch, and callback policy layered above it; it cannot identify a
more precise Ambiq release or private generating commit.

The full audit pins 31 direct entry sites, three stored interior callback
pointers, six raw-data pseudo-`BL` patterns, both retained-path literal cells,
and the exact adjacent `service_even_ai.c` boundary. There are no indirect calls
or executable strict-interior entries. The behavior is a mutex-protected fixed
database of ten 0x304-byte records with message-count callbacks and role/display
sync dispatch.

Reproduce with:

```sh
python3 tools/analyze_g2_service_ancc.py
python3 -m unittest -v tests.test_analyze_g2_service_ancc
make service-ancc-closure
```
