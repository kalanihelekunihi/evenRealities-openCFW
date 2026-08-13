# Nordic TWIM transfer-completeness correlation

## Result

The exact 98-byte function `0x00098DC0..<0x00098E22`, SHA-256
`8446af0756cad758941444cdf80848a92b988be41f55c39b21fea02c59fbe648`,
is Nordic SDK 17.1.0
`modules/nrfx/drivers/src/nrfx_twim.c::xfer_completeness_check`.

Its only direct callsites are `0x00093A44` in the TWIM1 interrupt path and
`0x00093DB8` in `nrfx_twim_xfer`. Ghidra associates those non-contiguous
compiler blocks with the already source-routed entries `0x00031A84` and
`0x0007B448`; the executable callsites themselves are verifier-pinned.

The census is reproducible with:

```sh
python3 tools/summarize_r1_nordic_twim_completeness.py
```

## Function-local match

The recovered body exactly implements Nordic's four transfer-type cases:

- TXTX selects primary versus secondary TX length using the SUSPENDED
  interrupt-mask bit;
- TXRX checks TX primary and RX secondary EasyDMA amounts;
- TX checks TX primary amount;
- RX checks RX primary amount.

If any latched EasyDMA amount differs from the requested descriptor length,
the function reports incomplete transfer and resets the TWIM state machine by
writing `ENABLE = 0` followed by `ENABLE = 6`. Otherwise it reports complete.
The descriptor offsets, TWIM `TXD.AMOUNT` / `RXD.AMOUNT` offsets, switch order,
and reset sequence all agree with the pinned provider source.

The linked clean-room firmware already compiles Nordic's `nrfx_twim.c`; this
closure changes source ownership and verification only. No Nordic TWIM body is
recreated locally.

## Admission decision

- provider family: `nordic_nrf5_sdk_17_1_0`;
- disposition: `use_nordic_sdk`;
- local implementation: prohibited;
- local scope: board configuration, product adapters, link integration, and
  verification only.
