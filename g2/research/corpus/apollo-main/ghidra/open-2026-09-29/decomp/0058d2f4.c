
undefined4 FUN_0058d2f4(undefined4 param_1,undefined4 *param_2)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  
  if (param_2 == (undefined4 *)0x0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_teleprompt_fsm_0058d504,PTR_s_D__01_workspace_s200_ap510b_iar__0058d500,
                   PTR_s_teleprompt_action_heartbeat_0058d4fc,0x186,PTR_s_heartbeat_is_NULL_0058d4f8
                  );
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__teleprompt_fsm_heartbeat_is_NUL_0058d508);
    }
    uVar3 = 0xffffffff;
  }
  else {
    cVar1 = FUN_005540b2();
    if ((cVar1 == '\0') || (cVar1 == '\x03')) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        uVar3 = FUN_005540bc(cVar1);
        FUN_0043d574(2,PTR_s_teleprompt_fsm_0058d504,PTR_s_D__01_workspace_s200_ap510b_iar__0058d500
                     ,PTR_s_teleprompt_action_heartbeat_0058d4fc,0x18c,
                     PTR_s_recv_heartbeat__teleprompt_ui_st_0058d50c,cVar1,uVar3);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        uVar3 = FUN_005540bc(cVar1);
        compress_log_output(0x8800000,PTR_s__teleprompt_fsm_recv_heartbeat__t_0058d510,
                            PTR_s__teleprompt_fsm_recv_heartbeat__t_0058d510,cVar1,uVar3);
      }
      uVar3 = 0xffffffff;
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(3,PTR_s_teleprompt_fsm_0058d504,PTR_s_D__01_workspace_s200_ap510b_iar__0058d500
                     ,PTR_s_teleprompt_action_heartbeat_0058d4fc,400,
                     PTR_s_heartbeat_recv__app_page_id__d__a_0058d514,*param_2,param_2[1],param_2[2]
                     ,param_2[3]);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xd000000,PTR_s__teleprompt_fsm_heartbeat_recv__a_0058d518,
                            PTR_s__teleprompt_fsm_heartbeat_recv__a_0058d518,*param_2,param_2[1],
                            param_2[2],param_2[3]);
      }
      uVar3 = 0;
    }
  }
  return uVar3;
}

