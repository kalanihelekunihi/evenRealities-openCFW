
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void hub_thread_entry(void)

{
  int iVar1;
  
  hub_state_enter();
  HUB_ResourceInit();
  HUB_IMUCalibParaInit();
  hub_role_init();
  iVar1 = productModeGet();
  if (iVar1 == 1) {
    hub_msg_send_id1(4);
    als_function_25();
  }
  else {
    iVar1 = hub_role_get();
    if (iVar1 == 3) {
      SVC_Settings_HeadUpConfig();
    }
    else {
      semantic_sensor_reset_line();
    }
  }
  hub_state_exit();
  do {
    while (iVar1 = osMessageQueueGet(*(undefined4 *)(DAT_004a6ecc + 0xc),&stack0xfffffff0,0,
                                     0xffffffff), iVar1 != 0) {
      *_DAT_004a7348 = *_DAT_004a7348 + 1;
    }
    task_vote_acquire_current();
    HUB_MessageProcesser(&stack0xfffffff0);
    task_vote_release_current();
  } while( true );
}

