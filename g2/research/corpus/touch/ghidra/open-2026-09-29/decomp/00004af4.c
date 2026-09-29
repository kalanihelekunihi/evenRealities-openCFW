
uint touch_application_17f4_run
               (undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;
  
  *(uint *)(param_1[1] + 8) = *(uint *)(param_1[1] + 8) | 0x8000;
  iVar6 = param_1[2];
  *(undefined1 *)(iVar6 + 0x76) = 0;
  event_dispatcher(1,param_1,iVar6,0x76,param_4);
  uVar1 = touch_application_17be_preflight(param_1);
  if (uVar1 == 0) {
    uVar2 = touch_sub_29a2(param_1);
    uVar3 = touch_sub_48b8(param_1);
    uVar1 = touch_terminal_297a_conditional_call(param_1);
    uVar1 = uVar2 | uVar3 | uVar1;
    uVar4 = __aeabi_uidiv(*(undefined4 *)*param_1,DAT_00004ba4);
    iVar6 = pdl_timeout_count_scale(DAT_00004ba4,uVar4,5);
    while (iVar5 = touch_state_298e_status80(param_1), iVar5 != 0) {
      if (iVar6 == 0) {
        uVar1 = 4;
        break;
      }
      iVar6 = iVar6 + -1;
    }
    *(undefined1 *)(param_1[2] + 0x76) = 1;
    event_dispatcher(1,param_1);
    for (uVar2 = 0; uVar2 < 3; uVar2 = uVar2 + 1) {
      touch_state_2902_cap_enabled_object(uVar2,param_1);
    }
  }
  touch_application_1c54_update_three(param_1);
  touch_pipeline_1b1c_reset_three(param_1);
  *(uint *)(param_1[1] + 8) = *(uint *)(param_1[1] + 8) & DAT_00004ba0;
  return uVar1;
}

