
undefined4 FUN_0047da78(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  undefined4 uStack_c;
  undefined4 uStack_8;
  undefined4 uStack_4;
  
  iVar2 = DAT_0047dc3c;
  piVar1 = DAT_0047dc38;
  if (param_1 != 0) {
    uVar4 = -*DAT_0047dc38 + 0x1193;
    if (uVar4 != 0) {
      uStack_c = param_2;
      uStack_8 = param_3;
      uStack_4 = param_4;
      uVar3 = FUN_0044b76c(*DAT_0047dc38 + DAT_0047dc3c,-*DAT_0047dc38 + 0x1194,param_1,&uStack_c);
      if (0 < (int)uVar3) {
        if (uVar4 < uVar3) {
          *piVar1 = uVar4 + *piVar1;
        }
        else {
          *piVar1 = uVar3 + *piVar1;
        }
      }
      *(undefined1 *)(iVar2 + *piVar1) = 0;
    }
  }
  return param_4;
}

