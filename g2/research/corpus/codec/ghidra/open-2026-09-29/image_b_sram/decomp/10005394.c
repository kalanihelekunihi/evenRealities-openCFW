
undefined4 FUN_10005394(uint param_1)

{
  gx8002_platform_gate(8,1);
  uRam00000028 = uRam00000028 & 0xffff03ff;
  uRam0000002c = uRam0000002c & 0xffff03ff;
  uRam00000000 = uRam00000000 & 0xffffbdff | (param_1 & 1) << 9 | 0x4000;
  *DAT_100053dc = *DAT_100053dc | 2;
  FUN_10005194(10);
  return 0;
}

