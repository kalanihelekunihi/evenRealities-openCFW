
uint FUN_100122f8(undefined4 param_1,undefined4 param_2)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  undefined4 local_20;
  undefined4 uStack_1c;
  uint uStack_18;
  int iStack_14;
  int iStack_10;
  uint uStack_c;
  uint uStack_8;
  
  local_20 = param_1;
  uStack_1c = param_2;
  FUN_10012694(&local_20,&uStack_18);
  if (uStack_18 < 3) {
    return 0;
  }
  if (uStack_18 != 4) {
    if (iStack_10 < 0) {
      return 0;
    }
    if (iStack_10 < 0x1f) {
      uVar2 = -iStack_10 + 0x3c;
      uVar3 = -iStack_10 + 0x1c;
      uVar1 = uStack_8 >> (uVar3 & 0x3f);
      if ((uVar3 & 0x80000000) != 0) {
        uVar1 = uStack_c >> (uVar2 & 0x3f) | (uStack_8 << 1) << (0x1f - uVar2 & 0x3f);
      }
      if (iStack_14 == 0) {
        return uVar1;
      }
      return -uVar1;
    }
  }
  return (iStack_14 != 0) + 0x7fffffff;
}

