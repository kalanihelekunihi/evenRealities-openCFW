
void event_wait_mask_42e2a2(undefined4 param_1,byte param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  uint uVar2;
  
  uVar2 = 1 << (uint)param_2;
  bl_runtime_transfer(param_1,0x800000);
  uVar1 = bl_runtime_flags_wait(*(undefined4 *)(DAT_0042e46c + 0x1c),uVar2,1,20000);
  if ((uVar2 & uVar1) != uVar2) {
    elog_output(1,DAT_0042e468,DAT_0042e464,PTR_s__thread_sync_0042e478,0x87,
                PTR_s_thread_sync_failed_0x_x__task__d_0042e474,uVar1,param_2,param_4);
  }
  return;
}

