# G2 `conversate.c` dependency boundary

Status: complete fail-closed linked-object and provider audit over the
authenticated G2 2.2.6.10 Apollo image. This is analysis only; the object is
not production-routed.

## Result

The retained `app\gui\conversate\conversate.c` anchor closes over twelve
functions in `[0x005B0114,0x005B0B58)`: 2,250 executable body bytes and 378
bytes of literal pools, strings, alignment, and object data, for 2,628 physical
bytes total. Nine bodies carry retained-path evidence. Three additional bodies
are restored from source order and control flow.

The first two tiny bodies are a vector-referenced CmBacktrace fault entry and
its self-looping fail-stop tail. The remaining ten implement lazy mutex setup,
serialized controller state, role-gated state messages, activity timeout,
protobuf response handling, UI-event translation, and conversation-payload
dispatch. Whole-image ingress is closed: 46 direct BL entries, three aligned
stored entry pointers (the fault vector and two callbacks), no indirect body
call, and no branch into a strict body interior. One unaligned exact-entry byte
window and eight odd interior words are pinned as non-semantic raw collisions.

## Provider provenance

The 139 external direct calls partition exactly:

| Provider | Calls | Provenance disposition |
|---|---:|---|
| EasyLogger | 80 | selected 2.2.99-compatible commit `a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24` |
| G2 first-party providers | 41 | private product UI, transport, and conversation policy |
| CMSIS-FreeRTOS | 7 | v10.5.1 commit `d213f261b5be6bb29a7cce8b84071706b72f4d53` |
| IAR DLIB memory | 4 | bounded copy/fill primitives; EWARM 9.20+ floor, exact release unobservable |
| nanopb | 3 | selected 0.4.9 compatibility commit `98bf4db69897b53434f3d0ba72e0a3ab1a902824` |
| LVGL | 2 | selected 9.3-compatible ceiling `344c7c318047b7348e1be8572a9fd4260c251cfa` |
| ARM EABI division | 1 | already source-owned OpenCFW reconstruction |
| CmBacktrace | 1 | compatible interval `4abadfa0…73714489`; OpenCFW selects `73714489f9d8af130aacb515586b397b604a5768` |

The CmBacktrace edge is useful corroboration: it proves that the controller's
vector-referenced fatal entry terminates at the already identified third-party
fault provider. It does not narrow the historical checkout beyond the existing
compatible interval, and OpenCFW's `73714489` snapshot remains an explicit
compatibility selection rather than a claim about Even's private commit.

No third-party implementation is embedded in this object, no new dependency
family appears, and no provider edge yields a new point-release discriminator.
The remaining work for this object is first-party source reconstruction and
hardware behavior validation, not third-party identification.

## Reproduction

```sh
python3 openCFW/tools/analyze_g2_conversate_controller.py
python3 -m unittest openCFW.tests.test_analyze_g2_conversate_controller
```

The analyzer authenticates the firmware, three manifests, exact function and
physical hashes, instructions, direct-call graph, all entry encodings, retained
path references, and the selected EasyLogger/LVGL/CmBacktrace provenance pins.
