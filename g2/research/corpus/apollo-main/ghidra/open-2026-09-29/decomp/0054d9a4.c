
undefined4 FUN_0054d9a4(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 in_r3;
  int iVar5;
  int iVar6;
  
  if (*DAT_0054e19c != 0) {
    iVar5 = *DAT_0054dabc;
    for (iVar6 = 0; iVar1 = DAT_0054e440, iVar6 < iVar5; iVar6 = iVar6 + 1) {
      if (*(int *)(DAT_0054e440 + iVar6 * 4) != 0) {
        iVar2 = FUN_0044dce2(*(undefined4 *)(DAT_0054e440 + iVar6 * 4),0);
        iVar3 = FUN_0044dce2(*(undefined4 *)(iVar1 + iVar6 * 4),1);
        if (iVar6 == *DAT_0054e1a0) {
          FUN_0044129e(*(undefined4 *)(iVar1 + iVar6 * 4),0x32,0);
          uVar4 = FUN_0044104c(0);
          FUN_0044127e(*(undefined4 *)(iVar1 + iVar6 * 4),uVar4,0);
          FUN_0044131c(*(undefined4 *)(iVar1 + iVar6 * 4),1,0);
          uVar4 = FUN_0044104c(0xffffff);
          FUN_004412ec(*(undefined4 *)(iVar1 + iVar6 * 4),uVar4,0);
          if (iVar2 != 0) {
            FUN_004413ce(iVar2,0xff,0);
          }
          if (iVar3 != 0) {
            uVar4 = FUN_0044104c(0xffffff);
            FUN_0044140e(iVar3,uVar4,0);
          }
        }
        else {
          FUN_0044129e(*(undefined4 *)(iVar1 + iVar6 * 4),0,0);
          FUN_0044131c(*(undefined4 *)(iVar1 + iVar6 * 4),0,0);
          if (iVar2 != 0) {
            FUN_004413ce(iVar2,100,0);
          }
          if (iVar3 != 0) {
            uVar4 = FUN_0044104c(DAT_0054e1a4);
            FUN_0044140e(iVar3,uVar4,0);
            FUN_005455c6(iVar3,0x100,0);
          }
        }
        FUN_00441488(*(undefined4 *)(iVar1 + iVar6 * 4),0xff,0);
        FUN_005455c6(*(undefined4 *)(iVar1 + iVar6 * 4),0x100,0);
      }
    }
  }
  return in_r3;
}

