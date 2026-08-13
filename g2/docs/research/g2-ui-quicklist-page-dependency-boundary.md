# G2 quicklist page dependency boundary

Status: complete read-only closure of `app\gui\quicklist\ui_quicklist_page.c`
in authenticated stock G2 firmware 2.2.6.10. This is analysis evidence, not a
production route.

## Result

The source-order object is `[0x004F5596,0x004FB1C0)`: 23,594 physical bytes,
of which 80 functions contribute 21,886 body bytes and 1,708 bytes are literal
pools or alignment. The 43 retained-path anchors expand through twenty
pathless Ghidra bodies and seventeen functions restored from direct calls or
stored callback pointers. The preceding bytes belong to the news-page tail;
the function at `0x004FB1C0` is used by the following health page.

The 8,233 recovered instructions contain 1,144 direct calls: 154 internal and
990 external. There are no indirect calls. A whole-image sweep pins 164 direct
entries, fifteen aligned stored Thumb entries, and zero strict-interior or
non-code branch targets. Eight retained-path cells produce 94 authenticated
literal references.

## Dependency result

The external provider split is:

| Provider | Calls | Provenance |
|---|---:|---|
| LVGL | 415 | selected 9.3-development hybrid commit `344c7c318047b7348e1be8572a9fd4260c251cfa` |
| EasyLogger | 465 | 2.2.99-compatible commit `a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24` |
| CMSIS-FreeRTOS | 5 | exact v10.5.1 `osKernelGetTickCount` at commit `d213f261b5be6bb29a7cce8b84071706b72f4d53` |
| IAR DLIB/runtime | 24 | bounded proprietary memory/runtime seams; 9.20+ floor, 9.60.2 leading candidate |
| G2 first-party | 81 | quicklist data, dashboard, animation, protobuf-service, role, and page policy |

No third-party definition is embedded, no additional dependency family is
present, and the object supplies no new version or historical-commit
discriminator. The adjacent `quicklist.c` mutex/event facade and
`pb_service_quicklist.c` protobuf provider were already closed separately; the
remaining UI behavior is private G2 reconstruction work.

Reproduce with:

```sh
make ui-quicklist-page-closure
```
