
undefined8 FUN_00420a08(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  if (*DAT_00421010 == 0) {
    iVar1 = 2;
  }
  else if ((param_1 & 0xfff) == 0) {
    if (param_1 < 0x2000000) {
      FUN_0041ff08();
      FUN_00420f10();
      iVar1 = FUN_004207f4();
      if (iVar1 == 0) {
        iVar1 = FUN_00420984();
        if (iVar1 == 0) {
          param_2 = 0;
          iVar1 = FUN_0042069e(0x20,param_1,1,0,0,param_3);
          if (iVar1 == 0) {
            iVar1 = FUN_004207f4();
            if (iVar1 == 0) {
              iVar1 = FUN_004209c4();
              if (iVar1 != 0) {
                FUN_00415fae(PTR_s_SE_write_disable_failed__addr_0x_00421054,param_1,iVar1);
              }
            }
            else {
              FUN_00415fae(PTR_s_SE_wait_idle_after_erase__timeou_00421050,param_1);
              iVar1 = 4;
            }
          }
          else {
            FUN_00415fae(PTR_s_SE_erase_command_failed__addr_0x_0042104c,param_1,iVar1);
          }
        }
        else {
          FUN_00415fae(PTR_s_SE_write_enable_failed__addr_0x__00421048,param_1,iVar1);
        }
      }
      else {
        FUN_00415fae(PTR_s_SE_wait_idle_before_WREN__timeou_00421044,param_1);
        iVar1 = 3;
      }
      FUN_00420e8c();
      FUN_0041ff1e();
    }
    else {
      iVar1 = 5;
    }
  }
  else {
    param_2 = 0x40e;
    elog_output(2,DAT_00420adc,DAT_00421030,PTR_s_mx25u25643g_sector_erase_00421040,0x40e,
                PTR_s_Error__Address_must_be_4KB_align_0042103c,param_4);
    iVar1 = 6;
  }
  return CONCAT44(param_2,iVar1);
}

