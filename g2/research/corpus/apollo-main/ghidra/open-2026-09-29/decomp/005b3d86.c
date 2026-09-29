
undefined8 FUN_005b3d86(uint param_1,undefined *param_2)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  uint uVar4;
  undefined *puVar5;
  
  uVar4 = param_1;
  puVar5 = param_2;
  iVar1 = FUN_0045a568();
  if ((iVar1 == 1) && (iVar1 = FUN_005b3718(param_1 & 0xff,(uint)param_2 & 0xff), iVar1 == 0)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar2 = FUN_005b16dc((uint)param_2 & 0xff);
      uVar3 = FUN_005b16dc(param_1 & 0xff);
      uVar4 = 0x199;
      puVar5 = PTR_s_No_timer_rule_found_for_state_tr_005b3eec;
      FUN_0043d574(4,DAT_005b3e18,DAT_005b3e14,PTR_s_conversate_timer_mgr_handle_stat_005b3ef0,0x199
                   ,PTR_s_No_timer_rule_found_for_state_tr_005b3eec,uVar3,uVar2);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      uVar4 = FUN_005b16dc((uint)param_2 & 0xff);
      uVar2 = FUN_005b16dc(param_1 & 0xff);
      compress_log_output(0x10800000,PTR_s__conversate_timer_No_timer_rule_f_005b3ef4,
                          PTR_s__conversate_timer_No_timer_rule_f_005b3ef4,uVar2);
    }
  }
  return CONCAT44(puVar5,uVar4);
}

