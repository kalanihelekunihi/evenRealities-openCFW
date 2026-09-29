
undefined8
runtime_context_publish_42dca2
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  
  iVar1 = DAT_0042e158;
  if (*(int *)(DAT_0042e158 + 0xc) == 0) {
    param_2 = 0x164;
    elog_output(1,DAT_0042e118,DAT_0042e114,PTR_s_dfu_task_msg_send_0042e160,0x164,
                PTR_s_dfu_task_msg_send_queue_null_0042e15c);
    uVar2 = 0;
  }
  else {
    iVar3 = FUN_004168a2(*(undefined4 *)(DAT_0042e158 + 0xc),param_1,0,0,param_2,param_3,param_4);
    if (iVar3 == 0) {
      bl_runtime_transfer(*(undefined4 *)(iVar1 + 8),0x400000);
    }
    else {
      param_2 = 0x169;
      elog_output(1,DAT_0042e118,DAT_0042e114,PTR_s_dfu_task_msg_send_0042e160,0x169,
                  PTR_s_msg_missed_0042e164);
    }
    uVar2 = (uint)(iVar3 == 0);
  }
  return CONCAT44(param_2,uVar2);
}

