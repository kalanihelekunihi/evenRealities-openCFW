
int FUN_004cf6e8(int param_1)

{
  undefined4 uVar1;
  undefined2 uVar2;
  int iVar3;
  uint uVar4;
  uint local_34 [2];
  undefined1 auStack_2c [32];
  
  iVar3 = FUN_004caf2e(param_1 + 0x3c);
  if (iVar3 == 0) {
    iVar3 = 0;
  }
  else {
    uVar2 = FUN_004caeb0(*(undefined4 *)(param_1 + 0x3c));
    uVar1 = DAT_004cfa2c;
    FUN_004733ee(DAT_004cfcc4,DAT_004cfa2c,0x1361,*(undefined4 *)(param_1 + 0x40),
                 *(undefined4 *)(param_1 + 0x44),uVar2,&DAT_004cf944);
    iVar3 = FUN_004cae98(*(undefined4 *)(param_1 + 0x3c));
    if (iVar3 != 0x4ff) {
      FUN_004d09b4(DAT_004cfcc8,uVar1,0x1365);
    }
    iVar3 = FUN_004cbedc(param_1,auStack_2c,param_1 + 0x40);
    if (iVar3 == 0) {
      uVar4 = FUN_004caeb0(*(undefined4 *)(param_1 + 0x3c));
      FUN_004cf5ec(param_1,0x3ff,0);
      local_34[1] = 0;
      local_34[0] = DAT_004cfcb8 | (uVar4 & 0xffff) << 10;
      iVar3 = FUN_004cd388(param_1,auStack_2c,local_34,1);
      if (iVar3 == 0) {
        iVar3 = 0;
      }
    }
  }
  return iVar3;
}

