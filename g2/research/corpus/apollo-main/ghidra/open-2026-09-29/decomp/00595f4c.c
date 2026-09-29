
undefined4
FUN_00595f4c(undefined1 *param_1,undefined1 *param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  
  FUN_0043c0e4(param_2,0x14,0,param_4,param_1,param_2,param_3,param_4);
  *param_2 = *param_1;
  *(undefined4 *)(param_2 + 0x10) = *(undefined4 *)(param_1 + 0x488);
  if (*(short *)(param_1 + 2) == 0) {
    *(undefined4 *)(param_2 + 4) = 0;
    *(undefined2 *)(param_2 + 0xc) = 0;
  }
  else {
    *(undefined2 *)(param_2 + 0xc) = *(undefined2 *)(param_1 + 2);
    uVar1 = file_heap_allocate(*(ushort *)(param_2 + 0xc) + 1);
    *(undefined4 *)(param_2 + 4) = uVar1;
    if (*(int *)(param_2 + 4) == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,PTR_s_conversate_tag_00596924,PTR_s_D__01_workspace_s200_ap510b_iar__005967b0
                     ,DAT_005967ac,0x24,DAT_005967a8,*(ushort *)(param_2 + 0xc) + 1);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4400000,PTR_s__conversate_tag_Failed_to_alloca_005967b4,
                            PTR_s__conversate_tag_Failed_to_alloca_005967b4,
                            *(ushort *)(param_2 + 0xc) + 1);
      }
      return 0;
    }
    FUN_00439be4(*(undefined4 *)(param_2 + 4),param_1 + 4,*(undefined2 *)(param_2 + 0xc));
    *(undefined1 *)(*(int *)(param_2 + 4) + (uint)*(ushort *)(param_2 + 0xc)) = 0;
  }
  if (*(short *)(param_1 + 0x84) == 0) {
    *(undefined4 *)(param_2 + 8) = 0;
    *(undefined2 *)(param_2 + 0xe) = 0;
  }
  else {
    *(undefined2 *)(param_2 + 0xe) = *(undefined2 *)(param_1 + 0x84);
    uVar1 = file_heap_allocate(*(ushort *)(param_2 + 0xe) + 1);
    *(undefined4 *)(param_2 + 8) = uVar1;
    if (*(int *)(param_2 + 8) == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,PTR_s_conversate_tag_00596924,PTR_s_D__01_workspace_s200_ap510b_iar__005967b0
                     ,DAT_005967ac,0x34,PTR_s_Failed_to_allocate_memory_for_ta_005967b8,
                     *(ushort *)(param_2 + 0xe) + 1);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_00596a2c,DAT_00596a2c,*(ushort *)(param_2 + 0xe) + 1);
      }
      if (*(int *)(param_2 + 4) != 0) {
        file_heap_free(*(undefined4 *)(param_2 + 4));
        *(undefined4 *)(param_2 + 4) = 0;
      }
      return 0;
    }
    FUN_00439be4(*(undefined4 *)(param_2 + 8),param_1 + 0x86,*(undefined2 *)(param_2 + 0xe));
    *(undefined1 *)(*(int *)(param_2 + 8) + (uint)*(ushort *)(param_2 + 0xe)) = 0;
  }
  return 1;
}

