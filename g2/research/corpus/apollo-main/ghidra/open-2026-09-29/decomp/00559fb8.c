
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_00559fb8(ushort *param_1)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  ushort *puVar5;
  int iVar6;
  int iVar7;
  
  if (param_1 == (ushort *)0x0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_health_data_mgr_0055a310,DAT_0055a30c,
                   PTR_s_health_data_save_mult_highlight_0055a308,0x16e,
                   PTR_s_pb_mult_highlight_is_NULL_0055a304);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__health_data_mgr_pb_mult_highlig_0055a314,
                          PTR_s__health_data_mgr_pb_mult_highlig_0055a314);
    }
    uVar3 = 1;
  }
  else if (*param_1 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(2,PTR_s_health_data_mgr_0055a310,DAT_0055a30c,
                   PTR_s_health_data_save_mult_highlight_0055a308,0x173,
                   PTR_s_No_highlight_data_to_save_0055a318);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__health_data_mgr_No_highlight_da_0055a31c,
                          PTR_s__health_data_mgr_No_highlight_da_0055a31c);
    }
    uVar3 = 0;
  }
  else {
    health_lock_storage();
    iVar2 = _DAT_0055a320;
    FUN_0043c0e4(_DAT_0055a320 + 200,0x505,0);
    *(undefined4 *)(iVar2 + 0xc4) = 0;
    iVar6 = 0;
    for (iVar7 = 0; iVar7 < (int)(uint)*param_1; iVar7 = iVar7 + 1) {
      puVar5 = param_1 + iVar7 * 0x83 + 1;
      if (((char)*puVar5 == '\0') || ((char)*puVar5 == '\x01')) {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(2,PTR_s_health_data_mgr_0055a310,DAT_0055a30c,
                       PTR_s_health_data_save_mult_highlight_0055a308,0x185,
                       PTR_s_Skipping_invalid_highlight_data_t_0055a32c,iVar7);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x8400000,PTR_s__health_data_mgr_Skipping_invali_0055a330,
                              PTR_s__health_data_mgr_Skipping_invali_0055a330,iVar7);
        }
      }
      else {
        if (4 < *(uint *)(iVar2 + 0xc4)) {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            FUN_0043d574(2,PTR_s_health_data_mgr_0055a310,DAT_0055a30c,
                         PTR_s_health_data_save_mult_highlight_0055a308,0x18b,
                         PTR_s_Highlight_storage_is_full__skipp_0055a334);
          }
          iVar2 = FUN_0043d0ce();
          if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
            compress_log_output(0x8000000,PTR_s__health_data_mgr_Highlight_stora_0055a338,
                                PTR_s__health_data_mgr_Highlight_stora_0055a338);
          }
          break;
        }
        cVar1 = FUN_0055a230(puVar5,iVar2 + *(int *)(iVar2 + 0xc4) * 0x101 + 200);
        if (cVar1 == '\0') {
          *(int *)(iVar2 + 0xc4) = *(int *)(iVar2 + 0xc4) + 1;
          iVar6 = iVar6 + 1;
        }
        else {
          iVar4 = FUN_0043d0ce();
          if (iVar4 << 0x1e < 0) {
            FUN_0043d574(1,PTR_s_health_data_mgr_0055a310,DAT_0055a30c,
                         PTR_s_health_data_save_mult_highlight_0055a308,0x195,
                         PTR_s_Failed_to_convert_pb_highlight_a_0055a324,iVar7);
          }
          iVar4 = FUN_0043d0ce();
          if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
            compress_log_output(0x4400000,PTR_s__health_data_mgr_Failed_to_conve_0055a328,
                                PTR_s__health_data_mgr_Failed_to_conve_0055a328,iVar7);
          }
        }
      }
    }
    health_unlock_storage();
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,PTR_s_health_data_mgr_0055a310,DAT_0055a30c,
                   PTR_s_health_data_save_mult_highlight_0055a308,0x1a0,
                   PTR_s_Batch_highlight_save_completed____0055a33c,iVar6,*param_1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc800000,PTR_s__health_data_mgr_Batch_highlight_0055a340,
                          PTR_s__health_data_mgr_Batch_highlight_0055a340,iVar6,*param_1);
    }
    uVar3 = 0;
  }
  return uVar3;
}

