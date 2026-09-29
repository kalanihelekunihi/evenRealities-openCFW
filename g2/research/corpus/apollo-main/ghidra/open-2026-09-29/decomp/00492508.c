
undefined4 SVC_KvdbReadMenuConfigureValue(void)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  
  piVar1 = DAT_00492c28;
  FUN_0043c0e4(DAT_00492c28,0x378,0);
  iVar2 = SVC_KvdbBlobRead(DAT_00492c2c,piVar1,0x378);
  if ((iVar2 < 1) || (*piVar1 != DAT_00492c30)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00492bf8,DAT_00492bf4,PTR_s__kvdbUpdataMenuConfigureValue_00492c38,0x8d,
                   DAT_00492c80);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_00492c84,DAT_00492c84);
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,DAT_00492bf8,DAT_00492bf4,PTR_s__kvdbUpdataMenuConfigureValue_00492c38,0x72,
                   PTR_s_SVC_KvdbReadMenuConfigureValue__m_00492c34,(char)piVar1[1]);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc400000,PTR_s__kv_module_cfg_SVC_KvdbReadMenuC_00492c3c,
                          PTR_s__kv_module_cfg_SVC_KvdbReadMenuC_00492c3c,(char)piVar1[1]);
    }
    for (iVar2 = 0; iVar2 < (int)(uint)*(byte *)(piVar1 + 1); iVar2 = iVar2 + 1) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(3,DAT_00492bf8,DAT_00492bf4,PTR_s__kvdbUpdataMenuConfigureValue_00492c38,0x74,
                     PTR_s_SVC_KvdbReadMenuConfigureValue__m_00492c50,iVar2,
                     (char)piVar1[iVar2 * 0xb + 2]);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0xc800000,PTR_s__kv_module_cfg_SVC_KvdbReadMenuC_00492c54,
                            PTR_s__kv_module_cfg_SVC_KvdbReadMenuC_00492c54,iVar2,
                            (char)piVar1[iVar2 * 0xb + 2]);
      }
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(3,DAT_00492bf8,DAT_00492bf4,PTR_s__kvdbUpdataMenuConfigureValue_00492c38,0x75,
                     PTR_s_SVC_KvdbReadMenuConfigureValue__m_00492c58,iVar2,piVar1[iVar2 * 0xb + 3])
        ;
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0xc800000,PTR_s__kv_module_cfg_SVC_KvdbReadMenuC_00492c5c,
                            PTR_s__kv_module_cfg_SVC_KvdbReadMenuC_00492c5c,iVar2,
                            piVar1[iVar2 * 0xb + 3]);
      }
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(3,DAT_00492bf8,DAT_00492bf4,PTR_s__kvdbUpdataMenuConfigureValue_00492c38,0x76,
                     PTR_s_SVC_KvdbReadMenuConfigureValue__m_00492c60,iVar2,piVar1 + iVar2 * 0xb + 4
                    );
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0xc800000,PTR_s__kv_module_cfg_SVC_KvdbReadMenuC_00492c64,
                            PTR_s__kv_module_cfg_SVC_KvdbReadMenuC_00492c64,iVar2,
                            piVar1 + iVar2 * 0xb + 4);
      }
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(3,DAT_00492bf8,DAT_00492bf4,PTR_s__kvdbUpdataMenuConfigureValue_00492c38,0x77,
                     PTR_s_SVC_KvdbReadMenuConfigureValue__m_00492c68,iVar2,
                     piVar1[iVar2 * 0xb + 0xc]);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0xc800000,PTR_s__kv_module_cfg_SVC_KvdbReadMenuC_00492c6c,
                            PTR_s__kv_module_cfg_SVC_KvdbReadMenuC_00492c6c,iVar2,
                            piVar1[iVar2 * 0xb + 0xc]);
      }
      iVar4 = DAT_00492c40;
      if ((char)piVar1[iVar2 * 0xb + 2] == '\0') {
        iVar5 = FUN_00460450(piVar1[iVar2 * 0xb + 0xc],DAT_00492c40 + iVar2 * 0x34,
                             iVar2 * 0x34 + DAT_00492c40 + 4,iVar2 * 0x34 + DAT_00492c40 + 0x24,
                             iVar2 * 0x34 + DAT_00492c40 + 0x28);
        if (iVar5 != 0) {
          iVar4 = FUN_0043d0ce();
          if (iVar4 << 0x1e < 0) {
            FUN_0043d574(1,DAT_00492bf8,DAT_00492bf4,PTR_s__kvdbUpdataMenuConfigureValue_00492c38,
                         0x7c,PTR_s_menu_page_recv_data_from_BLE__ge_00492c70,
                         piVar1[iVar2 * 0xb + 0xc]);
          }
          iVar4 = FUN_0043d0ce();
          if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
            compress_log_output(0x4400000,PTR_s__kv_module_cfg_menu_page_recv_da_00492c74,
                                PTR_s__kv_module_cfg_menu_page_recv_da_00492c74,
                                piVar1[iVar2 * 0xb + 0xc]);
          }
          return 0xffffffff;
        }
        *(int *)(iVar4 + iVar2 * 0x34 + 0x30) = piVar1[iVar2 * 0xb + 0xc];
      }
      else {
        *(int *)(iVar2 * 0x34 + DAT_00492c40 + 0x30) = piVar1[iVar2 * 0xb + 0xc];
        *(undefined4 *)(iVar2 * 0x34 + iVar4 + 0x24) = 0xffe;
        *(undefined1 *)(iVar2 * 0x34 + iVar4 + 0x28) = 1;
        *(undefined **)(iVar4 + iVar2 * 0x34) = PTR_LAB_00492c44;
        uVar3 = FUN_0044a43c(piVar1 + iVar2 * 0xb + 4);
        FUN_00439be4(iVar2 * 0x34 + iVar4 + 4,piVar1 + iVar2 * 0xb + 4,uVar3);
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          uVar3 = FUN_00460084(iVar2 * 0x34 + iVar4 + 4);
          uVar3 = FUN_0045fffe(iVar2 * 0x34 + iVar4 + 4,uVar3);
          FUN_0043d574(3,DAT_00492bf8,DAT_00492bf4,PTR_s__kvdbUpdataMenuConfigureValue_00492c38,0x86
                       ,PTR_s_text____s_app_id____d_app_type___00492c48,uVar3,
                       *(undefined4 *)(iVar2 * 0x34 + iVar4 + 0x30),
                       *(undefined1 *)(iVar2 * 0x34 + iVar4 + 0x28));
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          uVar3 = FUN_00460084(iVar2 * 0x34 + iVar4 + 4);
          uVar3 = FUN_0045fffe(iVar2 * 0x34 + iVar4 + 4,uVar3);
          compress_log_output(0xcc00000,PTR_s__kv_module_cfg_text____s_app_id___00492c4c,
                              PTR_s__kv_module_cfg_text____s_app_id___00492c4c,uVar3,
                              *(undefined4 *)(iVar4 + iVar2 * 0x34 + 0x30),
                              *(undefined1 *)(iVar2 * 0x34 + iVar4 + 0x28));
        }
      }
    }
    *DAT_00492c78 = 1;
    *DAT_00492c7c = (uint)*(byte *)(piVar1 + 1);
  }
  return 0;
}

