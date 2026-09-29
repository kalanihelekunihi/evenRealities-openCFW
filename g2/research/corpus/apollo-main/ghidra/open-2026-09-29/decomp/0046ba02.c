
void SVC_Settings_RequestLeftVersion(void)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  undefined4 in_r3;
  undefined1 local_44 [48];
  undefined4 uStack_14;
  
  uStack_14 = in_r3;
  iVar2 = FUN_0045a568();
  if (((iVar2 == 1) && (*(char *)(DAT_0046bee8 + 0x44) == '\0')) &&
     ((iVar2 = osKernelGetTickCount(), piVar1 = DAT_0046c40c, *DAT_0046c40c == 0 ||
      (499 < (uint)(iVar2 - *DAT_0046c40c))))) {
    FUN_0043c0e4(local_44,0x30,0);
    local_44[0] = 3;
    iVar3 = FUN_00465480(9,local_44,0x30,0,5);
    if (iVar3 == 0) {
      *piVar1 = iVar2;
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(3,DAT_0046bb74,DAT_0046bb70,DAT_0046c510,0xf7,
                     PTR_s_request_left_version_from_slave_0046c518);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc000000,PTR_s__service_settings_request_left_v_0046c650,
                            PTR_s__service_settings_request_left_v_0046c650);
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(2,DAT_0046bb74,DAT_0046bb70,DAT_0046c510,0xf3,DAT_0046c50c,iVar3);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_0046c514,DAT_0046c514,iVar3);
      }
    }
  }
  return;
}

