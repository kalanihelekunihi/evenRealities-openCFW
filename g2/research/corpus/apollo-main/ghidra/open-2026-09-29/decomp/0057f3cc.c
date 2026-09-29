
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_0057f3cc(void)

{
  int iVar1;
  undefined *puVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  int iVar8;
  uint uVar9;
  
  iVar6 = _DAT_0057fc94;
  if (*_DAT_0057fc6c == 1) {
    iVar1 = FUN_004cfd0c(_DAT_0057fc94);
    if (iVar1 < 0) {
      puVar2 = PTR_s_LFS_ERR_CORRUPT___84__metadata_d_0057fca0;
      if ((((iVar1 != -0x54) && (puVar2 = PTR_s_LFS_ERR_INVAL___22__0057ff14, iVar1 != -0x16)) &&
          (puVar2 = PTR_s_LFS_ERR_NOMEM___12__0057fca8, iVar1 != -0xc)) &&
         ((puVar2 = PTR_s_LFS_ERR_IO___5__device_IO_0057fc9c, iVar1 != -5 &&
          (puVar2 = PTR_s_LFS_ERR_NOENT___2__0057fca4, iVar1 != -2)))) {
        puVar2 = _DAT_0057fc98;
      }
      FUN_004733ee(PTR_s_df__lfs_fs_size_failed_err__ld___0057ff18,iVar1,puVar2);
    }
    else {
      iVar5 = *(int *)(*(int *)(iVar6 + 0x68) + 0x1c);
      iVar6 = *(int *)(*(int *)(iVar6 + 0x68) + 0x20);
      uVar3 = iVar5 * iVar6;
      iVar8 = iVar5 * iVar1;
      if (uVar3 == 0) {
        uVar7 = 0;
      }
      else {
        uVar7 = (uint)(iVar8 * 100) / uVar3;
      }
      FUN_004733ee(PTR_s_Filesystem_1K_blocks_Used_Availa_0057ff1c);
      uVar4 = uVar3 + 0x3ff >> 10;
      uVar9 = iVar8 + 0x3ffU >> 10;
      uVar3 = (uVar3 - iVar8) + 0x3ff >> 10;
      FUN_004733ee(PTR_s_littlefs__10lu__9lu__9lu__3d_____0057ff20,uVar4,uVar9,uVar3,uVar7);
      FUN_004733ee(0x57f684);
      FUN_004733ee(PTR_s_____Disk_Space_Summary_____0057ff24);
      FUN_004733ee(PTR_s_Total_Capacity___lu_KB_0057ff28,uVar4);
      FUN_004733ee(PTR_s_Used_Space___lu_KB___d____0057ff2c,uVar9,uVar7);
      FUN_004733ee(PTR_s_Available_Space___lu_KB_0057ff30,uVar3);
      FUN_004733ee(PTR_s____________________________0057ff34);
      iVar8 = FUN_0043d0ce();
      if (iVar8 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_prvCommand_filesystem_0057f954,
                     PTR_s_D__01_workspace_s200_ap510b_iar__0057f950,PTR_s_prvCommand_df_0057ff3c,
                     899,PTR_s_Block_info__size__lu__total__lu__0057ff38,iVar5,iVar6,iVar1);
      }
      iVar8 = FUN_0043d0ce();
      if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
        compress_log_output(0x10c00000,_DAT_0057ffa4,_DAT_0057ffa4,iVar5,iVar6,iVar1);
      }
    }
  }
  else {
    FUN_004733ee(_DAT_0057fc90);
  }
  return 0;
}

