
void FUN_100123cc(uint param_1)

{
  bool bVar1;
  uint uVar2;
  uint uVar3;
  undefined4 local_1c;
  undefined4 uStack_18;
  int iStack_14;
  int iStack_10;
  uint uStack_c;
  
  uStack_18 = 0;
  if (param_1 != 0) {
    uVar3 = LZCOUNT(param_1) + 0x1d;
    uVar2 = LZCOUNT(param_1) - 3;
    local_1c = 3;
    bVar1 = (uVar2 & 0x80000000) == 0;
    uStack_c = (param_1 >> 1) >> (0x1f - uVar3 & 0x3f);
    if (bVar1) {
      uStack_c = param_1 << (uVar2 & 0x3f);
    }
    iStack_10 = param_1 << (uVar3 & 0x3f);
    if (bVar1) {
      iStack_10 = 0;
    }
    iStack_14 = 0x3c - uVar3;
    FUN_10012504(&local_1c);
    return;
  }
  local_1c = 2;
  FUN_10012504(&local_1c);
  return;
}

