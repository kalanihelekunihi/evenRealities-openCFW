
undefined8 FUN_0045d4dc(undefined4 param_1,undefined4 param_2)

{
  undefined *puVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined *unaff_r6;
  
  if (*DAT_0045dd64 == 0) {
    iVar2 = FUN_0043d0ce();
    puVar1 = PTR_s_sync_module_uninit__0045df18;
    if (iVar2 << 0x1e < 0) {
      unaff_r5 = 0x477;
      FUN_0043d574(2,PTR_s_sync_module_framework_0045d7d0,
                   PTR_s_D__01_workspace_s200_ap510b_iar__0045d7cc,
                   PTR_s_SyncModuleReceivedDataHandler_0045df1c);
      unaff_r6 = puVar1;
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__sync_module_framework_sync_modu_0045dfd0,
                          PTR_s__sync_module_framework_sync_modu_0045dfd0);
    }
  }
  else {
    FUN_00491b9a(*DAT_0045dd64,param_1,param_2);
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

