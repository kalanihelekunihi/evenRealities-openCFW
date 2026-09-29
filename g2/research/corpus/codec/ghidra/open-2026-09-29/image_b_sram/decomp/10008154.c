
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_10008154(uint param_1,int param_2)

{
  uint uVar1;
  
  param_1 = param_1 & 0x1f;
  if (param_2 == 1) {
    _DAT_a0001008 = _DAT_a0001008 & ~(1 << param_1);
    _DAT_a0001000 = 1 << param_1 | _DAT_a0001000;
    return 0;
  }
  if (param_2 == 0) {
    _DAT_a0001000 = _DAT_a0001000 & ~(1 << param_1);
    _DAT_a0001008 = 1 << param_1 | _DAT_a0001008;
  }
  else if (param_2 == 2) {
    uVar1 = -2 << param_1 | 0xfffffffeU >> 0x20 - param_1;
    _DAT_a0001008 = _DAT_a0001008 & uVar1;
    _DAT_a0001000 = uVar1 & _DAT_a0001000;
    return 0;
  }
  return 0;
}

