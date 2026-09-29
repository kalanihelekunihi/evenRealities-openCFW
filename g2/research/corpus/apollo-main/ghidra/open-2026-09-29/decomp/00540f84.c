
undefined8 _flashDBErase(uint param_1,uint param_2,undefined *param_3,uint param_4)

{
  int iVar1;
  uint uVar2;
  
  if (((param_1 & 0xfff) == 0) && ((int)param_1 < DAT_0054127c)) {
    uVar2 = param_2;
    if ((param_2 & 0xfff) != 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        uVar2 = 0x69;
        FUN_0043d574(1,DAT_00541268,DAT_00541264,PTR_s__flashDBErase_00541284,0x69,
                     PTR_s_invalid_erase_size_0x_x_0054128c,param_2);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4400000,PTR_s__db_api_invalid_erase_size_0x_x_00541290,
                            PTR_s__db_api_invalid_erase_size_0x_x_00541290,param_2);
      }
      if ((param_2 & 0xfff) == 0) {
        param_2 = param_2 >> 0xc;
      }
      else {
        param_2 = (param_2 >> 0xc) + 1;
      }
      param_2 = param_2 << 0xc;
    }
    for (; param_2 != 0; param_2 = param_2 - 0x1000) {
      iVar1 = FUN_0047075c(param_1);
      if (iVar1 != 0) {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          uVar2 = 0x72;
          FUN_0043d574(1,DAT_00541268,DAT_00541264,PTR_s__flashDBErase_00541284,0x72,
                       PTR_s_Erase_failed_at_address_0x_08lX_00541294,param_1);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x4400000,PTR_s__db_api_Erase_failed_at_address_0_00541298,
                              PTR_s__db_api_Erase_failed_at_address_0_00541298,param_1);
        }
        param_2 = 0;
        break;
      }
      if (param_2 < 0x1001) break;
      param_1 = param_1 + 0x1000;
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    uVar2 = param_2;
    if (iVar1 << 0x1e < 0) {
      uVar2 = 0x62;
      param_3 = PTR_s_Offset_address_0x_08lX_is_not_4K_00541280;
      param_4 = param_1;
      FUN_0043d574(1,DAT_00541268,DAT_00541264,PTR_s__flashDBErase_00541284,0x62,
                   PTR_s_Offset_address_0x_08lX_is_not_4K_00541280,param_1);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4400000,PTR_s__db_api_Offset_address_0x_08lX_i_00541288,
                          PTR_s__db_api_Offset_address_0x_08lX_i_00541288,param_1,uVar2,param_3,
                          param_4);
    }
    param_2 = 0;
  }
  return CONCAT44(uVar2,param_2);
}

