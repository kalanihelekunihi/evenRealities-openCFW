
void event_service_loop_42e2f8(void)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  undefined4 local_60;
  undefined *local_5c;
  undefined4 local_38 [10];
  
  iVar3 = 0;
  event_flags_init_42e254();
  noop_callback_0042e276();
  event_runtime_setup_42e278();
  event_wait_one_wrapper_42e2ea();
  iVar1 = retained_state_probe_42e224();
  if (iVar1 == 0) {
    local_5c = PTR_s_DO_NOT_need_updata_firmware__GO_T_0042e484;
    local_60 = 0xd8;
    elog_output(3,DAT_0042e468,DAT_0042e464,PTR_s_thread_manager_0042e480);
    memset_wrapper_426c10(&local_60,0,0x28);
    local_60 = 0;
    runtime_context_publish_42dca2(&local_60);
  }
  else {
    local_5c = PTR_s_need_updata_firmware_0042e47c;
    local_60 = 0xd1;
    elog_output(3,DAT_0042e468,DAT_0042e464,PTR_s_thread_manager_0042e480);
    memset_wrapper_426c10(local_38,0,0x28);
    local_38[0] = 1;
    runtime_context_publish_42dca2(local_38);
  }
  do {
    while( true ) {
      uVar2 = bl_runtime_wait(0xffffff,0,60000);
      iVar1 = FUN_004160e8();
      if ((uVar2 == 0) || (0x7fffffff < uVar2)) break;
      noop_callback_0042e39a(uVar2);
    }
    if (59999 < (uint)(iVar1 - iVar3)) {
      iVar3 = iVar1;
    }
  } while( true );
}

