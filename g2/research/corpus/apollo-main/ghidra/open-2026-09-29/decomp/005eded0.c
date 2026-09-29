
undefined4
tracepoint_encode_response(byte *param_1,ushort *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  uint local_40;
  undefined *local_3c;
  uint local_38;
  uint local_34;
  uint local_30;
  undefined1 auStack_2c [12];
  ushort local_20;
  uint local_1c;
  undefined4 uStack_18;
  
  uVar2 = DAT_005ee898;
  uStack_18 = param_4;
  FUN_0043c0e4(DAT_005ee898,0x300,0);
  FUN_004905f4(&local_40,uVar2,0x300);
  FUN_00439c04(auStack_2c,&local_40,0x14);
  iVar1 = FUN_00490c32(auStack_2c,DAT_005ee89c,param_1);
  if (iVar1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_38 = DAT_005ee8a0;
      if (local_1c != 0) {
        local_38 = local_1c;
      }
      local_3c = DAT_005ee8a4;
      local_40 = 0xe4;
      FUN_0043d574(1,DAT_005ee79c,DAT_005ee798,DAT_005ee8a8);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      uVar3 = DAT_005ee8a0;
      if (local_1c != 0) {
        uVar3 = local_1c;
      }
      compress_log_output(0x4400000,DAT_005ee8ac,DAT_005ee8ac,uVar3);
    }
    uVar2 = 0xffffffff;
  }
  else {
    *param_2 = local_20;
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_30 = (uint)*param_2;
      local_34 = (uint)*(ushort *)(param_1 + 2);
      local_38 = (uint)*param_1;
      local_3c = PTR_s_tracepoint_encode_rsp_cmd__d_whi_005ee8b0;
      local_40 = 0xea;
      FUN_0043d574(4,DAT_005ee79c,DAT_005ee798,DAT_005ee8a8);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      local_3c = (undefined *)(uint)*param_2;
      local_40 = (uint)*(ushort *)(param_1 + 2);
      compress_log_output(0x10c00000,DAT_005eeb44,DAT_005eeb44,*param_1);
    }
    uVar2 = 0;
  }
  return uVar2;
}

