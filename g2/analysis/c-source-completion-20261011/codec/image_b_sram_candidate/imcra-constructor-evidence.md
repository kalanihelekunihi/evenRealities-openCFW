# Image-B IMCRA composite source reduction

Native image-B SHA256
`d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941`,
base `0x10003000`. Direct instruction disassemblies:
`native_imcra_ctor_1000e784.disasm`, `native_imcra_sizes.disasm`,
`native_imcra_sub_bc.disasm`, and `native_imcra_sub_d.disasm`.

- Composite `0x1000e784` receives two signed integer parameters in r0/r1
  and destination in r2. It zeroes 40 bytes, writes those integers at
  offsets 0/4 and zeroes header slots 8..20. It constructs four child
  records at offsets 40, 88, 140, 204, using native size returns 48,
  52 and 64. It stores the returned child pointers at offsets 24..36.
  `verify_imcra_constructor_host.c` checked all four child addresses,
  21 source configuration lookup positions/derived values, call order,
  and header slots: 5/5.
- A `0x1000ea74` takes fr0-fr3 and two stack words, zeroes 48 bytes,
  stores four floats and stack metadata, truncates the rate float to an
  unsigned sample count, computes two `expf(-logf(9)/(count*span))`
  coefficients and marks byte 44 initialized. Three size leaves at
  `0x1000ea68`, `0x1000eb48`, `0x1000ec2c` are exact native
  mode-nonzero selectors (48,52,64). A/size fixtures: 9/9.
- B `0x1000eb54` and C `0x1000ec38` have the same four float plus three
  stack-float contract, 52/64 byte zero extents and two decay
  coefficients. C additionally stores signed truncation of
  `sample_count*span2` at offset 44. B/C fixtures: 9/9.
- D finishing policy `0x1000ed2c`: positive level returns -1 with no
  write; less than -80 sets gain zero; otherwise stores the level at
  offset 16 and `powf(10,level/20)` at offset 60. Fixtures: 3/3.

Open real contracts: initialized configuration words from SRAM
`0x20016fb8..0x20017008`, setting word at `0x2002d7b4`, native expf
`0x100109c0`, and D constructor `0x1000ed7c`. The D constructor calls
float-environment/double helpers `0x10011af4`, `0x1000f84c` and
`0x10012398`; its full rounding/exception semantics remain unowned.
The source intentionally retains these as imports, and the initialized
configuration contains no guessed values. Host fixtures qualify C layout
and arithmetic for sampled inputs, not original FPU exception flags or
hardware execution.

Coherent CK804EF build: `build-imcra-substates-round/receipt.json`, 134 units, linked SHA256 `33d597a2d2a86222c9adf47909c2601f7660c31c2deeba9eee284f36caee1d86`. 8 unresolved symbols are explicit true code/data/ABI contracts. The finite address crosswalk now covers 197/288 catalogued entries; 91 remain outside.

D child constructor `0x1000ed7c..0x1000ee63` now has C source. It clears 64 bytes, handles null, writes float fields at offsets 0..36, and uses native float-to-binary64-exp-to-float decay sequencing; `verify_imcra_d_host.c` passes 2/2 record-layout/call-order fixtures. Binary64 exp `0x1000f84c` remains a true source import. Coherent target rebuild `build-imcra-d-round/receipt.json`: 135 units, linked SHA256 `74688b132c329399a1ff3f5d9c8102cacd9edef6aecf25917797b08bd911a29c`; crosswalk 198/288, 90 outside.

Final D/runtime coherent receipt: `build-imcra-d-runtime-final/receipt.json`, 136 units, SHA256 `2dc5b232117835bdf823217b41d27b9ed17b6914ced99e689cd4076fa7c7d05d`. Pinned LLVM compiler-rt `truncdfsf2.c` plus its exact include dependencies lives in `third-party/upstream/llvm-compiler-rt-format-20.1.8`, with a C-SKY warning-only wrapper. Remaining symbols: __fe_getround, __fe_raise_inexact, gx8002_image_b_exp_double_1000f84c, gx8002_image_b_expf_100109c0, gx8002_image_b_imcra_cfg_words_20016fb8, gx8002_image_b_imcra_setting_2002d7b4, gx8002_image_b_native_word_at_zero_1000ada6, gx8002_image_b_uart_dma_ambient_direction_100040e8.
