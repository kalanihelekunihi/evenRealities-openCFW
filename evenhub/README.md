# @opencfw/evenhub

Direct-to-glasses EvenHub SDK for Even Realities G2, built from the stock firmware's
nanopb schema rather than the official WebView bridge. Zero dependencies, TypeScript.

```sh
node --test test/          # 13 tests (Node >= 23.6 runs .ts natively)
npm run typecheck          # tsc via npx
```

* `src/transport.ts` 0xAA multipart framing + CRC16  · `src/pb.ts` protobuf wire codec
* `src/schema.ts` tags/cmds/limits · `src/messages.ts` encode/validate/decode
* `src/image.ts` 4-bpp BMP, RLE, LZ4 block, fragment planner · `src/client.ts` `EvenHubClient` over a pluggable `Link`
* `proto/evenhub.proto` reconstructed schema · `docs/DESIGN.md` design + evidence · `tools/dump_nanopb_desc.py` descriptor dumper

Status: unverified on hardware. See DESIGN.md §5.

## Direct Bluetooth (no Even app)

```ts
import { requestG2, connect } from '@opencfw/evenhub';
const link = await requestG2();              // Web Bluetooth; OS does Just Works bonding
// Node: const link = await (await import('@opencfw/evenhub')).connectNode(); // needs @abandonware/noble
const { hub, firmware, close } = await connect(link); // SecAuth, PipeRole, TimeSync, version, heartbeat
await hub.createPage({ texts: [{ x: 0, y: 0, width: 576, height: 288, containerID: 1, content: 'Hi' }] });
```
Evidence and what still needs a capture: docs/DESIGN.md §6.
