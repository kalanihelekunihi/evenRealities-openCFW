
undefined8 FUN_00494030(int param_1,undefined4 *param_2)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 unaff_r5;
  
  if ((param_1 == 0) || (param_2 == (undefined4 *)0x0)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      unaff_r5 = 0x1a6;
      FUN_0043d574(1,DAT_004940c0,DAT_004940bc,DAT_004949bc,0x1a6,DAT_004949b8);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00494a74,DAT_00494a74);
    }
    uVar2 = 0xffffffff;
  }
  else {
    *param_2 = 0;
    param_2[1] = 0;
    if (*(int *)(param_1 + 4) == 0) {
      *(undefined4 **)(param_1 + 4) = param_2;
      *(undefined4 **)(param_1 + 8) = param_2;
    }
    else {
      *param_2 = *(undefined4 *)(param_1 + 8);
      *(undefined4 **)(*(int *)(param_1 + 8) + 4) = param_2;
      *(undefined4 **)(param_1 + 8) = param_2;
    }
    *(int *)(param_1 + 0xc) = *(int *)(param_1 + 0xc) + 1;
    uVar2 = 0;
  }
  return CONCAT44(unaff_r5,uVar2);
}

