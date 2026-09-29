
undefined8 FUN_005b3d04(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined *param_4)

{
  int iVar1;
  uint uVar2;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  iVar1 = FUN_0045a568();
  uStack_10 = param_3;
  uStack_c = param_4;
  if (iVar1 != 1) goto LAB_005b3d60;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    uStack_c = PTR_s_Timer_manager_deinitialized_005b3ee0;
    uStack_10 = 0x17e;
    FUN_0043d574(4,DAT_005b3e18,DAT_005b3e14,PTR_s_conversate_timer_mgr_deinit_005b3ee4);
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1f < 0) {
LAB_005b3d3c:
    compress_log_output(0x10000000,PTR_s__conversate_timer_Timer_manager_d_005b3ee8,
                        PTR_s__conversate_timer_Timer_manager_d_005b3ee8);
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1d < 0) goto LAB_005b3d3c;
  }
  for (uVar2 = 1; (int)uVar2 < 4; uVar2 = uVar2 + 1) {
    FUN_005b36be(uVar2 & 0xff,2);
  }
  FUN_005b38cc();
LAB_005b3d60:
  return CONCAT44(uStack_c,uStack_10);
}

