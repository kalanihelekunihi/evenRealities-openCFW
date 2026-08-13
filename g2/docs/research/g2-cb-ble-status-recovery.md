# G2 BLE-status callback facade recovery

The retained `platform\service\callback_mgr\cb_ble_status.c` path closes as a
202-byte linked object at `[0x004ABCC6,0x004ABD90)`: three functions / 168
reachable body bytes followed by a 34-byte literal pool. The two retained-path
anchors are the exact diagnostic-named register and unregister functions; the
adjacent pathless 14-byte body is the notification dispatcher. The following
code at `0x004ABD90` is independently reachable NVDB product-mode code and is
excluded from this object.

`CB_BLE_STATUS_RegisterCallback` and
`CB_BLE_STATUS_UnregisterCallback` reject null functions with diagnostics and
otherwise call the generic manager over the `BLE_STATUS` list record at
`0x20073F6C`. The semantic `CB_BLE_STATUS_Notify` passes its event plus an
in/out status word to the generic list dispatcher and returns the possibly
updated word. Ten exterior BL sites reach the three entries. There are no
stored entry pointers, indirect calls, strict-interior targets, or unresolved
object calls.

## Provider result

The object has 13 direct external calls:

- ten reach the already admitted EasyLogger 2.2.99-equivalent seam, selected
  at commit `a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24`;
- one each reaches first-party `callback_manager.c` register, unregister, and
  invoke providers at `0x00510240`, `0x005103C4`, and `0x005105BC`.

There is no direct CMSIS-FreeRTOS, Cordio, IAR DLIB, allocator, or protobuf
edge and no upstream definition is embedded. Consequently this closure adds
no dependency family or version/commit discriminator. It narrows the future
port to a small first-party typed facade over the generic callback manager;
the object is not yet production-routed.
