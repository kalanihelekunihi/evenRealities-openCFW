
undefined8 FUN_00494834(int param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  undefined4 uVar2;
  
  if (param_1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_3 = 0x2ec;
      FUN_0043d574(1,PTR_s_evenhub_ui_00494b84,DAT_00494b80,
                   PTR_s_evenhub_ui_create_root_container_00494bdc,0x2ec,
                   PTR_s_evenhub_ui_create_root_container_00494bd8);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__evenhub_ui_evenhub_ui_create_ro_00494be0,
                          PTR_s__evenhub_ui_evenhub_ui_create_ro_00494be0);
    }
    iVar1 = 0;
  }
  else {
    iVar1 = FUN_0043de82();
    if (iVar1 == 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        param_3 = 0x2f1;
        FUN_0043d574(1,PTR_s_evenhub_ui_00494b84,DAT_00494b80,
                     PTR_s_evenhub_ui_create_root_container_00494bdc,0x2f1,
                     PTR_s_evenhub_ui_create_root_container_00494be4);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4000000,PTR_s__evenhub_ui_evenhub_ui_create_ro_004954c4);
      }
      iVar1 = 0;
    }
    else {
      FUN_0043dfa4(iVar1,0x10);
      FUN_0043f506(iVar1,0x240);
      FUN_0043f568(iVar1,0x120);
      FUN_0043f09a(iVar1,0,0);
      FUN_0043dfa4(iVar1,0x10);
      uVar2 = FUN_0044104c(0);
      FUN_0044127e(iVar1,uVar2,0);
      FUN_0044129e(iVar1,0xff,0);
      uVar2 = FUN_0044104c(0xffffff);
      FUN_0044140e(iVar1,uVar2,0);
      FUN_0044142e(iVar1,0xff,0);
      uVar2 = FUN_0044104c(0);
      FUN_004412ec(iVar1,uVar2,0);
      FUN_0044131c(iVar1,0,0);
      FUN_0044133a(iVar1,0,0);
      FUN_00441378(iVar1,0,0);
      FUN_00441386(iVar1,0,0);
      FUN_004413b0(iVar1,0,0);
      FUN_0044146a(iVar1,0,0);
      FUN_004935cc(iVar1,0,0);
      FUN_0044120e(iVar1,0,0);
      FUN_0044121c(iVar1,0,0);
      FUN_0044122a(iVar1,0,0);
      FUN_00441238(iVar1,0,0);
    }
  }
  return CONCAT44(param_3,iVar1);
}

