# Codec UART open/close flags, retained staging and error propagation

**213 original/source comparisons PASS**, including ordered selected state writes and provider arguments. [New reconstructed C](../../components/audio/codec_uart_lifecycle_offline/lifecycle.c), [helper interfaces](../../components/audio/codec_uart_lifecycle_offline/lifecycle.h), [results and phase states](results.json), [final ELF/source hashes](reproduction-receipt.json), [image/address evidence](provenance.json). Existing ring-write/drain source is reused unchanged.

## Distinct state domains

Codec ring descriptor20073ED4 uses64-byte storage200731B0/mask63. First initialize0x58FB52, controlled by initialized byte20075014, resets read/write indices, installs callback58FB1D on channel3 and sets initialized1. Open byte20075015 separately controls channel enable0x55E5BC. Already-open initialize returns0 without enabling again. Close0x58FC0C returns0 if already closed; otherwise calls channel disable0x55E630 and clears open only on success. **Close does not reset initialized byte, ring indices/data or registered callback.**

Channel table20000D2C stride28 has handle+4,pin-table+8,config+12,callback+20,active+24,completion+25. Enable calls HAL power(handle,0,1),configures both pins and **sets active1 even if power failed**, returning its status; GPIO return values are ignored. Disable first clears active0,configures raw RX3/TX E083 shutdown words,then calls HAL power(handle,2,1). These config words are pinned constants; no electrical interpretation or physical state is asserted. Callback registration byte-narrows channel and writes only for valid channel<4 and nonNULL callback; NULL cannot clear an existing callback through this helper.

## Retained bytes and retry traps

An executed initialize→explicitRXcallback(10,20,30)→close→initialize→drain sequence proves pending bytes survive successful close/reopen and are independently copied by the existing drain provider. With initialized0, drain returns those3bytes; with initialized1, it also returns the3preexisting A5 fixture bytes. No reset/drop happens on reopen. Callback entry is explicitly synthetic, not a claim that an IRQ arrives while closed or failed-open. Hardware noise/loss/stale responses are not measured.

Failed enable yields codec-init-1 with initialized1/open0 but channel-active1. There is no rollback of channel-active/pins. Failed close yields-1 with open1 but channel-active0. A subsequent init sees open1 and returns0 without re-enabling. The tested host-init→close→host-init sequence confirms this logical mismatch under injected failure statuses. These are actionable software recovery requirements, not proof that real hardware produces those failures.

## Baud/configuration

Channel baud0x55E898 accepts any nonzero active byte (TX wrapper instead requires exactly1), copies16-byte baseline config into a local buffer, replaces its first word, and normalizes configure status to0/1. The baseline table is not updated. Codec baud0x58FAB6 selects channel3. Host initialize0x57BA88 requests **115200 baud (0x1C200)** after codec init succeeds, but **ignores the baud setter error and returns0**. This is a requested software value, not measured line rate. It is separate from logger channel1's921600 configuration. Following failed close, host init can skip enable, see inactive descriptor in baud setter, and still return0.

## Scope and next source boundaries

Inputs span initialized/open0/1,enable/disable/configure statuses0/7,sequential initialize/RX/close/reopen/drain and host/close/host,channel0/3/4/259,active0/1/2,NULL/nonNULL callback,GPIO return7,and ring sizes0/1/2/64/128. Size0 is admitted by original bit-test and publishes maskFFFFFFFF; it is a degenerate initialization observation, not a usable ring claim. Non-power-of-two assertion paths are excluded. Callback pointers normalize original58FB1D and compiled successor symbol as the same relocated interface; raw firmware addresses are not falsely compared as equal to compiled addresses.

Power/configure/GPIO are explicit status/argument providers; logs disabled. Native reached executable code is guarded to compiled source. No physical power,GPIO,baud,actual IRQ,whole initializer or shutdown/drain guarantee. Prior source-backed HAL power/configure exists separately; this wrapper suite does not compose all its revision/clock/power dependencies. Whole codec DFU and hardware writes are deliberately unexecuted.

Next source/dependency leads: compose these wrappers with pinned HAL retained-power/configure and known clock/GPIO providers; investigate GPIO provider frontend and callback/IRQ channel registration. Request serialization, expected-response command/sequence matching and physical closure ordering remain distinct app/CFW requirements. The separate [notification tick composition](../audio-notifier-tick-replay-composition-2026-10-09/REPORT.md) reduces scheduler software-ordering opacity but does not establish real interrupt or quiescence behavior.
