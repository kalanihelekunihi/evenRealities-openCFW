# G2 dashboard news-page dependency boundary

Status: complete read-only closure of
`app\gui\dashboard\screens\ui_widget_news_page.c` in authenticated stock G2
firmware 2.2.6.10. This is analysis evidence, not a production route.

## Complete object

The source-order object is `[0x004EFF94,0x004F5050)`: 20,668 physical bytes.
Its 22 retained-path anchors expand to 45 functions / 19,058 body bytes. The
31-function Ghidra inventory omitted fourteen helpers recovered from direct
calls and twelve aligned stored Thumb callback cells. The remaining 1,616
bytes are literal pools, alignment, and one six-byte inline region. The object
follows the calendar-page tail and ends before quicklist support code.

The 6,993 reachable instructions make 1,252 direct calls: 56 internal and
1,196 external. A whole-image sweep pins 70 direct entry sites and the twelve
stored callbacks. Seven apparent `BL` decodes into the final literal/function
area and eight apparent wide interior branches are explicitly classified;
none supplies another entry. There are no indirect calls.

## Dependency closure

| Provider | Calls | Provenance |
|---|---:|---|
| LVGL | 508 | selected 9.3-development hybrid commit `344c7c318047b7348e1be8572a9fd4260c251cfa` |
| EasyLogger | 565 | 2.2.99-compatible commit `a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24` |
| CMSIS-FreeRTOS | 8 | four balanced mutex acquire/release pairs from v10.5.1 commit `d213f261b5be6bb29a7cce8b84071706b72f4d53` |
| IAR / ARM EABI runtime | 36 | memory, length, formatting, and source-recreated unsigned division seams |
| G2 first-party | 79 | time, role, dashboard, onboarding, resource, and protobuf policy |

The page embeds no reusable third-party definition and exposes no new version
or producing-commit discriminator. Its private UI layout and behavior remain
first-party reconstruction work.

Reproduce with `make ui-widget-news-page-closure`.
