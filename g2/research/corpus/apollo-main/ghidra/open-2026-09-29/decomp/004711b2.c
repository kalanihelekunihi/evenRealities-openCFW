
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_004711b2(uint param_1,undefined *param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  if (param_1 < 8) {
    *DAT_00471ac4 = param_1;
    uVar2 = 0;
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_4 = 0;
      param_2 = PTR_s_set_general_configure_language__l_00471ad4;
      param_3 = param_1;
      FUN_0043d574(2,DAT_00471ae0,DAT_00471adc,PTR_s_set_general_configure_language_00471ad8,0x55,
                   PTR_s_set_general_configure_language__l_00471ad4,param_1,0);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8800000,_DAT_00471ae4,_DAT_00471ae4,param_1,0,param_2,param_3,param_4);
    }
    uVar2 = 0xffffffff;
  }
  return uVar2;
}

