
undefined4 FUN_0054db30(void)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 in_r3;
  int iVar4;
  
  if (*DAT_0054e5e0 != 0) {
    for (iVar4 = 0; iVar1 = DAT_0054e5dc, iVar4 < 2; iVar4 = iVar4 + 1) {
      if (*(int *)(DAT_0054e5dc + iVar4 * 4) != 0) {
        iVar2 = FUN_0044dce2(*(undefined4 *)(DAT_0054e5dc + iVar4 * 4),0);
        if (iVar4 == *DAT_0054e5d8) {
          FUN_0044129e(*(undefined4 *)(iVar1 + iVar4 * 4),0x32,0);
          uVar3 = FUN_0044104c(0);
          FUN_0044127e(*(undefined4 *)(iVar1 + iVar4 * 4),uVar3,0);
          FUN_0044131c(*(undefined4 *)(iVar1 + iVar4 * 4),1,0);
          uVar3 = FUN_0044104c(0xffffff);
          FUN_004412ec(*(undefined4 *)(iVar1 + iVar4 * 4),uVar3,0);
          if (iVar2 != 0) {
            uVar3 = FUN_0044104c(0xffffff);
            FUN_0044140e(iVar2,uVar3,0);
          }
        }
        else {
          FUN_0044129e(*(undefined4 *)(iVar1 + iVar4 * 4),0,0);
          FUN_0044131c(*(undefined4 *)(iVar1 + iVar4 * 4),0,0);
          if (iVar2 != 0) {
            uVar3 = FUN_0044104c(DAT_0054e1a4);
            FUN_0044140e(iVar2,uVar3,0);
          }
        }
        FUN_00441488(*(undefined4 *)(iVar1 + iVar4 * 4),0xff,0);
      }
    }
  }
  return in_r3;
}

