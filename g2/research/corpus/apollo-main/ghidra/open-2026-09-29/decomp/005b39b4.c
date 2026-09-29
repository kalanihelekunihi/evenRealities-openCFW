
undefined8 FUN_005b39b4(undefined4 param_1)

{
  undefined *puVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined *unaff_r6;
  
  if (*DAT_005b3e34 == '\x02' && DAT_005b3e34[0x96] == '\x01') {
    if (*(char *)(DAT_005b3e48 + 8) == '\0') {
      FUN_005b37d8();
    }
    else {
      iVar2 = FUN_005b3628(DAT_005b3e48 + 8,param_1);
      if (iVar2 != 0) {
        iVar2 = FUN_0043d0ce();
        puVar1 = PTR_s_Select_timeout__switch_to_unsele_005b3e8c;
        if (iVar2 << 0x1e < 0) {
          unaff_r5 = 0x11b;
          FUN_0043d574(3,DAT_005b3e18,DAT_005b3e14,PTR_s_conversate_timer_process_select__005b3e90);
          unaff_r6 = puVar1;
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0xc000000,PTR_s__conversate_timer_Select_timeout_005b3e94,
                              PTR_s__conversate_timer_Select_timeout_005b3e94);
        }
        FUN_005b383c();
        FUN_005b02e4(0xd,0);
      }
    }
  }
  else if (*(char *)(DAT_005b3e48 + 8) != '\0') {
    FUN_005b383c();
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

