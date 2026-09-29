
undefined4 FUN_00462db6(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 in_r3;
  int iVar5;
  
  if (*DAT_004631f8 != 0) {
    for (iVar5 = 0; iVar1 = DAT_00463200, iVar5 < *DAT_00462f28; iVar5 = iVar5 + 1) {
      if (*(int *)(DAT_00463200 + iVar5 * 4) != 0) {
        iVar2 = FUN_0044dce2(*(undefined4 *)(DAT_00463200 + iVar5 * 4),0);
        iVar3 = FUN_0044dce2(*(undefined4 *)(iVar1 + iVar5 * 4),1);
        if (iVar5 == *DAT_00462f34) {
          FUN_0044129e(*(undefined4 *)(iVar1 + iVar5 * 4),0x32,0);
          if (iVar3 != 0) {
            uVar4 = FUN_0044104c(0xffffff);
            FUN_0044140e(iVar3,uVar4,0);
          }
          if (iVar2 != 0) {
            FUN_004413ce(iVar2,0xff,0);
          }
        }
        else {
          FUN_0044129e(*(undefined4 *)(iVar1 + iVar5 * 4),0,0);
          if (iVar3 != 0) {
            uVar4 = FUN_0044104c(DAT_004631fc);
            FUN_0044140e(iVar3,uVar4,0);
            FUN_0046015a(iVar3,0x100,0);
          }
          if (iVar2 != 0) {
            FUN_004413ce(iVar2,0x20,0);
            FUN_0046015a(iVar2,0x100,0);
          }
        }
        FUN_00441488(*(undefined4 *)(iVar1 + iVar5 * 4),0xff,0);
        FUN_0046015a(*(undefined4 *)(iVar1 + iVar5 * 4),0x100,0);
      }
    }
  }
  return in_r3;
}

