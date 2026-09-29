
undefined4 gx8002_aout_init(uint param_1)

{
  func_0x10025080(0xb,1);
  func_0x10025080(0xf,1);
  uRam00000020 = uRam00000020 | 0xe;
  if (param_1 == 2) {
    uRam00000004 = uRam00000004 & 0xfffff37f | 0x400;
  }
  else {
    uRam00000004 = (param_1 & 3) << 10 | uRam00000004 & 0xfffff3ff;
  }
  do {
  } while ((uRam0000000c & 0x100000) == 0);
  uRam0000000c = uRam0000000c & 0x100000;
  uRam00000000 = uRam00000000 | 0x80000000;
  return 0;
}

