
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_100081b8(uint param_1,int param_2)

{
  param_1 = param_1 & 0x1f;
  if (param_2 == 0) {
    _DAT_a0001004 = _DAT_a0001004 & (-2 << param_1 | 0xfffffffeU >> 0x20 - param_1);
  }
  else {
    _DAT_a0001004 = _DAT_a0001004 | 1 << param_1;
  }
  return 0;
}

