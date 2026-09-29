
undefined8 FUN_0059619e(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  int iVar2;
  
  puVar1 = DAT_00596998;
  if (*(char *)((int)DAT_00596998 + 10) == '\0') {
    FUN_0043c0e4(DAT_00596998,0xc,0,param_4,param_2,param_3,param_4);
    *puVar1 = 0;
    *(undefined2 *)(puVar1 + 2) = 0;
    *(undefined1 *)((int)puVar1 + 10) = 1;
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_2 = 0x9e;
      FUN_0043d574(3,PTR_s_conversate_tag_00596924,PTR_s_D__01_workspace_s200_ap510b_iar__005967b0,
                   DAT_005969a0,0x9e,DAT_00596a38);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc000000,DAT_00596a3c);
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_2 = 0x93;
      FUN_0043d574(2,PTR_s_conversate_tag_00596924,PTR_s_D__01_workspace_s200_ap510b_iar__005967b0,
                   DAT_005969a0,0x93,DAT_0059699c);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_00596a34,DAT_00596a34);
    }
  }
  return CONCAT44(param_2,1);
}

