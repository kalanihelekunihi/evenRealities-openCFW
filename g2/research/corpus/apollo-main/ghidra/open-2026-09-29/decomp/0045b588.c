
undefined4
FUN_0045b588(undefined4 param_1,undefined2 *param_2,undefined4 param_3,undefined4 param_4)

{
  ushort uVar1;
  int iVar2;
  ushort *puVar3;
  undefined4 local_38;
  undefined4 local_34;
  uint local_30;
  undefined1 *local_2c;
  undefined2 local_28;
  undefined4 uStack_1c;
  
  puVar3 = *(ushort **)(param_2 + 4);
  uStack_1c = param_4;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    local_30 = (uint)(ushort)param_2[6];
    local_34 = DAT_0045bf74;
    local_38 = 0x20b;
    FUN_0043d574(4,PTR_s_sync_module_framework_0045bc88,DAT_0045bc84,DAT_0045bf78);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_0045bf7c,DAT_0045bf7c,param_2[6]);
  }
  if (*puVar3 >> 8 == 9) {
    uVar1 = puVar3[1];
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_30 = (uint)uVar1;
      local_34 = DAT_0045bf80;
      local_38 = 0x20f;
      FUN_0043d574(4,PTR_s_sync_module_framework_0045bc88,DAT_0045bc84,DAT_0045bf78);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_0045bf84,DAT_0045bf84,uVar1);
    }
    FUN_0043c0e4(&local_34,0x18,0);
    local_38 = CONCAT31(local_38._1_3_,10);
    local_28 = 1;
    local_34 = CONCAT22(local_34._2_2_,*param_2);
    for (iVar2 = 0; iVar2 < (int)(uint)(ushort)param_2[6]; iVar2 = iVar2 + 1) {
    }
    local_2c = (undefined1 *)&local_38;
    FUN_0049225a(param_1,&local_34);
    FUN_0045a72c(uVar1,puVar3 + 4,puVar3[3],puVar3[2]);
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_30 = (uint)*puVar3;
      local_34 = DAT_0045bbf0;
      local_38 = 0x21e;
      FUN_0043d574(2,PTR_s_sync_module_framework_0045bc88,DAT_0045bc84,DAT_0045bf78);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8400000,PTR_s__sync_module_framework_unknown_c_0045bc78,
                          PTR_s__sync_module_framework_unknown_c_0045bc78,*puVar3);
    }
  }
  return 1;
}

