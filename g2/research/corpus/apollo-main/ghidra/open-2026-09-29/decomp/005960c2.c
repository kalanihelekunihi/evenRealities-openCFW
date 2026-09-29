
undefined8 FUN_005960c2(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  int iVar2;
  
  iVar1 = file_heap_allocate(0x1c);
  if (iVar1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_3 = 0x65;
      FUN_0043d574(1,PTR_s_conversate_tag_00596924,PTR_s_D__01_workspace_s200_ap510b_iar__005967b0,
                   PTR_s_create_tag_node_0059692c,0x65,
                   PTR_s_Failed_to_allocate_memory_for_ta_00596928);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00596990,DAT_00596990);
    }
    iVar1 = 0;
  }
  else {
    FUN_0043c0e4(iVar1,0x1c,0);
    *(undefined4 *)(iVar1 + 0x14) = 0;
    *(undefined4 *)(iVar1 + 0x18) = 0;
    iVar2 = FUN_00595f4c(param_1,iVar1);
    if (iVar2 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_3 = 0x70;
        FUN_0043d574(1,PTR_s_conversate_tag_00596924,PTR_s_D__01_workspace_s200_ap510b_iar__005967b0
                     ,PTR_s_create_tag_node_0059692c,0x70,DAT_00596994);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_00596a30,DAT_00596a30);
      }
      file_heap_free(iVar1);
      iVar1 = 0;
    }
  }
  return CONCAT44(param_3,iVar1);
}

