# Bounded ARC recovery: `0x003068C8`

This private candidate covers `[0x003068C8,0x0030690C)` (68 authenticated bytes, 21 contiguous ARCv2 EM instructions). The symbol catalog proposes the name `IRQ_Cleaning`; its referenced SDK comparison report is absent in the workspace, so the label is only a seed. The body initializes `LP_COUNT` to 18, installs a zero-overhead loop ending at `0x0030690A`, and returns by `j_s [blink]`. There are no literal-pool or jump-table bytes inside the span: every byte decodes as an instruction, with long immediates encoded within their instruction lengths.

```text
function candidate_003068c8(opaque_r0):
    CLRI(0)
    SYNC()

    LP_COUNT = 18
    base = 0x00F00808
    r2 = 0
    r1 = 0
    r3 = base

    # ARC zero-overhead loop whose end instruction is 0x0030690A.
    repeat 18 times:
        if r1 == 17:
            selected = 0x99            # 0x003068E8 delay-slot instruction
        else:
            selected = r2               # fall-through at 0x003068EA
            M32[r3] = 0xFFFFFFFF        # skipped by the terminal taken branch

        row = base + (selected << 2)     # ADD2 r0,r12,r0 at 0x003068F0
        M32[row + 12] = 0xFFFFFFFF
        SYNC()
        M32[row + 24] = 0xFFFFFFFF
        SYNC()

        r3 += 0x24
        r2 += 9
        r1 += 1

    return                                # j_s [blink] at 0x0030690A
```

## Loop and writes

`LP_COUNT=0x12` (18) and `LP` designate the zero-overhead loop. `r1` starts at zero and increments once per pass; the comparison at `0x003068E4` selects the special terminal path exactly when `r1==0x11`. The delayed instruction loads `0x99` on that branch; otherwise the following move selects `r2`. The no-argument setup means incoming `r0` is not used by the observed body.

`ADD2` adds the second operand shifted left by two bits, so the row address for pass `i` is `0x00F00808 + 36*i`: `r2` advances by 9 while `r3` advances by 36. Passes 0 through 16 write `0xFFFFFFFF` at row offset 0, and all 18 passes write the same value at offsets 12 and 24. The final pass skips the offset-0 store and uses selected index `0x99` (153), which yields its terminal row address. Thus the statically implied trace contains 53 word stores and 36 `SYNC` instructions across those writes. These are address and instruction facts only; no peripheral or register-array meaning is assigned to `0x00F00808`.

The direct caller is packet 1288 at `0x00302B20`, an ordinary non-delayed `BL`. `r0` was last formed from `LR[STATUS32]`, bit-set at 13, and passed to `KFLAG`; there is no callee-specific setup or delay slot. The body does not read that value before using `r0` as a loop temporary. Its first instruction is `CLRI 0`; the function does not restore a prior status value in this bounded body. No hardware interrupt or timing behavior is claimed.

## Boundary and uncertainty

The candidate begins at the catalog row’s `0x003068C8` start and ends with `j_s [blink]` at `0x0030690A`. Packet 1512 independently decodes the immediately following helper `[0x0030690C,0x00306922)`. The context also shows a two-byte `nop_s` at `0x00306922` and the next catalog function beginning at `0x00306924`. No global entry census or SDK comparison report was available, so this remains a bounded private ownership candidate pending review.

Static fixtures validate the 18 loop states and their write addresses from the authenticated body; they are not target execution. No C implementation or canonical admission is included.
