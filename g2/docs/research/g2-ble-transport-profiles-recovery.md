# G2 BLE EUS/ESS/EFS/NUS transport-profile recovery

Status: authenticated first-party object closure; no production routing.

The four adjacent retained objects below are G2-local Cordio application
adapters, not opaque third-party profile implementations:

| module | retained path | physical interval | functions / body bytes | event | provider handle |
|---|---|---:|---:|---:|---:|
| EUS | `platform\ble\profiles\eus\profile_eus.c` | `[0x004BDE4C,0x004BE228)` | 6 / 800 | `0xA8` | `0x0844` |
| ESS | `platform\ble\profiles\ess\profile_ess.c` | `[0x004BE228,0x004BE3A4)` | 5 / 314 | `0xA9` | `0x0864` |
| EFS | `platform\ble\profiles\efs\profile_efs.c` | `[0x004BE3A4,0x004BE6F0)` | 5 / 596 | `0xAA` | `0x0884` |
| NUS | `platform\ble\profiles\nus\profile_nus.c` | `[0x004BE6F0,0x004BEA04)` | 5 / 664 | `0xAB` | `0x08A4` |

Together these intervals form one contiguous 3,000-byte region with 21
authenticated function bodies (2,374 bytes) and 626 bytes of literal pools,
strings, alignment, and local state references. The function map, complete
physical hashes, direct-call topology, stored callbacks, retained-path
pointers, and absence of strict-interior branch ingress are checked by:

```text
make ble-transport-profiles-closure
```

## Shared recovered behavior

Each object owns the same four-byte control shape: connection ID, handler ID,
CCC-enabled flag, and connection-ready flag. Event `0x12` updates connection
readiness, `0x14` dispatches CCC state, and `0x27`/`0x28` handle connection
open/close. The module-specific event allocates a 12-byte WSF message and sends
the payload through the corresponding Cordio application provider handle.
EUS adds a direct-send companion. EUS, EFS, and NUS retain EasyLogger and/or
product OTA policy that the smaller ESS object does not.

These facts explain the strong structural repetition without implying shared
upstream source: the modules are product service adapters built against one
Cordio provider ABI.

## Third-party provenance sweep

Exact public searches for the retained `APP_Ble*HandlerInit` symbols and the
module-local callback names found no source. AmbiqSuite 2.5.1 ships profiles
`amdtpc`, `amdtps`, `amota`, `amsc`, `ancc`, `custss`, and `vole`; it does not
ship EUS, ESS, EFS, or NUS objects. Nordic's UART Service supplies the generic
NUS concept, but its `ble_nus_*` API and SoftDevice event topology do not match
this G2 object. Packetcraft Cordio supplies the WSF/ATT/provider framework, not
these implementations.

The defensible dependency conclusion is therefore:

- Cordio is the already-admitted provider framework;
- these four translation units are first-party G2 code;
- there is no third-party version or source commit to assign to them;
- the unavailable historical G2 repository commit remains unobservable from
  the binary.

This negative result prevents both a false AmbiqSuite admission and a false
Nordic NUS admission while closing four paths in the first-party frontier.

## Boundary

This closure authenticates and specifies the linked stock objects. It does not
claim historical C recovery, production ownership, radio behavior, or hardware
validation. Any clean-room implementation must separately qualify WSF message
allocation, provider-handle ABI, connection races, CCC transitions, OTA gates,
and dual-device behavior before production routing.
