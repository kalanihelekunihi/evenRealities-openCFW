
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00496430(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined *puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(4,DAT_004964e8,DAT_0049651c,PTR_s_evenhub_ui_create_timeout_exit_p_00496534,0x5b9,
                 PTR_s_navigation_ui_create_break_exit__00496530,param_4);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10000000,PTR_s__evenhub_ui_navigation_ui_create_00496538,
                        PTR_s__evenhub_ui_navigation_ui_create_00496538);
  }
  uVar3 = FUN_00499416(param_1);
  FUN_0043f506(uVar3,0x3fffffff);
  FUN_0043f568(uVar3,0x3fffffff);
  FUN_0043f6ac(uVar3,9);
  puVar1 = PTR_s_ID_GENERAL_BLUETOOTH_DISCONNECT_0049653c;
  uVar4 = FUN_00460084(PTR_s_ID_GENERAL_BLUETOOTH_DISCONNECT_0049653c);
  uVar4 = FUN_0045fffe(puVar1,uVar4);
  FUN_0049942e(uVar3,uVar4);
  FUN_0044143e(uVar3,*_DAT_00496540,0);
  uVar4 = FUN_0044104c(0xffffff);
  FUN_0044140e(uVar3,uVar4,0);
  return;
}

