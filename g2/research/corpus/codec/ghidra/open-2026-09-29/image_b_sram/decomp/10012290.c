
undefined4 FUN_10012290(uint param_1)

{
  bool bVar1;
  undefined4 uVar2;
  uint uVar3;
  uint uVar4;
  undefined4 local_18;
  uint uStack_14;
  int iStack_10;
  int iStack_c;
  uint uStack_8;
  
  local_18 = 3;
  uStack_14 = param_1 >> 0x1f;
  if (param_1 == 0) {
    local_18 = 2;
  }
  else {
    if ((int)param_1 < 0) {
      if (param_1 == 0) {
        return 0;
      }
      param_1 = -param_1;
    }
    uVar3 = LZCOUNT(param_1) + 0x1d;
    uVar4 = LZCOUNT(param_1) - 3;
    bVar1 = (uVar4 & 0x80000000) == 0;
    uStack_8 = (param_1 >> 1) >> (0x1f - uVar3 & 0x3f);
    if (bVar1) {
      uStack_8 = param_1 << (uVar4 & 0x3f);
    }
    iStack_c = param_1 << (uVar3 & 0x3f);
    if (bVar1) {
      iStack_c = 0;
    }
    iStack_10 = 0x3c - uVar3;
  }
  uVar2 = FUN_10012504(&local_18);
  return uVar2;
}

