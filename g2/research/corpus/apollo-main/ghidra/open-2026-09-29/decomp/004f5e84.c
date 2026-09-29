
undefined8 FUN_004f5e84(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined *param_4)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uStack_18;
  undefined *puStack_14;
  
  uStack_18 = param_3;
  puStack_14 = param_4;
  iVar2 = quicklist_lock_storage();
  if (iVar2 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      puStack_14 = PTR_s_Failed_to_lock_storage_004f6868;
      uStack_18 = 0x42a;
      FUN_0043d574(1,DAT_004f6314,DAT_004f6310,PTR_s_quicklist_ui_data_update_004f686c);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__quicklist_page_Failed_to_lock_s_004f6870,
                          PTR_s__quicklist_page_Failed_to_lock_s_004f6870);
    }
    uVar3 = 0xffffffff;
    goto LAB_004f5fae;
  }
  cVar1 = FUN_004f5e18();
  if (cVar1 == '\0') {
    quicklist_unlock_storage();
    iVar2 = FUN_00443484();
    if ((iVar2 == 1) && (iVar2 = FUN_004434d0(1), iVar2 == 1)) {
      iVar2 = FUN_0045a568();
      if (iVar2 == 1) {
        uStack_18 = CONCAT13((char)*DAT_004f62f8,
                             CONCAT12(*DAT_004f62f4,(short)*(undefined4 *)PTR_DAT_004f687c));
        puStack_14 = (undefined *)
                     CONCAT31((int3)((uint)*(undefined4 *)(PTR_DAT_004f687c + 4) >> 8),
                              (char)((uint)*DAT_004f62f8 >> 8));
        FUN_00464bb2(1,&uStack_18,6,0);
      }
    }
    else {
      iVar2 = DAT_004f6760;
      *(undefined1 *)(DAT_004f6760 + 0x2e4e) = *DAT_004f62f4;
      *(short *)(iVar2 + 0x2e48) = (short)*DAT_004f62f8;
      FUN_004f5596();
      *(undefined1 *)(iVar2 + 0x2e4e) = 0;
      *(undefined2 *)(iVar2 + 0x2e48) = 0;
    }
    uVar3 = 0;
    goto LAB_004f5fae;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    puStack_14 = PTR_s_Failed_to_sync_data_from_storage_004f6874;
    uStack_18 = 0x430;
    FUN_0043d574(1,DAT_004f6314,DAT_004f6310,PTR_s_quicklist_ui_data_update_004f686c);
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1f < 0) {
LAB_004f5f18:
    compress_log_output(0x4000000,PTR_s__quicklist_page_Failed_to_sync_d_004f6878);
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1d < 0) goto LAB_004f5f18;
  }
  quicklist_unlock_storage();
  uVar3 = 0xfffffffe;
LAB_004f5fae:
  return CONCAT44(uStack_18,uVar3);
}

