
undefined8 FUN_00493fa8(int param_1,int param_2)

{
  byte bVar1;
  int iVar2;
  int iVar3;
  undefined4 unaff_r5;
  
  if (param_1 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      unaff_r5 = 0x156;
      FUN_0043d574(1,DAT_004940c0,DAT_004940bc,DAT_00494830,0x156,DAT_0049482c);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004949b4,DAT_004949b4);
    }
    iVar2 = 0;
  }
  else {
    for (iVar2 = *(int *)(param_1 + 4); iVar2 != 0; iVar2 = *(int *)(iVar2 + 4)) {
      iVar3 = 0;
      bVar1 = *(byte *)(iVar2 + 8);
      if (bVar1 == 0) {
        iVar3 = *(int *)(*(int *)(iVar2 + 0xc) + 0x20);
      }
      else if (bVar1 == 2) {
        iVar3 = *(int *)(*(int *)(iVar2 + 0xc) + 0x10);
      }
      else if (bVar1 < 2) {
        iVar3 = *(int *)(*(int *)(iVar2 + 0xc) + 0x20);
      }
      if (iVar3 == param_2) goto LAB_00494026;
    }
    iVar2 = 0;
  }
LAB_00494026:
  return CONCAT44(unaff_r5,iVar2);
}

