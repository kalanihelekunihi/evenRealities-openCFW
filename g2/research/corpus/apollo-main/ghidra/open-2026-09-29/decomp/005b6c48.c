
undefined8 FUN_005b6c48(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_00450286();
  if (*(int *)(DAT_005b7604 + 0x24) != 0) {
    FUN_0044e498(*(undefined4 *)(DAT_005b7604 + 0x24));
    uVar2 = FUN_005b6a3a();
    if ((iVar1 == 0xf) || (iVar1 == 0xc)) {
      FUN_005b6b58(uVar2);
    }
    else if (iVar1 == 0xe) {
      FUN_005b6b58(uVar2);
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        param_2 = 0xc2;
        param_3 = DAT_005b7608;
        FUN_0043d574(3,PTR_s_conversate_prep_005b7614,DAT_005b7610,DAT_005b760c,0xc2,DAT_005b7608,
                     uVar2);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0xc400000,PTR_s__conversate_prep_prep_scroll_end_005b7618,
                            PTR_s__conversate_prep_prep_scroll_end_005b7618,uVar2);
      }
    }
  }
  return CONCAT44(param_3,param_2);
}

