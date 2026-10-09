# Stock 0x201C supported-state layout binding

Locked2.2.6.10 Apollo OTA SHA256 `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`, offset20 maps438000. Selected ranges freshly hash-match current authenticated symbol index; hashes/literal values in HCI-201C-STOCK-BINDING.json. No emulator behavior substitutes for these bindings.

## Command producer and response consumer

`HciLeReadSupStatesCmd`52B37C..52B396 constructs command201C with zero parameter length via52AE38, then submits via52AE5E when allocation succeeds. It is an Apollo command producer, not proof of the controller's response producer. Ghidra decomp corroborates the constants; retained original disassembly and range hash supply byte identity.

`hciCoreResetSequence`569B56..569D26 first tests event code0E at569B58–5C. It decodes opcode bytes at original event offsets3/4, little-endian, at569B60–6A.569B6E–70 advances pointer to original offset6. The arithmetic switch's201C branch reaches569C46: length8;569C48 loads literal569D44=200714D8;569C4E calls439BE4 copy with source originaloffset6;569C52 invokes next reset command52B396. The preceding LEbuffer-size branch569C40 calls52B37C, binding this request into reset sequencing.

Pinned Pigweed schema defines EventHeader(code,length), CommandComplete(header,num_hci_command_packets,opcode), then status and8byte LE states. Therefore offsets0code,1length,2commandcredits,3–4opcode,5status,6–13bitmap agree exactly with stock's opcode parser and eightbytecopy. The schema resolves field names/bitmapextent and standard bit semantics; this was already the known Cordio reset family, not a new library attribution.

## Status and bits: limits

This selected reset consumer skips status atoffset5; it does not test it before201C copy. No eventlength guard is visible inside this selected routine. Upstream dispatch may validate status/length; absence inside this range does not establish absence across ingress or a confirmed malformed-packet bug.

Pigweed bitmap bit6 means initiating; bit35 central connection plus connectable/scannable undirected advertising; bit41 peripheral connection plus initiating. In copied bytes at200714D8 these correspond to byte0mask40,byte4mask08,byte5mask02 respectively. This gives exact interpretation **if corresponding controller response bits are present**. No bit6/35/41-specific stock decision or runtime bitmap values were authenticated in this finite pass. Bounded symbol/decomp lookup yielded the reset consumer, not a stock capacity/rolepolicy proof. Emulatorfixtures or states cannot establish the physical controller's advertised support.

No authenticated EM9305 controller-side201C response producer is identified here; its vendor ARC handlers require separate address-bound analysis. Stop before substituting modelresponse or genericschema as its implementation. Useful nextcheck only if justified: find crossreferences to200714D8 or semanticgetter/caller then classify actualmaskuses; independentlybind a frozen realresponse ifavailable. Currentresult establishes Apollorequest and reset-response storage contract, not sourcecompleteness/capacity/physicalbehavior.
