
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_00549994(undefined4 param_1,undefined4 param_2,undefined *param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 uVar5;
  
  uVar3 = _DAT_00549bfc;
  iVar4 = _DAT_00549bb8;
  if (*(char *)(_DAT_00549bb8 + 0x47ed) == '\x01') {
    uVar5 = 60000;
    FUN_0043c0e4(_DAT_00549bfc,60000,0);
    puVar1 = _DAT_00549bb0;
    if (*(int *)(iVar4 + 0x47f4) == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_2 = 2000;
        param_3 = PTR_s_max_map_compress_mode_is_0__no_c_00549c00;
        FUN_0043d574(4,PTR_s_navigation_ui_00549bc8,PTR_s_D__01_workspace_s200_ap510b_iar__00549bc4,
                     PTR_s_store_max_map_data_00549c04);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10000000,PTR_s__navigation_ui_max_map_compress_m_00549c08,
                            PTR_s__navigation_ui_max_map_compress_m_00549c08);
      }
      puVar1 = _DAT_00549bb0;
      osMutexAcquire(*_DAT_00549bb0,0xffffffff);
      if (*(uint *)(iVar4 + 0x47f0) < 60000) {
        uVar5 = *(undefined4 *)(iVar4 + 0x47f0);
      }
      FUN_00439be4(uVar3,iVar4 + 0x47f8,uVar5);
      osMutexRelease(*puVar1);
    }
    else if (*(int *)(iVar4 + 0x47f4) == 1) {
      osMutexAcquire(*_DAT_00549bb0,0xffffffff);
      uVar3 = func_0x004e0c34(iVar4 + 0x47f8,*(undefined4 *)(iVar4 + 0x47f0),uVar3,60000);
      osMutexRelease(*puVar1);
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        param_2 = 0x7d9;
        param_3 = PTR_s_rle_decompress_max_map_data_len___00549c0c;
        FUN_0043d574(4,PTR_s_navigation_ui_00549bc8,PTR_s_D__01_workspace_s200_ap510b_iar__00549bc4,
                     PTR_s_store_max_map_data_00549c04,0x7d9,
                     PTR_s_rle_decompress_max_map_data_len___00549c0c,uVar3);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x10400000,PTR_s__navigation_ui_rle_decompress_ma_00549c10,
                            PTR_s__navigation_ui_rle_decompress_ma_00549c10,uVar3);
      }
    }
    else if (*(int *)(iVar4 + 0x47f4) == 2) {
      osMutexAcquire(*_DAT_00549bb0,0xffffffff);
      uVar3 = func_0x004e0c0c(iVar4 + 0x47f8,*(undefined4 *)(iVar4 + 0x47f0),uVar3,60000,param_2,
                              param_3,param_4);
      osMutexRelease(*puVar1);
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        param_2 = 0x7de;
        param_3 = PTR_s_lz4_decompress_max_map_data_len___00549c14;
        FUN_0043d574(4,PTR_s_navigation_ui_00549bc8,PTR_s_D__01_workspace_s200_ap510b_iar__00549bc4,
                     PTR_s_store_max_map_data_00549c04,0x7de,
                     PTR_s_lz4_decompress_max_map_data_len___00549c14,uVar3);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x10400000,PTR_s__navigation_ui_lz4_decompress_ma_00549c18,
                            PTR_s__navigation_ui_lz4_decompress_ma_00549c18,uVar3);
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_2 = 0x7e0;
        param_3 = PTR_s_unsupported_max_map_compress_mod_00549c1c;
        FUN_0043d574(2,PTR_s_navigation_ui_00549bc8,PTR_s_D__01_workspace_s200_ap510b_iar__00549bc4,
                     PTR_s_store_max_map_data_00549c04,0x7e0,
                     PTR_s_unsupported_max_map_compress_mod_00549c1c,*(undefined4 *)(iVar4 + 0x47f4)
                    );
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8400000,PTR_s__navigation_ui_unsupported_max_m_00549c20,
                            PTR_s__navigation_ui_unsupported_max_m_00549c20,
                            *(undefined4 *)(iVar4 + 0x47f4));
      }
    }
  }
  return CONCAT44(param_3,param_2);
}

