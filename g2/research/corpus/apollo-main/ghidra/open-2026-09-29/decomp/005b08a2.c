
undefined4 FUN_005b08a2(char *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  byte bVar2;
  undefined4 uVar3;
  int iVar4;
  
  cVar1 = *param_1;
  if (cVar1 == '\x01') {
    bVar2 = param_1[4];
    if (bVar2 == 1) {
      uVar3 = FUN_005b4904(1,param_1 + 4,0x94,param_4,param_1,param_2,param_3,param_4);
      return uVar3;
    }
    if (bVar2 != 0) {
      if (bVar2 == 3) {
        uVar3 = FUN_005b4904(2,param_1 + 4,0x94,param_4,param_1,param_2,param_3,param_4);
        return uVar3;
      }
      if (bVar2 < 3) {
        uVar3 = FUN_005b4904(4,param_1 + 4,0x94,param_4,param_1,param_2,param_3,param_4);
        return uVar3;
      }
      if (bVar2 == 5) {
        uVar3 = FUN_005b4904(5,param_1 + 4,0x94,param_4,param_1,param_2,param_3,param_4);
        return uVar3;
      }
      if (bVar2 < 5) {
        uVar3 = FUN_005b4904(3,param_1 + 4,0x94,param_4,param_1,param_2,param_3,param_4);
        return uVar3;
      }
    }
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(2,DAT_005b09f4,DAT_005b09f0,DAT_005b0ab4,0x157,DAT_005b0ab0,param_1[4]);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_005b0ab8,DAT_005b0ab8,param_1[4]);
    }
  }
  else if (cVar1 != '\x03') {
    if (cVar1 == '\x05') {
      uVar3 = FUN_005b4904(10,param_1 + 4,0x48c,param_4,param_1,param_2,param_3,param_4);
      return uVar3;
    }
    if (cVar1 == '\x06') {
      uVar3 = FUN_005b4904(0xb,param_1 + 4,0x408,param_4,param_1,param_2,param_3,param_4);
      return uVar3;
    }
    if (cVar1 == '\a') {
      uVar3 = FUN_005b4904(9,param_1 + 4,0xfa8,param_4,param_1,param_2,param_3,param_4);
      return uVar3;
    }
    if (cVar1 != -1) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(2,DAT_005b09f4,DAT_005b09f0,DAT_005b0ab4,0x165,DAT_005b0abc,*param_1);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_005b0ac0,DAT_005b0ac0,*param_1);
      }
      return 1;
    }
    uVar3 = FUN_005b4904(0xc,param_1 + 4,1,param_4,param_1,param_2,param_3,param_4);
    return uVar3;
  }
  uVar3 = FUN_005b4904(8,param_1 + 4,0xaa8);
  return uVar3;
}

