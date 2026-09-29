
undefined8 FUN_0044ce2c(int *param_1,undefined1 param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  uint uVar6;
  
  iVar2 = FUN_0044b7c0(param_1);
  if (iVar2 == 0) {
    iVar2 = *param_1;
    bVar1 = *(byte *)(param_1 + 2);
    for (uVar6 = 0; uVar6 < *(byte *)(param_1 + 2); uVar6 = uVar6 + 1) {
      iVar5 = FUN_0044b844(*(undefined1 *)(iVar2 + (uint)bVar1 * 4 + uVar6),param_2);
      if (iVar5 != 0) {
        uVar4 = 1;
        goto LAB_0044ce88;
      }
    }
  }
  else {
    iVar2 = *param_1;
    for (iVar5 = 0; *(char *)(iVar2 + iVar5 * 8) != '\0'; iVar5 = iVar5 + 1) {
      iVar3 = FUN_0044b844(*(undefined1 *)(iVar2 + iVar5 * 8),param_2);
      if (iVar3 != 0) {
        uVar4 = 1;
        goto LAB_0044ce88;
      }
    }
  }
  uVar4 = 0;
LAB_0044ce88:
  return CONCAT44(param_4,uVar4);
}

