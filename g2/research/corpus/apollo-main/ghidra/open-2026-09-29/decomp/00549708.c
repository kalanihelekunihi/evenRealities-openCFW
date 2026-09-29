
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_00549708(undefined4 param_1,undefined4 param_2,undefined *param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 uVar5;
  
  iVar4 = _DAT_00549bb8;
  if (*(char *)(_DAT_00549bb8 + 0x18c) == '\x01') {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_2 = 0x7b2;
      param_3 = PTR_s_rle_decompress_mini_map_data_00549bbc;
      FUN_0043d574(4,PTR_s_navigation_ui_00549bc8,PTR_s_D__01_workspace_s200_ap510b_iar__00549bc4,
                   PTR_s_store_mini_map_data_00549bc0,0x7b2,
                   PTR_s_rle_decompress_mini_map_data_00549bbc,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__navigation_ui_rle_decompress_mi_00549bcc,
                          PTR_s__navigation_ui_rle_decompress_mi_00549bcc);
    }
    uVar3 = _DAT_00549bd0;
    uVar5 = 18000;
    FUN_0043c0e4(_DAT_00549bd0,18000,0);
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_2 = 0x7b4;
      param_3 = PTR_s_mini_map_size____d_00549bd4;
      FUN_0043d574(4,PTR_s_navigation_ui_00549bc8,PTR_s_D__01_workspace_s200_ap510b_iar__00549bc4,
                   PTR_s_store_mini_map_data_00549bc0,0x7b4,PTR_s_mini_map_size____d_00549bd4,
                   *(undefined4 *)(iVar4 + 400));
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__navigation_ui_mini_map_size_____00549bd8,
                          PTR_s__navigation_ui_mini_map_size_____00549bd8,
                          *(undefined4 *)(iVar4 + 400));
    }
    puVar1 = _DAT_00549bb0;
    if (*(int *)(iVar4 + 0x194) == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_2 = 0x7b6;
        param_3 = PTR_s_mini_map_compress_mode_is_0__no_c_00549bdc;
        FUN_0043d574(4,PTR_s_navigation_ui_00549bc8,PTR_s_D__01_workspace_s200_ap510b_iar__00549bc4,
                     PTR_s_store_mini_map_data_00549bc0);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10000000,PTR_s__navigation_ui_mini_map_compress_00549be0,
                            PTR_s__navigation_ui_mini_map_compress_00549be0);
      }
      puVar1 = _DAT_00549bb0;
      osMutexAcquire(*_DAT_00549bb0,0xffffffff);
      if (*(uint *)(iVar4 + 400) < 18000) {
        uVar5 = *(undefined4 *)(iVar4 + 400);
      }
      FUN_00439be4(uVar3,iVar4 + 0x19c,uVar5);
      osMutexRelease(*puVar1);
    }
    else if (*(int *)(iVar4 + 0x194) == 1) {
      osMutexAcquire(*_DAT_00549bb0,0xffffffff);
      uVar3 = func_0x004e0c34(iVar4 + 0x19c,*(undefined4 *)(iVar4 + 400),uVar3,18000);
      osMutexRelease(*puVar1);
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        param_2 = 0x7bf;
        param_3 = PTR_s_rle_decompress_mini_map_data_len_00549be4;
        FUN_0043d574(4,PTR_s_navigation_ui_00549bc8,PTR_s_D__01_workspace_s200_ap510b_iar__00549bc4,
                     PTR_s_store_mini_map_data_00549bc0,0x7bf,
                     PTR_s_rle_decompress_mini_map_data_len_00549be4,uVar3);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x10400000,PTR_s__navigation_ui_rle_decompress_mi_00549be8,
                            PTR_s__navigation_ui_rle_decompress_mi_00549be8,uVar3);
      }
    }
    else if (*(int *)(iVar4 + 0x194) == 2) {
      osMutexAcquire(*_DAT_00549bb0,0xffffffff);
      uVar3 = func_0x004e0c0c(iVar4 + 0x19c,*(undefined4 *)(iVar4 + 400),uVar3,18000);
      osMutexRelease(*puVar1);
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        param_2 = 0x7c4;
        param_3 = PTR_s_lz4_decompress_mini_map_data_len_00549bec;
        FUN_0043d574(4,PTR_s_navigation_ui_00549bc8,PTR_s_D__01_workspace_s200_ap510b_iar__00549bc4,
                     PTR_s_store_mini_map_data_00549bc0,0x7c4,
                     PTR_s_lz4_decompress_mini_map_data_len_00549bec,uVar3);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x10400000,PTR_s__navigation_ui_lz4_decompress_mi_00549bf0,
                            PTR_s__navigation_ui_lz4_decompress_mi_00549bf0,uVar3);
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_2 = 0x7c6;
        param_3 = PTR_s_unsupported_mini_map_compress_mo_00549bf4;
        FUN_0043d574(2,PTR_s_navigation_ui_00549bc8,PTR_s_D__01_workspace_s200_ap510b_iar__00549bc4,
                     PTR_s_store_mini_map_data_00549bc0,0x7c6,
                     PTR_s_unsupported_mini_map_compress_mo_00549bf4,*(undefined4 *)(iVar4 + 0x194))
        ;
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8400000,PTR_s__navigation_ui_unsupported_mini_m_00549bf8,
                            PTR_s__navigation_ui_unsupported_mini_m_00549bf8,
                            *(undefined4 *)(iVar4 + 0x194));
      }
    }
  }
  return CONCAT44(param_3,param_2);
}

