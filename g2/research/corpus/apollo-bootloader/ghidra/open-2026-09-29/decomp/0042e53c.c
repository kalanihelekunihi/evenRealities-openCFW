
undefined8
event_runtime_init_42e53c
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  undefined4 local_10;
  undefined4 local_c;
  
  piVar1 = DAT_0042e838;
  local_10 = param_3;
  local_c = param_4;
  if (*DAT_0042e838 == 0) {
    iVar2 = bl_runtime_queue_create(0xf,8,DAT_0042e83c);
    *piVar1 = iVar2;
    if (*piVar1 == 0) {
      local_c = DAT_0042e840;
      local_10 = 0x58;
      elog_output(1,DAT_0042e84c,DAT_0042e848,DAT_0042e844);
    }
  }
  piVar1 = DAT_0042e850;
  if (*DAT_0042e850 == 0) {
    iVar2 = bl_runtime_register(0x42e6f5,0,0,DAT_0042e854);
    *piVar1 = iVar2;
    if (*piVar1 == 0) {
      local_c = DAT_0042e858;
      local_10 = 0x61;
      elog_output(1,DAT_0042e84c,DAT_0042e848,DAT_0042e844);
    }
  }
  piVar1 = DAT_0042e85c;
  if (*DAT_0042e85c == 0) {
    iVar2 = bl_runtime_flags_create(DAT_0042e860);
    *piVar1 = iVar2;
    if (*piVar1 == 0) {
      local_c = DAT_0042e864;
      local_10 = 0x6a;
      elog_output(1,DAT_0042e84c,DAT_0042e848,DAT_0042e844);
    }
  }
  piVar1 = DAT_0042e868;
  if (*DAT_0042e868 != 0) {
    bl_runtime_action(*DAT_0042e868);
    *piVar1 = 0;
  }
  if (*piVar1 == 0) {
    iVar2 = bl_runtime_dispatch(0x42e645,0,DAT_0042e86c);
    *piVar1 = iVar2;
    if (*piVar1 == 0) {
      local_c = DAT_0042e870;
      local_10 = 0x79;
      elog_output(1,DAT_0042e84c,DAT_0042e848,DAT_0042e844);
    }
  }
  return CONCAT44(local_c,local_10);
}

