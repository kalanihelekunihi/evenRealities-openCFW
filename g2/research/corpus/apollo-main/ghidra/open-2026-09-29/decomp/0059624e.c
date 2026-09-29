
undefined8 FUN_0059624e(undefined4 param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  short sVar3;
  
  piVar1 = DAT_00596998;
  if (*(char *)((int)DAT_00596998 + 10) != '\0') {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_3 = (uint)*(ushort *)(piVar1 + 2);
      param_1 = 0xae;
      param_2 = DAT_00596a40;
      FUN_0043d574(4,PTR_s_conversate_tag_00596924,PTR_s_D__01_workspace_s200_ap510b_iar__005967b0,
                   DAT_00596a44,0xae,DAT_00596a40,param_3,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_00596a48,DAT_00596a48,(short)piVar1[2],param_1,param_2,
                          param_3);
    }
    if (*piVar1 != 0) {
      iVar2 = *piVar1;
      sVar3 = 0;
      *(undefined4 *)(*(int *)(*piVar1 + 0x18) + 0x14) = 0;
      while (iVar2 != 0) {
        iVar2 = *(int *)(iVar2 + 0x14);
        FUN_00596188();
        sVar3 = sVar3 + 1;
      }
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_1 = 0xc0;
        param_2 = DAT_00596a4c;
        FUN_0043d574(4,PTR_s_conversate_tag_00596924,PTR_s_D__01_workspace_s200_ap510b_iar__005967b0
                     ,DAT_00596a44,0xc0,DAT_00596a4c,sVar3);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_00596a50,DAT_00596a50,sVar3);
      }
    }
    FUN_0043c0e4(piVar1,0xc,0);
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_1 = 0xc6;
      param_2 = DAT_00596a54;
      FUN_0043d574(3,PTR_s_conversate_tag_00596924,PTR_s_D__01_workspace_s200_ap510b_iar__005967b0,
                   DAT_00596a44);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_s__conversate_tag_Tag_storage_dein_00596a58,
                          PTR_s__conversate_tag_Tag_storage_dein_00596a58);
    }
  }
  return CONCAT44(param_2,param_1);
}

