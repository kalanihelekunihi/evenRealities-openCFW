
undefined4 FUN_00596360(int param_1)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  undefined *puVar5;
  
  piVar1 = DAT_00596998;
  if (param_1 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_conversate_tag_00596924,PTR_s_D__01_workspace_s200_ap510b_iar__005967b0,
                   PTR_s_conversate_tag_add_00596a60,0xd3,PTR_s_Tag_data_is_NULL_00596a5c);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__conversate_tag_Tag_data_is_NULL_00596a64,
                          PTR_s__conversate_tag_Tag_data_is_NULL_00596a64);
    }
    uVar3 = 0;
  }
  else if (*(char *)((int)DAT_00596998 + 10) == '\0') {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_conversate_tag_00596924,PTR_s_D__01_workspace_s200_ap510b_iar__005967b0,
                   PTR_s_conversate_tag_add_00596a60,0xd8,DAT_00596a68);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__conversate_tag_Storage_not_init_00596a6c);
    }
    uVar3 = 0;
  }
  else {
    iVar2 = FUN_005960c2();
    if (iVar2 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,PTR_s_conversate_tag_00596924,PTR_s_D__01_workspace_s200_ap510b_iar__005967b0
                     ,PTR_s_conversate_tag_add_00596a60,0xdf,
                     PTR_s_Failed_to_create_new_tag_node_00596a70);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,PTR_s__conversate_tag_Failed_to_create_00596a74,
                            PTR_s__conversate_tag_Failed_to_create_00596a74);
      }
      uVar3 = 0;
    }
    else {
      if (*piVar1 == 0) {
        *(int *)(iVar2 + 0x14) = iVar2;
        *(int *)(iVar2 + 0x18) = iVar2;
        *piVar1 = iVar2;
      }
      else {
        iVar4 = *(int *)(*piVar1 + 0x18);
        *(int *)(iVar2 + 0x14) = *piVar1;
        *(int *)(iVar2 + 0x18) = iVar4;
        *(int *)(*piVar1 + 0x18) = iVar2;
        *(int *)(iVar4 + 0x14) = iVar2;
        *piVar1 = iVar2;
      }
      *(short *)(piVar1 + 2) = (short)piVar1[2] + 1;
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        puVar5 = PTR_DAT_00596a78;
        if (*(int *)(iVar2 + 4) != 0) {
          puVar5 = *(undefined **)(iVar2 + 4);
        }
        FUN_0043d574(4,PTR_s_conversate_tag_00596924,PTR_s_D__01_workspace_s200_ap510b_iar__005967b0
                     ,PTR_s_conversate_tag_add_00596a60,0xf7,
                     PTR_s_Added_tag_text___s__at_head__tot_00596a7c,puVar5,(short)piVar1[2]);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        puVar5 = PTR_DAT_00596a78;
        if (*(int *)(iVar2 + 4) != 0) {
          puVar5 = *(undefined **)(iVar2 + 4);
        }
        compress_log_output(0x10800000,PTR_s__conversate_tag_Added_tag_text____00596a80,
                            PTR_s__conversate_tag_Added_tag_text____00596a80,puVar5,(short)piVar1[2]
                           );
      }
      uVar3 = 1;
    }
  }
  return uVar3;
}

