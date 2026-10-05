# Binary variable-image storage admission — reconstructed pseudocode

This explains a bounded original-instruction test and static constructor references. It is not firmware C implementation or a complete decoder recovery.

Authenticated source: Apollo OTA payload SHA-256 `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`; payload/runtime conversion `runtime = payload_offset + 0x437FE0` (32-byte preamble). Per-range hashes and exact executed PCs are in `validation.json` and `executed-instructions.jsonl`.

## Attribution chain

`0x5BF332` constructor → literal load into R1 → direct BL `0x5BF2F8` → image object creator `0x498668` → `0x498680(object, descriptor)`. Six direct literal-load/call pairs are verified against bytes; no assumption that arbitrary aligned pointer matches are consumers. Constructor and helper body hashes match their historical source catalogue. The constructor itself is not executed in this batch.

Image setter `0x498680` classifies the source via `0x488CB8`, then queries info via `0x488F6A` → `0x48925A`, which walks registered decoder callbacks. `0x4C794C` installs callbacks `0x4C79D1` (header), `0x4C7B25` (open), `0x4C7E4D` (area), `0x4C7E29` (close). Low bits indicate Thumb entry. Registration stores and variable header/open branches are executed in the bounded test. Global startup ordering and live renderer selection are not traced.

## Descriptor and context layouts

Descriptor (28 bytes, little endian):

```c
struct image_descriptor_pseudocode {
    uint8_t magic;       // +0 = 0x19 for these assets
    uint8_t color;       // +1 = 6, L8
    uint16_t flags;      // +2 = 0 for admitted family
    uint16_t width;      // +4
    uint16_t height;     // +6
    uint16_t stride;     // +8, byte stride
    uint16_t reserved;   // +10
    uint32_t data_size;  // +12
    uint32_t pixels;     // +16: runtime pointer into stored main image
    uint32_t storage;    // +20: zero in static descriptor; constructor sets pixels here
    uint32_t handlers;   // +24: zero in static descriptor; constructed buffer sets handler table
};
```

Decoder context fields used here: source pointer `+0x0C`, source type byte `+0x10` (0 = variable; 1 = filename; 2 = symbol), decoded header `+0x20`, admitted draw-buffer pointer `+0x2C`, workspace pointer `+0x48`. Fields overlap views; this is not a complete context structure.

## Original behavior recovered

```c
// 0x4C79D0: registered header callback, variable branch only
bool variable_image_info(context *ctx, header12 *out) {
    descriptor *src = ctx->source;
    if (ctx->source_type == VARIABLE) {
        copy(out, src, 12);              // original 0x454738 -> 0x439BE4
        if (out->color == 0) return false;
        // If magic differs from 0x19, this branch clears a flag bit;
        // it does NOT universally reject the variable source.
        return true;
    }
    // Filename and symbol branches exist; outside this proof.
}

// 0x4C7B24: variable L8 branch, condensed from executed instructions
bool variable_L8_open(context *ctx) {
    descriptor *src = ctx->source;
    if (src->pixels == 0) return false;
    workspace *ws = ensure_workspace(ctx); // test stub; +0x48 storage
    descriptor *out = &ws->inline_descriptor; // workspace +0x24
    if (src->stride != 0)
        ok = drawbuf_from_descriptor(out, src); // original 0x48B762
    else
        /* derive stride branch; not exercised for these six assets */;
    if (!ok) return false;
    ctx->draw_buffer = out;
    // Remaining cache/postprocess provider is an explicit identity stub.
    return true;
}

// 0x48B762 -> 0x48AEF8, original geometry/storage checks execute
bool drawbuf_from_descriptor(out, src) {
    if (src->data_size < src->height * src->stride) return false;
    zero(out, 28);                       // zero helper externally stubbed
    out->magic = 0x19;
    out->color = src->color;
    out->width = src->width;
    out->height = src->height;
    out->stride = src->stride;
    out->data_size = src->data_size;
    out->pixels = src->pixels;
    out->storage = src->pixels;
    out->handlers = default_handlers;
    out->flags = src->flags;
    // Alignment provider is an identity stub for this L8 fixture.
    return true;
}
```

The six tested assets have `stride == width`, `data_size == stride * height`, flags zero and fully bounded stored pixels. Their unique pixel storage totals 28,872 bytes. These facts establish a typed immutable image storage role; they do not establish exact displayed appearance, renderer pixel-access safety, or all image formats. Static descriptors and constructor pointer literals add 168 and 24 non-code bytes respectively.

## Verification and limits

Eight cases: callback registration, six real variable-L8 descriptor admissions, and a one-byte-short storage capacity rejection. Original header/copy/open/draw-buffer instruction PCs and immutable descriptor reads are persisted; 634 unique original instruction bytes executed. Registry allocator, zero helper, workspace allocator, alignment provider, cache/postprocess and logging are explicit stubs. There is no device, RTOS, live UI or renderer trace. The short-buffer test uses a RAM copy and contributes no stored-image bytes to the map. No full function body or literal pool is admitted as code merely because it was disassembled.
