# R1 generated-model data admission

## Decision

The generated-model parameters formerly represented only as caller-supplied inputs now compile as
ordinary C integer constants in `reconstructed/model_data`. The production build does not read,
link, concatenate, or package the reconstructed research image. That image is used only by
`tools/generate_r1_model_data.py --check` to prove that the checked-in initializer still equals
the SHA-pinned Ghidra data ranges.

The three consumers overlap in stock flash, so the source stores one deduplicated word array and
exports three bounded typed views:

| View | Stock range | Words | SHA-256 |
| --- | --- | ---: | --- |
| Goodix generated model | `0x000B19E4..<0x000B5734` | 3,924 | `655f94539fd186e8c99d5e616c296dba63b247a114963870c044798cd75fef47` |
| GoMore sleep model, modes below 100 | `0x000B2458..<0x000B7998` | 5,456 | `da353b02976da84378f6321b2f5ec7cbc4c184eb706b1d6a7fad5499258c4861` |
| GoMore sleep model, modes 100 and above | `0x000B7998..<0x000BCED8` | 5,456 | `09f807f0c73daae139a0f2aa39ec37b4c57db8c6a7178e943aec6bd8913ee82c` |

The union is `0x000B19E4..<0x000BCED8`: 46,324 bytes / 11,581 little-endian
`uint32_t` words, SHA-256
`cde455f534ef8528509bca8e7c65460af63187d835274ec4fa007ce1811dd470`.
The Goodix view begins at union word zero, the lower GoMore view at word 669, and the upper
GoMore view at word 6,125. Compile-time assertions keep every view inside the admitted union.

## Provenance and build boundary

`r1_model_data_generated.inc` is a transparent, reviewable initializer containing only explicit
`UINT32_C` constants. The generator accepts only the reconstructed application with SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`, then independently
checks the union and all three view hashes before rendering. Normal host, Cortex-M4, and Nordic
SDK builds consume the checked-in initializer and require no firmware image.

The parameters are recovered product data, not a claim that the trained values were independently
derived. Their source admission removes the last stock-image byte dependency from the Goodix and
GoMore generated-model paths while keeping their origin explicit.

## Reproduction

```sh
python3 tools/generate_r1_model_data.py --check
make test arm-objects
```
