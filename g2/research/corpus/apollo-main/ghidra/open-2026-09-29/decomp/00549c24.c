
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

uint FUN_00549c24(byte *param_1,short param_2)

{
  byte bVar1;
  byte bVar2;
  char *pcVar3;
  int *piVar4;
  char *pcVar5;
  uint *puVar6;
  undefined *puVar7;
  undefined *puVar8;
  undefined4 *puVar9;
  char cVar10;
  int iVar11;
  uint uVar12;
  int iVar13;
  undefined4 uVar14;
  undefined4 uVar15;
  undefined4 uVar16;
  byte abStack_dc [4];
  undefined1 uStack_d8;
  undefined1 uStack_d7;
  undefined1 uStack_d6;
  undefined1 uStack_d5;
  undefined1 uStack_d4;
  undefined1 uStack_d3;
  undefined4 uStack_cc;
  undefined4 uStack_c8;
  undefined4 uStack_c4;
  undefined4 uStack_c0;
  undefined4 uStack_bc;
  undefined4 uStack_b8;
  undefined4 uStack_b4;
  undefined4 uStack_b0;
  undefined4 uStack_ac;
  undefined4 uStack_a8;
  undefined4 uStack_a4;
  undefined4 uStack_a0;
  undefined4 uStack_9c;
  undefined4 uStack_98;
  undefined4 uStack_94;
  undefined4 uStack_90;
  undefined4 uStack_8c;
  undefined4 uStack_88;
  undefined4 uStack_84;
  undefined4 uStack_80;
  undefined4 uStack_7c;
  undefined4 uStack_78;
  undefined4 uStack_74;
  undefined4 uStack_70;
  undefined4 uStack_6c;
  undefined4 uStack_68;
  undefined4 uStack_64;
  undefined4 uStack_60;
  undefined4 uStack_5c;
  undefined4 uStack_58;
  undefined4 uStack_54;
  undefined4 uStack_50;
  undefined4 uStack_4c;
  undefined4 uStack_48;
  undefined4 uStack_44;
  undefined4 uStack_40;
  undefined4 uStack_3c;
  undefined4 uStack_38;
  undefined4 uStack_34;
  undefined4 uStack_30;
  undefined4 uStack_2c;
  undefined4 uStack_28;
  undefined4 uStack_24;
  undefined4 uStack_20;
  
  if (param_2 == 0) {
    iVar11 = FUN_0043d0ce();
    if (iVar11 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_navigation_ui_0054a924,PTR_s_D__01_workspace_s200_ap510b_iar__0054a920,
                   PTR_s_navigation_ui_reflash_page_handl_0054a91c,0x845,
                   PTR_s_navigation_ui_reflash_page_handl_0054a918);
    }
    iVar11 = FUN_0043d0ce();
    if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__navigation_ui_navigation_ui_ref_0054a928);
    }
    uVar12 = 0xffffffff;
  }
  else {
    bVar1 = *param_1;
    bVar2 = param_1[1];
    iVar11 = *(int *)(param_1 + 2);
    abStack_dc[0] = bVar2;
    iVar13 = FUN_0043d0ce();
    if (iVar13 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_navigation_ui_0054a924,PTR_s_D__01_workspace_s200_ap510b_iar__0054a920,
                   PTR_s_navigation_ui_reflash_page_handl_0054a91c,0x84e,
                   PTR_s_navigation_ui_reflash_page_handl_0054a92c,bVar1,iVar11);
    }
    iVar13 = FUN_0043d0ce();
    if ((iVar13 << 0x1f < 0) || (iVar13 = FUN_0043d0ce(), iVar13 << 0x1d < 0)) {
      compress_log_output(0x10800000,PTR_s__navigation_ui_navigation_ui_ref_0054a930,
                          PTR_s__navigation_ui_navigation_ui_ref_0054a930,bVar1,iVar11);
    }
    if (((bVar1 == 0) || (param_2 != 0)) && (*_DAT_0054a934 = 0x14, bVar1 == 0)) {
      navigation_send_type_0_shared(bVar2);
      iVar13 = FUN_0043d0ce();
      if (iVar13 << 0x1e < 0) {
        FUN_0043d574(4,PTR_s_navigation_ui_0054a924,PTR_s_D__01_workspace_s200_ap510b_iar__0054a920,
                     PTR_s_navigation_ui_reflash_page_handl_0054a91c,0x854,_DAT_0054a938);
      }
      iVar13 = FUN_0043d0ce();
      if ((iVar13 << 0x1f < 0) || (iVar13 = FUN_0043d0ce(), iVar13 << 0x1d < 0)) {
        compress_log_output(0x10000000,_DAT_0054a93c,_DAT_0054a93c);
      }
    }
    iVar13 = FUN_0043d0ce();
    if (iVar13 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_navigation_ui_0054a924,PTR_s_D__01_workspace_s200_ap510b_iar__0054a920,
                   PTR_s_navigation_ui_reflash_page_handl_0054a91c,0x858,
                   PTR_s_navigation_ui_state___d_0054aa94,*_DAT_0054a940);
    }
    iVar13 = FUN_0043d0ce();
    if ((iVar13 << 0x1f < 0) || (iVar13 = FUN_0043d0ce(), iVar13 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__navigation_ui_navigation_ui_sta_0054aa98,
                          PTR_s__navigation_ui_navigation_ui_sta_0054aa98,*_DAT_0054a940);
    }
    pcVar3 = _DAT_0054a940;
    cVar10 = *_DAT_0054a940;
    if (cVar10 == '\0') {
      if (bVar1 == 0xf2) {
        iVar11 = FUN_0043d0ce();
        if (iVar11 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_navigation_ui_0054a924,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054a920,
                       PTR_s_navigation_ui_reflash_page_handl_0054a91c,0x85e,
                       PTR_s_navigation_ui_reflash_page_handl_0054aa9c);
        }
        iVar11 = FUN_0043d0ce();
        if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
          compress_log_output(0x10000000,_DAT_0054ab28,_DAT_0054ab28);
        }
        if (abStack_dc[0] == 0x48) {
          uVar12 = system_close_page_factory_0046ae9c(1,8);
          return uVar12;
        }
      }
      if (bVar1 == 2) {
        navigation_send_type_1_shared(bVar2,0);
        FUN_005485c4(*_DAT_0054ab2c);
        *pcVar3 = '\x02';
        *_DAT_0054ab30 = '\0';
        *_DAT_0054ab34 = '\0';
        puVar6 = _DAT_0054ab38;
        if (*_DAT_0054ab38 != 0) {
          ui_common_api_fn_00509c96(*_DAT_0054ab38);
          *puVar6 = 0;
        }
        uVar12 = *puVar6;
        if (uVar12 == 0) {
          uVar12 = ui_common_api_fn_00509c1c();
          *puVar6 = uVar12;
          uVar12 = *puVar6;
          if (uVar12 == 0) {
            iVar11 = FUN_0043d0ce();
            if (iVar11 << 0x1e < 0) {
              FUN_0043d574(1,PTR_s_navigation_ui_0054a924,
                           PTR_s_D__01_workspace_s200_ap510b_iar__0054a920,
                           PTR_s_navigation_ui_reflash_page_handl_0054a91c,0x874,
                           PTR_s_navigation_ui_startup_page_creat_0054ab3c);
            }
            iVar11 = FUN_0043d0ce();
            if (-1 < iVar11 << 0x1f) {
              iVar11 = FUN_0043d0ce();
              if (-1 < iVar11 << 0x1d) {
                return iVar11 << 0x1d;
              }
            }
            uVar12 = compress_log_output(0x4000000,PTR_s__navigation_ui_navigation_ui_sta_0054ab40,
                                         PTR_s__navigation_ui_navigation_ui_sta_0054ab40);
          }
        }
      }
      else if (bVar1 == 3) {
        iVar11 = FUN_0043d0ce();
        if (iVar11 << 0x1e < 0) {
          FUN_0043d574(3,PTR_s_navigation_ui_0054a924,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054a920,
                       PTR_s_navigation_ui_reflash_page_handl_0054a91c,0x879,
                       PTR_s_navigation_ui_reflash_page_handl_0054ab44);
        }
        iVar11 = FUN_0043d0ce();
        if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
          compress_log_output(0xc000000,PTR_s__navigation_ui_navigation_ui_ref_0054ab48,
                              PTR_s__navigation_ui_navigation_ui_ref_0054ab48);
        }
        *pcVar3 = '\b';
        uStack_24 = *_DAT_0054ac50;
        uStack_20 = _DAT_0054ac50[1];
        FUN_0048eb32(_DAT_0054ac54,2,&uStack_24);
        FUN_005477ac();
        *_DAT_0054ac58 = 1;
        uVar12 = 0xf0;
        *_DAT_0054ac5c = 0xf0;
      }
      else if (bVar1 == 0xf0) {
        iVar11 = FUN_0043d0ce();
        if (iVar11 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_navigation_ui_0054a924,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054a920,
                       PTR_s_navigation_ui_reflash_page_handl_0054a91c,0x880,
                       PTR_s_navigation_ui_reflash_page_handl_0054ac60);
        }
        iVar11 = FUN_0043d0ce();
        if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054ac64,
                              PTR_s__navigation_ui_navigation_ui_ref_0054ac64);
        }
        FUN_0044d878(*_DAT_0054ab2c);
        *pcVar3 = '\b';
        uStack_2c = *(undefined4 *)PTR_DAT_0054ac68;
        uStack_28 = *(undefined4 *)(PTR_DAT_0054ac68 + 4);
        FUN_0048eb32(_DAT_0054ac54,2,&uStack_2c);
        FUN_005476e4();
        *_DAT_0054ac58 = 1;
        uVar12 = 0xf0;
        *_DAT_0054ac5c = 0xf0;
      }
      else {
        uVar12 = (uint)bVar1;
        if (uVar12 == 0xc) {
          navigation_send_type_12_shared(bVar2,0);
          FUN_004641b6(*_DAT_0054ab2c,8);
          uStack_a4 = *(undefined4 *)PTR_DAT_0054ac6c;
          uStack_a0 = *(undefined4 *)(PTR_DAT_0054ac6c + 4);
          FUN_0048eb32(_DAT_0054ac54,2,&uStack_a4);
          uVar12 = 1;
          *_DAT_0054ac70 = 1;
        }
        else if (bVar1 == 0xf4) {
          iVar11 = FUN_0043d0ce();
          if (iVar11 << 0x1e < 0) {
            FUN_0043d574(4,PTR_s_navigation_ui_0054a924,
                         PTR_s_D__01_workspace_s200_ap510b_iar__0054a920,
                         PTR_s_navigation_ui_reflash_page_handl_0054a91c,0x88e,
                         PTR_s_navigation_ui_reflash_page_handl_0054ad4c);
          }
          iVar11 = FUN_0043d0ce();
          if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
            compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054ad50,
                                PTR_s__navigation_ui_navigation_ui_ref_0054ad50);
          }
          FUN_004641b6(*_DAT_0054ab2c,8);
          *_DAT_0054ac70 = 1;
          uStack_34 = *(undefined4 *)PTR_DAT_0054ad54;
          uStack_30 = *(undefined4 *)(PTR_DAT_0054ad54 + 4);
          uVar12 = FUN_0048eb32(_DAT_0054ac54,2,&uStack_34);
        }
      }
    }
    else if (cVar10 == '\x01') {
      if (bVar1 == 0xf5) {
        iVar11 = FUN_0043d0ce();
        if (iVar11 << 0x1e < 0) {
          FUN_0043d574(3,PTR_s_navigation_ui_0054b21c,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054b218,
                       PTR_s_navigation_ui_reflash_page_handl_0054b214,0x9bd,
                       PTR_s_navigation_ui_reflash_page_handl_0054baa0);
        }
        iVar11 = FUN_0043d0ce();
        if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
          compress_log_output(0xc000000,PTR_s__navigation_ui_navigation_ui_ref_0054baa4,
                              PTR_s__navigation_ui_navigation_ui_ref_0054baa4);
        }
        *pcVar3 = '\n';
        uVar12 = FUN_00546620();
        return uVar12;
      }
      if (bVar1 == 0xf2) {
        iVar13 = FUN_0043d0ce();
        if (iVar13 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_navigation_ui_0054b21c,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054b218,
                       PTR_s_navigation_ui_reflash_page_handl_0054b214,0x9c4,
                       PTR_s_navigation_ui_reflash_page_handl_0054ba4c);
        }
        iVar13 = FUN_0043d0ce();
        if ((iVar13 << 0x1f < 0) || (iVar13 = FUN_0043d0ce(), iVar13 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054ba50,
                              PTR_s__navigation_ui_navigation_ui_ref_0054ba50);
        }
        if (abStack_dc[0] == 0x41) {
          iVar13 = FUN_0043d0ce();
          if (iVar13 << 0x1e < 0) {
            FUN_0043d574(4,PTR_s_navigation_ui_0054b21c,
                         PTR_s_D__01_workspace_s200_ap510b_iar__0054b218,
                         PTR_s_navigation_ui_reflash_page_handl_0054b214,0x9c7,_DAT_0054be68);
          }
          iVar13 = FUN_0043d0ce();
          if ((iVar13 << 0x1f < 0) || (iVar13 = FUN_0043d0ce(), iVar13 << 0x1d < 0)) {
            compress_log_output(0x10000000,_DAT_0054be6c,_DAT_0054be6c);
          }
          piVar4 = _DAT_0054be74;
          if (*_DAT_0054be70 != 1) {
            return *_DAT_0054be70;
          }
          *_DAT_0054be74 = iVar11;
          navigation_send_type_15_allocating(*piVar4);
          iVar11 = FUN_0043d0ce();
          if (iVar11 << 0x1e < 0) {
            FUN_0043d574(4,PTR_s_navigation_ui_0054b21c,
                         PTR_s_D__01_workspace_s200_ap510b_iar__0054b218,
                         PTR_s_navigation_ui_reflash_page_handl_0054b214,0x9cb,_DAT_0054be78,*piVar4
                        );
          }
          iVar11 = FUN_0043d0ce();
          if (-1 < iVar11 << 0x1f) {
            iVar11 = FUN_0043d0ce();
            if (-1 < iVar11 << 0x1d) {
              return iVar11 << 0x1d;
            }
          }
          uVar12 = compress_log_output(0x10400000,PTR_s__navigation_ui_navigation_ui_ref_0054baa8,
                                       PTR_s__navigation_ui_navigation_ui_ref_0054baa8,*piVar4);
          return uVar12;
        }
        if (abStack_dc[0] == 0x48) {
          uVar12 = system_close_page_factory_0046ae9c(1,8);
          return uVar12;
        }
      }
      if (bVar1 == 7) {
        iVar13 = FUN_0043d0ce();
        if (iVar13 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_navigation_ui_0054bf08,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054bf04,
                       PTR_s_navigation_ui_reflash_page_handl_0054bf00,0x9d9,
                       PTR_s_navigation_ui_reflash_page_handl_0054befc);
        }
        iVar13 = FUN_0043d0ce();
        if ((iVar13 << 0x1f < 0) || (iVar13 = FUN_0043d0ce(), iVar13 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054bf0c,
                              PTR_s__navigation_ui_navigation_ui_ref_0054bf0c);
        }
        FUN_005495a8();
        piVar4 = _DAT_0054b9ec;
        if ((*_DAT_0054b9ec != 0) &&
           (iVar13 = FUN_0043e2ea(*(undefined4 *)*_DAT_0054b9ec), iVar13 != 0)) {
          FUN_00463e1c(*piVar4,1);
          *piVar4 = 0;
        }
        navigation_send_type_7_shared(bVar2,0);
        FUN_0054692c();
        *pcVar3 = '\x05';
        *_DAT_0054bf10 = 0;
        *_DAT_0054bf14 = 0;
        iVar13 = FUN_0043d0ce();
        if (iVar13 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_navigation_ui_0054bf08,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054bf04,
                       PTR_s_navigation_ui_reflash_page_handl_0054bf00,0x9e7,_DAT_0054bf18);
        }
        iVar13 = FUN_0043d0ce();
        if ((iVar13 << 0x1f < 0) || (iVar13 = FUN_0043d0ce(), iVar13 << 0x1d < 0)) {
          compress_log_output(0x10000000,_DAT_0054bf1c,_DAT_0054bf1c);
        }
      }
      if (bVar1 == 8) {
        iVar13 = FUN_0043d0ce();
        if (iVar13 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_navigation_ui_0054bf08,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054bf04,
                       PTR_s_navigation_ui_reflash_page_handl_0054bf00,0x9eb,
                       PTR_s_navigation_ui_reflash_page_handl_0054ba54);
        }
        iVar13 = FUN_0043d0ce();
        if ((iVar13 << 0x1f < 0) || (iVar13 = FUN_0043d0ce(), iVar13 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054ba58,
                              PTR_s__navigation_ui_navigation_ui_ref_0054ba58);
        }
        FUN_00549708();
        piVar4 = _DAT_0054bf24;
        if (*(char *)(_DAT_0054bf20 + 0x18c) == '\x01') {
          if ((*_DAT_0054bf24 != 0) && (iVar13 = FUN_0043e2ea(*_DAT_0054bf24), iVar13 != 0)) {
            FUN_0043ded4(*piVar4,1);
          }
          *_DAT_0054ba5c = 1;
        }
      }
      if (bVar1 == 9) {
        iVar13 = FUN_0043d0ce();
        if (iVar13 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_navigation_ui_0054bf08,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054bf04,
                       PTR_s_navigation_ui_reflash_page_handl_0054bf00,0x9f7,
                       PTR_s_navigation_ui_reflash_page_handl_0054ba60);
        }
        iVar13 = FUN_0043d0ce();
        if ((iVar13 << 0x1f < 0) || (iVar13 = FUN_0043d0ce(), iVar13 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054ba64,
                              PTR_s__navigation_ui_navigation_ui_ref_0054ba64);
        }
        FUN_00549994();
        piVar4 = _DAT_0054bf2c;
        if (*_DAT_0054bf28 == '\x01') {
          if ((*_DAT_0054bf2c != 0) && (iVar13 = FUN_0043e2ea(*_DAT_0054bf2c), iVar13 != 0)) {
            FUN_0043ded4(*piVar4,1);
          }
          piVar4 = _DAT_0054bf30;
          if ((*_DAT_0054bf30 != 0) && (iVar13 = FUN_0043e2ea(*_DAT_0054bf30), iVar13 != 0)) {
            FUN_005458a2(*piVar4,_DAT_0054bf34);
          }
        }
      }
      if (bVar1 == 6) {
        iVar13 = FUN_0043d0ce();
        if (iVar13 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_navigation_ui_0054bf08,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054bf04,
                       PTR_s_navigation_ui_reflash_page_handl_0054bf00,0xa04,
                       PTR_s_navigation_ui_reflash_page_handl_0054ba68);
        }
        iVar13 = FUN_0043d0ce();
        if ((iVar13 << 0x1f < 0) || (iVar13 = FUN_0043d0ce(), iVar13 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054ba6c,
                              PTR_s__navigation_ui_navigation_ui_ref_0054ba6c);
        }
        *pcVar3 = '\x04';
        uStack_74 = *_DAT_0054bf38;
        uStack_70 = _DAT_0054bf38[1];
        FUN_0048eb32(_DAT_0054ba74,2,&uStack_74);
        *_DAT_0054ba78 = 1;
        *_DAT_0054ba7c = 0xf0;
        navigation_send_type_6_shared(bVar2,0);
        if (*_DAT_0054b808 != 0) {
          FUN_0044d878(*_DAT_0054b808);
        }
        FUN_0054787c(iVar11);
      }
      if (bVar1 == 0xc) {
        navigation_send_type_12_shared(bVar2,0);
        FUN_004641b6(*_DAT_0054b808,8);
        *_DAT_0054ba80 = 1;
        uStack_c4 = *_DAT_0054bf3c;
        uStack_c0 = _DAT_0054bf3c[1];
        FUN_0048eb32(_DAT_0054ba74,2,&uStack_c4);
      }
      if (bVar1 == 0xf0) {
        iVar11 = FUN_0043d0ce();
        if (iVar11 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_navigation_ui_0054bf08,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054bf04,
                       PTR_s_navigation_ui_reflash_page_handl_0054bf00,0xa1e,
                       PTR_s_navigation_ui_reflash_page_handl_0054ba88);
        }
        iVar11 = FUN_0043d0ce();
        if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054ba8c,
                              PTR_s__navigation_ui_navigation_ui_ref_0054ba8c);
        }
        FUN_0044d878(*_DAT_0054b808);
        *pcVar3 = '\b';
        FUN_005476e4();
        *_DAT_0054ba78 = 1;
        uStack_7c = *(undefined4 *)PTR_DAT_0054c248;
        uStack_78 = *(undefined4 *)(PTR_DAT_0054c248 + 4);
        FUN_0048eb32(_DAT_0054ba74,2,&uStack_7c);
        *_DAT_0054ba7c = 0xf0;
      }
      if (bVar1 == 0xf4) {
        iVar11 = FUN_0043d0ce();
        if (iVar11 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_navigation_ui_0054bf08,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054bf04,
                       PTR_s_navigation_ui_reflash_page_handl_0054bf00,0xa28,
                       PTR_s_navigation_ui_reflash_page_handl_0054ba94);
        }
        iVar11 = FUN_0043d0ce();
        if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054ba98,
                              PTR_s__navigation_ui_navigation_ui_ref_0054ba98);
        }
        FUN_004641b6(*_DAT_0054b808,8);
        *_DAT_0054ba80 = 1;
        uStack_84 = *(undefined4 *)PTR_DAT_0054c24c;
        uStack_80 = *(undefined4 *)(PTR_DAT_0054c24c + 4);
        uVar12 = FUN_0048eb32(_DAT_0054ba74,2,&uStack_84);
      }
      else {
        iVar11 = FUN_0043d0ce();
        if (iVar11 << 0x1e < 0) {
          FUN_0043d574(2,PTR_s_navigation_ui_0054bf08,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054bf04,
                       PTR_s_navigation_ui_reflash_page_handl_0054bf00,0xa2d,
                       PTR_s_navigation_ui_reflash_page_handl_0054c250,bVar1);
        }
        iVar11 = FUN_0043d0ce();
        if (-1 < iVar11 << 0x1f) {
          iVar11 = FUN_0043d0ce();
          if (-1 < iVar11 << 0x1d) {
            return iVar11 << 0x1d;
          }
        }
        uVar12 = compress_log_output(0x8400000,PTR_s__navigation_ui_navigation_ui_ref_0054c254,
                                     PTR_s__navigation_ui_navigation_ui_ref_0054c254,bVar1);
      }
    }
    else if (cVar10 == '\x02') {
      if (bVar1 == 0xf2) {
        iVar11 = FUN_0043d0ce();
        if (iVar11 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_navigation_ui_0054a924,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054a920,
                       PTR_s_navigation_ui_reflash_page_handl_0054a91c,0x89a,
                       PTR_s_navigation_ui_reflash_page_handl_0054aa9c);
        }
        iVar11 = FUN_0043d0ce();
        if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
          compress_log_output(0x10000000,_DAT_0054ab28,_DAT_0054ab28);
        }
        if (abStack_dc[0] == 0x48) {
          uVar12 = system_close_page_factory_0046ae9c(1,8);
          return uVar12;
        }
      }
      if (bVar1 == 0xf2) {
        iVar11 = FUN_0043d0ce();
        if (iVar11 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_navigation_ui_0054a924,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054a920,
                       PTR_s_navigation_ui_reflash_page_handl_0054a91c,0x8a3,
                       PTR_s_navigation_ui_reflash_page_handl_0054aa9c);
        }
        iVar11 = FUN_0043d0ce();
        if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
          compress_log_output(0x10000000,_DAT_0054ab28,_DAT_0054ab28);
        }
        if (abStack_dc[0] == 10) {
          iVar11 = FUN_0043d0ce();
          if (iVar11 << 0x1e < 0) {
            FUN_0043d574(4,PTR_s_navigation_ui_0054a924,
                         PTR_s_D__01_workspace_s200_ap510b_iar__0054a920,
                         PTR_s_navigation_ui_reflash_page_handl_0054a91c,0x8a5,
                         PTR_s_navigation_ui_reflash_page_handl_0054ad58);
          }
          iVar11 = FUN_0043d0ce();
          if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
            compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054ad5c,
                                PTR_s__navigation_ui_navigation_ui_ref_0054ad5c);
          }
          pcVar5 = _DAT_0054ab30;
          if (*_DAT_0054ab30 == '\x01') {
            iVar11 = FUN_0043d0ce();
            if (iVar11 << 0x1e < 0) {
              FUN_0043d574(4,PTR_s_navigation_ui_0054a924,
                           PTR_s_D__01_workspace_s200_ap510b_iar__0054a920,
                           PTR_s_navigation_ui_reflash_page_handl_0054a91c,0x8a7,
                           PTR_s_animation_running_push_event_to_f_0054ad60);
            }
            iVar11 = FUN_0043d0ce();
            if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
              compress_log_output(0x10000000,PTR_s__navigation_ui_animation_running_0054ad64,
                                  PTR_s__navigation_ui_animation_running_0054ad64);
            }
            uVar12 = ui_common_api_fn_00509ca2(*_DAT_0054ab38,abStack_dc,1);
          }
          else {
            FUN_0054cfd0(2);
            if (*_DAT_0054ab2c != 0) {
              FUN_0044d878(*_DAT_0054ab2c);
            }
            *pcVar3 = '\t';
            *_DAT_0054ab34 = '\0';
            *pcVar5 = '\0';
            ui_common_api_fn_00509f52(*_DAT_0054ab38);
            uVar12 = FUN_00548b98();
          }
        }
        else if (abStack_dc[0] == 0x44) {
          iVar11 = FUN_0043d0ce();
          if (iVar11 << 0x1e < 0) {
            FUN_0043d574(4,PTR_s_navigation_ui_0054a924,
                         PTR_s_D__01_workspace_s200_ap510b_iar__0054a920,
                         PTR_s_navigation_ui_reflash_page_handl_0054a91c,0x8b7,
                         PTR_s_navigation_ui_reflash_page_handl_0054ad68);
          }
          iVar11 = FUN_0043d0ce();
          if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
            compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054ad6c,
                                PTR_s__navigation_ui_navigation_ui_ref_0054ad6c);
          }
          if (*_DAT_0054ab30 == '\x01') {
            iVar11 = FUN_0043d0ce();
            if (iVar11 << 0x1e < 0) {
              FUN_0043d574(4,PTR_s_navigation_ui_0054a924,
                           PTR_s_D__01_workspace_s200_ap510b_iar__0054a920,
                           PTR_s_navigation_ui_reflash_page_handl_0054a91c,0x8b9,
                           PTR_s_animation_running_push_event_to_f_0054ad60);
            }
            iVar11 = FUN_0043d0ce();
            if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
              compress_log_output(0x10000000,PTR_s__navigation_ui_animation_running_0054ad64,
                                  PTR_s__navigation_ui_animation_running_0054ad64);
            }
            uVar12 = ui_common_api_fn_00509ca2(*_DAT_0054ab38,abStack_dc,1);
          }
          else {
            uVar12 = FUN_0054cfd0(1);
          }
        }
        else {
          uVar12 = (uint)abStack_dc[0];
          if (uVar12 == 0x45) {
            iVar11 = FUN_0043d0ce();
            if (iVar11 << 0x1e < 0) {
              FUN_0043d574(4,PTR_s_navigation_ui_0054a924,
                           PTR_s_D__01_workspace_s200_ap510b_iar__0054a920,
                           PTR_s_navigation_ui_reflash_page_handl_0054a91c,0x8bf,
                           PTR_s_navigation_ui_reflash_page_handl_0054ad70);
            }
            iVar11 = FUN_0043d0ce();
            if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
              compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054ad74,
                                  PTR_s__navigation_ui_navigation_ui_ref_0054ad74);
            }
            if (*_DAT_0054ab30 == '\x01') {
              iVar11 = FUN_0043d0ce();
              if (iVar11 << 0x1e < 0) {
                FUN_0043d574(4,PTR_s_navigation_ui_0054a924,
                             PTR_s_D__01_workspace_s200_ap510b_iar__0054a920,
                             PTR_s_navigation_ui_reflash_page_handl_0054a91c,0x8c1,
                             PTR_s_animation_running_push_event_to_f_0054ad60);
              }
              iVar11 = FUN_0043d0ce();
              if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
                compress_log_output(0x10000000,PTR_s__navigation_ui_animation_running_0054ad64,
                                    PTR_s__navigation_ui_animation_running_0054ad64);
              }
              uVar12 = ui_common_api_fn_00509ca2(*_DAT_0054ab38,abStack_dc,1);
            }
            else {
              uVar12 = FUN_0054cfd0(0);
            }
          }
        }
      }
      else if (bVar1 == 0xf0) {
        iVar11 = FUN_0043d0ce();
        if (iVar11 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_navigation_ui_0054a924,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054a920,
                       PTR_s_navigation_ui_reflash_page_handl_0054a91c,0x8c8,
                       PTR_s_navigation_ui_reflash_page_handl_0054ac60);
        }
        iVar11 = FUN_0043d0ce();
        if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054ac64,
                              PTR_s__navigation_ui_navigation_ui_ref_0054ac64);
        }
        FUN_0044d878(*_DAT_0054ab2c);
        *pcVar3 = '\b';
        uStack_3c = *(undefined4 *)PTR_DAT_0054b0cc;
        uStack_38 = *(undefined4 *)(PTR_DAT_0054b0cc + 4);
        FUN_0048eb32(_DAT_0054ac54,2,&uStack_3c);
        FUN_005476e4();
        *_DAT_0054ac58 = 1;
        uVar12 = 0xf0;
        *_DAT_0054ac5c = 0xf0;
      }
      else if (bVar1 == 0xc) {
        navigation_send_type_12_shared(bVar2,0);
        FUN_004641b6(*_DAT_0054ab2c,8);
        uStack_ac = *(undefined4 *)PTR_DAT_0054b0d0;
        uStack_a8 = *(undefined4 *)(PTR_DAT_0054b0d0 + 4);
        FUN_0048eb32(_DAT_0054ac54,2,&uStack_ac);
        uVar12 = 1;
        *_DAT_0054ac70 = 1;
      }
      else if (bVar1 == 0xf4) {
        iVar11 = FUN_0043d0ce();
        if (iVar11 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_navigation_ui_0054a924,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054a920,
                       PTR_s_navigation_ui_reflash_page_handl_0054a91c,0x8d6,
                       PTR_s_navigation_ui_reflash_page_handl_0054ad4c);
        }
        iVar11 = FUN_0043d0ce();
        if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054ad50,
                              PTR_s__navigation_ui_navigation_ui_ref_0054ad50);
        }
        FUN_004641b6(*_DAT_0054ab2c,8);
        *_DAT_0054ac70 = 1;
        uStack_44 = *(undefined4 *)PTR_DAT_0054b0d4;
        uStack_40 = *(undefined4 *)(PTR_DAT_0054b0d4 + 4);
        uVar12 = FUN_0048eb32(_DAT_0054ac54,2,&uStack_44);
      }
      else {
        iVar11 = FUN_0043d0ce();
        if (iVar11 << 0x1e < 0) {
          FUN_0043d574(2,PTR_s_navigation_ui_0054a924,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054a920,
                       PTR_s_navigation_ui_reflash_page_handl_0054a91c,0x8db,
                       PTR_s_navigation_ui_reflash_page_handl_0054b1c4,bVar1);
        }
        iVar11 = FUN_0043d0ce();
        if (-1 < iVar11 << 0x1f) {
          iVar11 = FUN_0043d0ce();
          if (-1 < iVar11 << 0x1d) {
            return iVar11 << 0x1d;
          }
        }
        uVar12 = compress_log_output(0x8400000,PTR_s__navigation_ui_navigation_ui_ref_0054b1c8,
                                     PTR_s__navigation_ui_navigation_ui_ref_0054b1c8,bVar1);
      }
    }
    else if (cVar10 == '\x04') {
      if (bVar1 == 0xc) {
        navigation_send_type_12_shared(bVar2,0);
        FUN_004641b6(*DAT_0054c588,8);
        *_DAT_0054c7f4 = 1;
      }
      uVar12 = (uint)bVar1;
      if (uVar12 == 0xf3) {
        iVar11 = FUN_0043d0ce();
        if (iVar11 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_navigation_ui_0054c5ac,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054c5a8,
                       PTR_s_navigation_ui_reflash_page_handl_0054c5a4,0xb06,
                       PTR_s_navigation_ui_reflash_page_handl_0054c834);
        }
        iVar11 = FUN_0043d0ce();
        if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054c838,
                              PTR_s__navigation_ui_navigation_ui_ref_0054c838);
        }
        FUN_004641b6(*DAT_0054c588,8);
        uVar12 = 1;
        *_DAT_0054c7f4 = 1;
      }
      if (bVar1 == 0xf4) {
        iVar11 = FUN_0043d0ce();
        if (iVar11 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_navigation_ui_0054c5ac,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054c5a8,
                       PTR_s_navigation_ui_reflash_page_handl_0054c5a4,0xb0c,
                       PTR_s_navigation_ui_reflash_page_handl_0054c828);
        }
        iVar11 = FUN_0043d0ce();
        if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054c82c,
                              PTR_s__navigation_ui_navigation_ui_ref_0054c82c);
        }
        FUN_004641b6(*DAT_0054c588,8);
        uVar12 = 1;
        *_DAT_0054c7f4 = 1;
      }
    }
    else if (cVar10 == '\x05') {
      if (bVar1 == 0xf2) {
        iVar13 = FUN_0043d0ce();
        if (iVar13 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_navigation_ui_0054bf08,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054bf04,
                       PTR_s_navigation_ui_reflash_page_handl_0054bf00,0xa36,
                       PTR_s_navigation_ui_reflash_page_handl_0054ba4c);
        }
        iVar13 = FUN_0043d0ce();
        if ((iVar13 << 0x1f < 0) || (iVar13 = FUN_0043d0ce(), iVar13 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054ba50,
                              PTR_s__navigation_ui_navigation_ui_ref_0054ba50);
        }
        if (abStack_dc[0] == 0x48) {
          uVar12 = system_close_page_factory_0046ae9c(1,8);
          return uVar12;
        }
      }
      if (bVar1 == 7) {
        iVar13 = FUN_0043d0ce();
        if (iVar13 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_navigation_ui_0054bf08,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054bf04,
                       PTR_s_navigation_ui_reflash_page_handl_0054bf00,0xa40,
                       PTR_s_navigation_ui_reflash_page_handl_0054befc);
        }
        iVar13 = FUN_0043d0ce();
        if ((iVar13 << 0x1f < 0) || (iVar13 = FUN_0043d0ce(), iVar13 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054bf0c,
                              PTR_s__navigation_ui_navigation_ui_ref_0054bf0c);
        }
        puVar9 = _DAT_0054c258;
        cVar10 = FUN_0043e0e0(*_DAT_0054c258,1);
        if (cVar10 == '\0') {
          iVar13 = FUN_0043d0ce();
          if (iVar13 << 0x1e < 0) {
            FUN_0043d574(3,PTR_s_navigation_ui_0054bf08,
                         PTR_s_D__01_workspace_s200_ap510b_iar__0054bf04,
                         PTR_s_navigation_ui_reflash_page_handl_0054bf00,0xa43,_DAT_0054c25c);
          }
          iVar13 = FUN_0043d0ce();
          if ((iVar13 << 0x1f < 0) || (iVar13 = FUN_0043d0ce(), iVar13 << 0x1d < 0)) {
            compress_log_output(0xc000000,_DAT_0054c260,_DAT_0054c260);
          }
          FUN_0043ded4(*puVar9,1);
        }
        FUN_005495a8();
        navigation_send_type_7_shared(bVar2,0);
        FUN_005464b8();
      }
      if (bVar1 == 8) {
        iVar13 = FUN_0043d0ce();
        if (iVar13 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_navigation_ui_0054bf08,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054bf04,
                       PTR_s_navigation_ui_reflash_page_handl_0054bf00,0xa4c,
                       PTR_s_navigation_ui_reflash_page_handl_0054ba54);
        }
        iVar13 = FUN_0043d0ce();
        if ((iVar13 << 0x1f < 0) || (iVar13 = FUN_0043d0ce(), iVar13 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054ba58,
                              PTR_s__navigation_ui_navigation_ui_ref_0054ba58);
        }
        FUN_00549708();
        if (*(char *)(_DAT_0054bf20 + 0x18c) == '\x01') {
          FUN_0054e660(*_DAT_0054c3c0,_DAT_0054c264,0xaa,0xaa,*_DAT_0054be74 * -10 + 0xe10,4);
          *_DAT_0054ba5c = 1;
          FUN_0043ded4(*_DAT_0054bf24,1);
        }
        else {
          FUN_0043dfa4(*_DAT_0054bf24,1);
        }
      }
      if (bVar1 == 9) {
        iVar13 = FUN_0043d0ce();
        if (iVar13 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_navigation_ui_0054bf08,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054bf04,
                       PTR_s_navigation_ui_reflash_page_handl_0054bf00,0xa6a,
                       PTR_s_navigation_ui_reflash_page_handl_0054ba60);
        }
        iVar13 = FUN_0043d0ce();
        if ((iVar13 << 0x1f < 0) || (iVar13 = FUN_0043d0ce(), iVar13 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054ba64,
                              PTR_s__navigation_ui_navigation_ui_ref_0054ba64);
        }
        FUN_00549994();
        if (*_DAT_0054bf28 == '\x01') {
          FUN_005458a2(*_DAT_0054bf30,_DAT_0054bf34);
          FUN_0043ded4(*_DAT_0054bf2c,1);
        }
      }
      if (bVar1 == 0xf2) {
        iVar13 = FUN_0043d0ce();
        if (iVar13 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_navigation_ui_0054bf08,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054bf04,
                       PTR_s_navigation_ui_reflash_page_handl_0054bf00,0xa74,
                       PTR_s_navigation_ui_reflash_page_handl_0054ba4c);
        }
        iVar13 = FUN_0043d0ce();
        if ((iVar13 << 0x1f < 0) || (iVar13 = FUN_0043d0ce(), iVar13 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054ba50,
                              PTR_s__navigation_ui_navigation_ui_ref_0054ba50);
        }
        if (abStack_dc[0] == 10) {
          iVar11 = FUN_0043d0ce();
          if (iVar11 << 0x1e < 0) {
            FUN_0043d574(4,PTR_s_navigation_ui_0054bf08,
                         PTR_s_D__01_workspace_s200_ap510b_iar__0054bf04,
                         PTR_s_navigation_ui_reflash_page_handl_0054bf00,0xa76,_DAT_0054c3c4);
          }
          iVar11 = FUN_0043d0ce();
          if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
            compress_log_output(0x10000000,_DAT_0054c3c8,_DAT_0054c3c8);
          }
          if (*_DAT_0054c3cc == '\x01') {
            iVar11 = FUN_0043d0ce();
            if (iVar11 << 0x1e < 0) {
              FUN_0043d574(4,PTR_s_navigation_ui_0054bf08,
                           PTR_s_D__01_workspace_s200_ap510b_iar__0054bf04,
                           PTR_s_navigation_ui_reflash_page_handl_0054bf00,0xa78,_DAT_0054c3d0);
            }
            iVar11 = FUN_0043d0ce();
            if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
              compress_log_output(0x10000000,_DAT_0054c3d4,_DAT_0054c3d4);
            }
            ui_common_api_fn_00509ca2(*_DAT_0054c3d8,param_1 + 1,5);
          }
          else if (*_DAT_0054bf10 == 0) {
            *_DAT_0054bf10 = 1;
            iVar11 = FUN_0043d0ce();
            if (iVar11 << 0x1e < 0) {
              FUN_0043d574(4,PTR_s_navigation_ui_0054bf08,
                           PTR_s_D__01_workspace_s200_ap510b_iar__0054bf04,
                           PTR_s_navigation_ui_reflash_page_handl_0054bf00,0xa7d,
                           PTR_s_navigation_ui_reflash_page_handl_0054c3dc);
            }
            iVar11 = FUN_0043d0ce();
            if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
              compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054c3e0,
                                  PTR_s__navigation_ui_navigation_ui_ref_0054c3e0);
            }
            FUN_0054853a();
            navigation_send_type_14_allocating(2);
          }
          else {
            *_DAT_0054bf10 = 0;
            iVar11 = FUN_0043d0ce();
            if (iVar11 << 0x1e < 0) {
              FUN_0043d574(4,PTR_s_navigation_ui_0054bf08,
                           PTR_s_D__01_workspace_s200_ap510b_iar__0054bf04,
                           PTR_s_navigation_ui_reflash_page_handl_0054bf00,0xa82,
                           PTR_s_navigation_ui_reflash_page_handl_0054c3e4);
            }
            iVar11 = FUN_0043d0ce();
            if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
              compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054c3e8,
                                  PTR_s__navigation_ui_navigation_ui_ref_0054c3e8);
            }
            FUN_00548542();
            navigation_send_type_14_allocating(1);
          }
        }
        else if (abStack_dc[0] == 0x41) {
          iVar13 = FUN_0043d0ce();
          if (iVar13 << 0x1e < 0) {
            FUN_0043d574(4,PTR_s_navigation_ui_0054bf08,
                         PTR_s_D__01_workspace_s200_ap510b_iar__0054bf04,
                         PTR_s_navigation_ui_reflash_page_handl_0054bf00,0xa88,_DAT_0054be68);
          }
          iVar13 = FUN_0043d0ce();
          if ((iVar13 << 0x1f < 0) || (iVar13 = FUN_0043d0ce(), iVar13 << 0x1d < 0)) {
            compress_log_output(0x10000000,_DAT_0054be6c,_DAT_0054be6c);
          }
          piVar4 = _DAT_0054be74;
          puVar6 = _DAT_0054be70;
          if (*_DAT_0054be70 == 1) {
            *_DAT_0054be74 = iVar11;
            navigation_send_type_15_allocating(*piVar4);
            iVar13 = FUN_0043d0ce();
            if (iVar13 << 0x1e < 0) {
              FUN_0043d574(4,PTR_s_navigation_ui_0054bf08,
                           PTR_s_D__01_workspace_s200_ap510b_iar__0054bf04,
                           PTR_s_navigation_ui_reflash_page_handl_0054bf00,0xa8d,_DAT_0054be78,
                           *piVar4);
            }
            iVar13 = FUN_0043d0ce();
            if ((iVar13 << 0x1f < 0) || (iVar13 = FUN_0043d0ce(), iVar13 << 0x1d < 0)) {
              compress_log_output(0x10400000,_DAT_0054c578,_DAT_0054c578,*piVar4);
            }
          }
          if (((*(char *)(_DAT_0054bf20 + 0x18c) == '\x01') && (*_DAT_0054c57c == '\x01')) &&
             (*puVar6 == 1)) {
            iVar13 = FUN_0043d0ce();
            if (iVar13 << 0x1e < 0) {
              FUN_0043d574(4,PTR_s_navigation_ui_0054bf08,
                           PTR_s_D__01_workspace_s200_ap510b_iar__0054bf04,
                           PTR_s_navigation_ui_reflash_page_handl_0054bf00,0xa91,_DAT_0054c580);
            }
            iVar13 = FUN_0043d0ce();
            if ((iVar13 << 0x1f < 0) || (iVar13 = FUN_0043d0ce(), iVar13 << 0x1d < 0)) {
              compress_log_output(0x10000000,_DAT_0054c584,_DAT_0054c584);
            }
            FUN_0054e660(*_DAT_0054c3c0,_DAT_0054c264,0xaa,0xaa,*_DAT_0054be74 * -10 + 0xe10,4);
            FUN_0043ded4(*_DAT_0054bf24,1);
          }
          piVar4 = _DAT_0054bf14;
          *_DAT_0054bf14 = iVar11;
          iVar11 = FUN_0043d0ce();
          if (iVar11 << 0x1e < 0) {
            FUN_0043d574(3,PTR_s_navigation_ui_0054bf08,
                         PTR_s_D__01_workspace_s200_ap510b_iar__0054bf04,
                         PTR_s_navigation_ui_reflash_page_handl_0054bf00,0xaa7,_DAT_0054be78,*piVar4
                        );
          }
          iVar11 = FUN_0043d0ce();
          if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
            compress_log_output(0xc400000,_DAT_0054c578,_DAT_0054c578,*piVar4);
          }
        }
      }
      if (bVar1 == 0xc) {
        navigation_send_type_12_shared(bVar2,0);
        FUN_004641b6(*DAT_0054c588,8);
        *_DAT_0054c7f4 = 1;
        uStack_cc = *_DAT_0054c58c;
        uStack_c8 = _DAT_0054c58c[1];
        FUN_0048eb32(_DAT_0054c590,2,&uStack_cc);
      }
      if (bVar1 == 0xf0) {
        iVar11 = FUN_0043d0ce();
        if (iVar11 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_navigation_ui_0054bf08,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054bf04,
                       PTR_s_navigation_ui_reflash_page_handl_0054bf00,0xaba,_DAT_0054c594);
        }
        iVar11 = FUN_0043d0ce();
        if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
          compress_log_output(0x10000000,_DAT_0054c598,_DAT_0054c598);
        }
        FUN_0044d878(*DAT_0054c588);
        *pcVar3 = '\b';
        FUN_005476e4();
        *_DAT_0054c59c = 1;
        uStack_8c = *(undefined4 *)PTR_DAT_0054c5a0;
        uStack_88 = *(undefined4 *)(PTR_DAT_0054c5a0 + 4);
        FUN_0048eb32(_DAT_0054c590,2,&uStack_8c);
        *_DAT_0054c7f8 = 0xf0;
      }
      if (bVar1 == 0xb) {
        iVar11 = FUN_0043d0ce();
        if (iVar11 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_navigation_ui_0054bf08,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054bf04,
                       PTR_s_navigation_ui_reflash_page_handl_0054bf00,0xac5,
                       PTR_s_navigation_ui_reflash_page_handl_0054c7fc);
        }
        iVar11 = FUN_0043d0ce();
        if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054c800,
                              PTR_s__navigation_ui_navigation_ui_ref_0054c800);
        }
        *pcVar3 = '\x04';
        *_DAT_0054c59c = 1;
        *_DAT_0054c7f8 = 0xf0;
        navigation_send_type_11_shared(bVar2,0);
        FUN_0044d878(*DAT_0054c588);
        FUN_005479c8();
        uStack_94 = *(undefined4 *)PTR_DAT_0054c804;
        uStack_90 = *(undefined4 *)(PTR_DAT_0054c804 + 4);
        FUN_0048eb32(_DAT_0054c590,2,&uStack_94);
      }
      uVar12 = (uint)bVar1;
      if (uVar12 == 10) {
        iVar11 = FUN_0043d0ce();
        if (iVar11 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_navigation_ui_0054bf08,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054bf04,
                       PTR_s_navigation_ui_reflash_page_handl_0054bf00,0xad1,
                       PTR_s_navigation_ui_reflash_page_handl_0054c808);
        }
        iVar11 = FUN_0043d0ce();
        if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054c80c,
                              PTR_s__navigation_ui_navigation_ui_ref_0054c80c);
        }
        navigation_send_type_10_shared(bVar2,0);
        FUN_0043dfa4(*_DAT_0054c258,1);
        *_DAT_0054c57c = '\0';
        FUN_0043dfa4(*_DAT_0054bf24,1);
        FUN_0043dfa4(*_DAT_0054bf2c,1);
        FUN_00498680(*_DAT_0054bf30,0);
        FUN_00498680(*_DAT_0054c3c0,0);
        puVar9 = _DAT_0054c810;
        osMutexAcquire(*_DAT_0054c810,0xffffffff);
        *_DAT_0054c814 = 0;
        FUN_0043c0e4(_DAT_0054c818,0x55c,0);
        FUN_0043c0e4(_DAT_0054c81c,0x18c,0);
        FUN_0043c0e4(_DAT_0054c820,0x4674,0);
        FUN_0043c0e4(_DAT_0054c824,0xea7c,0);
        uVar12 = osMutexRelease(*puVar9);
      }
      if (bVar1 == 0xf4) {
        iVar11 = FUN_0043d0ce();
        if (iVar11 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_navigation_ui_0054bf08,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054bf04,
                       PTR_s_navigation_ui_reflash_page_handl_0054bf00,0xae6,
                       PTR_s_navigation_ui_reflash_page_handl_0054c828);
        }
        iVar11 = FUN_0043d0ce();
        if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054c82c,
                              PTR_s__navigation_ui_navigation_ui_ref_0054c82c);
        }
        FUN_004641b6(*DAT_0054c588,8);
        *_DAT_0054c7f4 = 1;
        uStack_9c = *(undefined4 *)PTR_DAT_0054c830;
        uStack_98 = *(undefined4 *)(PTR_DAT_0054c830 + 4);
        uVar12 = FUN_0048eb32(_DAT_0054c590,2,&uStack_9c);
      }
    }
    else if (cVar10 == '\a') {
      if (bVar1 == 0xc) {
        navigation_send_type_12_shared(bVar2,0);
        FUN_004641b6(*DAT_0054c588,8);
        *_DAT_0054c7f4 = 1;
      }
      uVar12 = (uint)bVar1;
      if (uVar12 == 0xf3) {
        iVar11 = FUN_0043d0ce();
        if (iVar11 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_navigation_ui_0054c5ac,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054c5a8,
                       PTR_s_navigation_ui_reflash_page_handl_0054c5a4,0xb28,
                       PTR_s_navigation_ui_reflash_page_handl_0054c834);
        }
        iVar11 = FUN_0043d0ce();
        if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054c838,
                              PTR_s__navigation_ui_navigation_ui_ref_0054c838);
        }
        FUN_004641b6(*DAT_0054c588,8);
        uVar12 = 1;
        *_DAT_0054c7f4 = 1;
      }
      if (bVar1 == 0xf4) {
        iVar11 = FUN_0043d0ce();
        if (iVar11 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_navigation_ui_0054c5ac,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054c5a8,
                       PTR_s_navigation_ui_reflash_page_handl_0054c5a4,0xb2f,
                       PTR_s_navigation_ui_reflash_page_handl_0054c828);
        }
        iVar11 = FUN_0043d0ce();
        if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054c82c,
                              PTR_s__navigation_ui_navigation_ui_ref_0054c82c);
        }
        FUN_004641b6(*DAT_0054c588,8);
        uVar12 = 1;
        *_DAT_0054c7f4 = 1;
      }
    }
    else if (cVar10 == '\b') {
      if (bVar1 == 0xc) {
        navigation_send_type_12_shared(bVar2,0);
        FUN_004641b6(*DAT_0054c588,8);
        *_DAT_0054c7f4 = 1;
      }
      uVar12 = (uint)bVar1;
      if (uVar12 == 0xf3) {
        iVar11 = FUN_0043d0ce();
        if (iVar11 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_navigation_ui_0054c5ac,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054c5a8,
                       PTR_s_navigation_ui_reflash_page_handl_0054c5a4,0xb4c,
                       PTR_s_navigation_ui_reflash_page_handl_0054c834);
        }
        iVar11 = FUN_0043d0ce();
        if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054c838,
                              PTR_s__navigation_ui_navigation_ui_ref_0054c838);
        }
        FUN_004641b6(*DAT_0054c588,8);
        uVar12 = 1;
        *_DAT_0054c7f4 = 1;
      }
      if (bVar1 == 0xf4) {
        iVar11 = FUN_0043d0ce();
        if (iVar11 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_navigation_ui_0054c5ac,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054c5a8,
                       PTR_s_navigation_ui_reflash_page_handl_0054c5a4,0xb52,
                       PTR_s_navigation_ui_reflash_page_handl_0054c828);
        }
        iVar11 = FUN_0043d0ce();
        if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054c82c,
                              PTR_s__navigation_ui_navigation_ui_ref_0054c82c);
        }
        FUN_004641b6(*DAT_0054c588,8);
        uVar12 = 1;
        *_DAT_0054c7f4 = 1;
      }
    }
    else if (cVar10 == '\t') {
      if (bVar1 == 0xf2) {
        iVar11 = FUN_0043d0ce();
        if (iVar11 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_navigation_ui_0054a924,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054a920,
                       PTR_s_navigation_ui_reflash_page_handl_0054a91c,0x8e5,
                       PTR_s_navigation_ui_reflash_page_handl_0054aa9c);
        }
        iVar11 = FUN_0043d0ce();
        if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
          compress_log_output(0x10000000,_DAT_0054ab28,_DAT_0054ab28);
        }
        if (abStack_dc[0] == 0x48) {
          uVar12 = system_close_page_factory_0046ae9c(1,8);
          return uVar12;
        }
      }
      if (bVar1 == 0xf2) {
        iVar11 = FUN_0043d0ce();
        if (iVar11 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_navigation_ui_0054a924,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054a920,
                       PTR_s_navigation_ui_reflash_page_handl_0054a91c,0x8ef,
                       PTR_s_NAVIGATION_MODE_SELECT_PAGE__rec_0054b1cc);
        }
        iVar11 = FUN_0043d0ce();
        if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__navigation_ui_NAVIGATION_MODE_S_0054b1d0,
                              PTR_s__navigation_ui_NAVIGATION_MODE_S_0054b1d0);
        }
        if (abStack_dc[0] == 10) {
          iVar11 = FUN_0043d0ce();
          if (iVar11 << 0x1e < 0) {
            FUN_0043d574(4,PTR_s_navigation_ui_0054a924,
                         PTR_s_D__01_workspace_s200_ap510b_iar__0054a920,
                         PTR_s_navigation_ui_reflash_page_handl_0054a91c,0x8f1,
                         PTR_s_NAVIGATION_MODE_SELECT_PAGE__rec_0054b1d4);
          }
          iVar11 = FUN_0043d0ce();
          if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
            compress_log_output(0x10000000,PTR_s__navigation_ui_NAVIGATION_MODE_S_0054b1d8,
                                PTR_s__navigation_ui_NAVIGATION_MODE_S_0054b1d8);
          }
          if (*_DAT_0054ab34 == '\x01') {
            iVar11 = FUN_0043d0ce();
            if (iVar11 << 0x1e < 0) {
              FUN_0043d574(4,PTR_s_navigation_ui_0054a924,
                           PTR_s_D__01_workspace_s200_ap510b_iar__0054a920,
                           PTR_s_navigation_ui_reflash_page_handl_0054a91c,0x8f3,
                           PTR_s_animation_running_push_event_to_f_0054ad60);
            }
            iVar11 = FUN_0043d0ce();
            if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
              compress_log_output(0x10000000,PTR_s__navigation_ui_animation_running_0054ad64,
                                  PTR_s__navigation_ui_animation_running_0054ad64);
            }
            uVar12 = ui_common_api_fn_00509ca2(*_DAT_0054ab38,abStack_dc,1);
          }
          else {
            FUN_0054e1a8(2);
            iVar11 = FUN_0043d0ce();
            if (iVar11 << 0x1e < 0) {
              FUN_0043d574(3,PTR_s_navigation_ui_0054a924,
                           PTR_s_D__01_workspace_s200_ap510b_iar__0054a920,
                           PTR_s_navigation_ui_reflash_page_handl_0054a91c,0x8f7,
                           PTR_s_navigation_notify_location_selec_0054b1e8,_DAT_0054b1e4,
                           *_DAT_0054b1e0,*_DAT_0054b1dc);
            }
            iVar11 = FUN_0043d0ce();
            if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
              compress_log_output(0xcc00000,PTR_s__navigation_ui_navigation_notify_0054b1ec,
                                  PTR_s__navigation_ui_navigation_notify_0054b1ec,_DAT_0054b1e4,
                                  *_DAT_0054b1e0,*_DAT_0054b1dc);
            }
            piVar4 = _DAT_0054ab2c;
            if (*_DAT_0054ab2c != 0) {
              FUN_0044d878(*_DAT_0054ab2c);
            }
            uVar14 = FUN_00499416(*piVar4);
            FUN_0043f506(uVar14,0x23a);
            FUN_0043f568(uVar14,0x3fffffff);
            FUN_0043f6ac(uVar14,9);
            FUN_00499678(uVar14,0);
            puVar8 = PTR_s_ID_NAVIGATE_LOADING_BIKE_ROUTE_T_0054b204;
            puVar7 = PTR_s_ID_NAVIGATE_LOADING_WALK_ROUTE_T_0054b1f0;
            pcVar5 = _DAT_0054b1dc;
            if (*_DAT_0054b1dc == '\x01') {
              uVar15 = FUN_00460084(PTR_s_ID_NAVIGATE_LOADING_WALK_ROUTE_T_0054b1f0);
              uVar16 = FUN_0045fffe(puVar7,uVar15);
              uVar15 = _DAT_0054b1f4;
              FUN_0044b728(_DAT_0054b1f4,0x100,PTR_s__s__s_0054b1f8,uVar16,_DAT_0054b1e4);
              iVar11 = FUN_0043d0ce();
              if (iVar11 << 0x1e < 0) {
                FUN_0043d574(4,PTR_s_navigation_ui_0054a924,
                             PTR_s_D__01_workspace_s200_ap510b_iar__0054a920,
                             PTR_s_navigation_ui_reflash_page_handl_0054a91c,0x905,
                             PTR_s_temp_buf_loading_string___s_0054b1fc,uVar15);
              }
              iVar11 = FUN_0043d0ce();
              if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
                compress_log_output(0x10400000,PTR_s__navigation_ui_temp_buf_loading__0054b200,
                                    PTR_s__navigation_ui_temp_buf_loading__0054b200,uVar15);
              }
              FUN_0049942e(uVar14,uVar15);
            }
            else if (*_DAT_0054b1dc == '\x02') {
              uVar15 = FUN_00460084(PTR_s_ID_NAVIGATE_LOADING_BIKE_ROUTE_T_0054b204);
              uVar16 = FUN_0045fffe(puVar8,uVar15);
              uVar15 = _DAT_0054b1f4;
              FUN_0044b728(_DAT_0054b1f4,0x100,PTR_s__s__s_0054b1f8,uVar16,_DAT_0054b1e4);
              iVar11 = FUN_0043d0ce();
              if (iVar11 << 0x1e < 0) {
                FUN_0043d574(4,PTR_s_navigation_ui_0054a924,
                             PTR_s_D__01_workspace_s200_ap510b_iar__0054a920,
                             PTR_s_navigation_ui_reflash_page_handl_0054a91c,0x90a,
                             PTR_s_temp_buf_loading_string___s_0054b1fc,uVar15);
              }
              iVar11 = FUN_0043d0ce();
              if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
                compress_log_output(0x10400000,PTR_s__navigation_ui_temp_buf_loading__0054b200,
                                    PTR_s__navigation_ui_temp_buf_loading__0054b200,uVar15);
              }
              FUN_0049942e(uVar14,uVar15);
            }
            FUN_0044143e(uVar14,*_DAT_0054b208,0);
            FUN_0044145a(uVar14,2,0);
            FUN_00440656(*piVar4);
            *pcVar3 = '\x01';
            uVar14 = _DAT_0054b1e4;
            uVar15 = FUN_0044a43c(_DAT_0054b1e4);
            navigation_send_type_4_allocating(0,uVar14,uVar15,*_DAT_0054b1e0,*pcVar5);
            FUN_005455e4();
            uVar12 = FUN_0045a570();
            if ((uVar12 == 1) && (uVar12 = semantic_get_flag_20074fdc(), uVar12 == 0)) {
              navigation_send_type_16_allocating();
              FUN_0043c0e4(&uStack_d8,10,0);
              uStack_d8 = 0xf5;
              uStack_d7 = 0;
              uStack_d6 = 0;
              uStack_d5 = 0;
              uStack_d4 = 0;
              uStack_d3 = 0;
              uVar14 = FUN_00464bb2(8,&uStack_d8,6,0);
              iVar11 = FUN_0043d0ce();
              if (iVar11 << 0x1e < 0) {
                FUN_0043d574(4,PTR_s_navigation_ui_0054a924,
                             PTR_s_D__01_workspace_s200_ap510b_iar__0054a920,
                             PTR_s_navigation_ui_reflash_page_handl_0054a91c,0x924,
                             PTR_s_navigation_data_handler_send_for_0054b20c,uVar14);
              }
              iVar11 = FUN_0043d0ce();
              if (-1 < iVar11 << 0x1f) {
                iVar11 = FUN_0043d0ce();
                if (-1 < iVar11 << 0x1d) {
                  return iVar11 << 0x1d;
                }
              }
              uVar12 = compress_log_output(0x10400000,
                                           PTR_s__navigation_ui_navigation_data_h_0054b210,
                                           PTR_s__navigation_ui_navigation_data_h_0054b210,uVar14);
            }
          }
        }
        else if (abStack_dc[0] == 0x44) {
          iVar11 = FUN_0043d0ce();
          if (iVar11 << 0x1e < 0) {
            FUN_0043d574(4,PTR_s_navigation_ui_0054b21c,
                         PTR_s_D__01_workspace_s200_ap510b_iar__0054b218,
                         PTR_s_navigation_ui_reflash_page_handl_0054b214,0x92b,
                         PTR_s_navigation_ui_reflash_page_handl_0054ad68);
          }
          iVar11 = FUN_0043d0ce();
          if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
            compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054ad6c,
                                PTR_s__navigation_ui_navigation_ui_ref_0054ad6c);
          }
          if (*_DAT_0054ab34 == '\x01') {
            iVar11 = FUN_0043d0ce();
            if (iVar11 << 0x1e < 0) {
              FUN_0043d574(4,PTR_s_navigation_ui_0054b21c,
                           PTR_s_D__01_workspace_s200_ap510b_iar__0054b218,
                           PTR_s_navigation_ui_reflash_page_handl_0054b214,0x92d,
                           PTR_s_animation_running_push_event_to_f_0054ad60);
            }
            iVar11 = FUN_0043d0ce();
            if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
              compress_log_output(0x10000000,PTR_s__navigation_ui_animation_running_0054ad64,
                                  PTR_s__navigation_ui_animation_running_0054ad64);
            }
            uVar12 = ui_common_api_fn_00509ca2(*_DAT_0054ab38,abStack_dc,1);
          }
          else {
            uVar12 = FUN_0054e1a8(1);
          }
        }
        else {
          uVar12 = (uint)abStack_dc[0];
          if (uVar12 == 0x45) {
            iVar11 = FUN_0043d0ce();
            if (iVar11 << 0x1e < 0) {
              FUN_0043d574(4,PTR_s_navigation_ui_0054b21c,
                           PTR_s_D__01_workspace_s200_ap510b_iar__0054b218,
                           PTR_s_navigation_ui_reflash_page_handl_0054b214,0x933,
                           PTR_s_navigation_ui_reflash_page_handl_0054ad70);
            }
            iVar11 = FUN_0043d0ce();
            if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
              compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054ad74,
                                  PTR_s__navigation_ui_navigation_ui_ref_0054ad74);
            }
            if (*_DAT_0054ab34 == '\x01') {
              iVar11 = FUN_0043d0ce();
              if (iVar11 << 0x1e < 0) {
                FUN_0043d574(4,PTR_s_navigation_ui_0054b21c,
                             PTR_s_D__01_workspace_s200_ap510b_iar__0054b218,
                             PTR_s_navigation_ui_reflash_page_handl_0054b214,0x935,
                             PTR_s_animation_running_push_event_to_f_0054ad60);
              }
              iVar11 = FUN_0043d0ce();
              if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
                compress_log_output(0x10000000,PTR_s__navigation_ui_animation_running_0054ad64,
                                    PTR_s__navigation_ui_animation_running_0054ad64);
              }
              uVar12 = ui_common_api_fn_00509ca2(*_DAT_0054ab38,abStack_dc,1);
            }
            else {
              uVar12 = FUN_0054e1a8(0);
            }
          }
        }
      }
      else if (bVar1 == 0xf0) {
        iVar11 = FUN_0043d0ce();
        if (iVar11 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_navigation_ui_0054b21c,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054b218,
                       PTR_s_navigation_ui_reflash_page_handl_0054b214,0x93c,
                       PTR_s_navigation_ui_reflash_page_handl_0054ac60);
        }
        iVar11 = FUN_0043d0ce();
        if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054ac64,
                              PTR_s__navigation_ui_navigation_ui_ref_0054ac64);
        }
        FUN_0044d878(*_DAT_0054ab2c);
        *pcVar3 = '\b';
        uStack_4c = *_DAT_0054b804;
        uStack_48 = _DAT_0054b804[1];
        FUN_0048eb32(_DAT_0054ac54,2,&uStack_4c);
        FUN_005476e4();
        *_DAT_0054ac58 = 1;
        uVar12 = 0xf0;
        *_DAT_0054ac5c = 0xf0;
      }
      else if (bVar1 == 0xc) {
        navigation_send_type_12_shared(bVar2,0);
        FUN_004641b6(*_DAT_0054b808,8);
        *_DAT_0054ac70 = 1;
        uStack_b4 = *(undefined4 *)PTR_DAT_0054b80c;
        uStack_b0 = *(undefined4 *)(PTR_DAT_0054b80c + 4);
        uVar12 = FUN_0048eb32(_DAT_0054ac54,2,&uStack_b4);
      }
      else if (bVar1 == 0xf4) {
        iVar11 = FUN_0043d0ce();
        if (iVar11 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_navigation_ui_0054b21c,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054b218,
                       PTR_s_navigation_ui_reflash_page_handl_0054b214,0x94f,
                       PTR_s_navigation_ui_reflash_page_handl_0054ad4c);
        }
        iVar11 = FUN_0043d0ce();
        if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054ad50,
                              PTR_s__navigation_ui_navigation_ui_ref_0054ad50);
        }
        FUN_004641b6(*_DAT_0054b808,8);
        *_DAT_0054ac70 = 1;
        uStack_54 = *(undefined4 *)PTR_DAT_0054b810;
        uStack_50 = *(undefined4 *)(PTR_DAT_0054b810 + 4);
        uVar12 = FUN_0048eb32(_DAT_0054ac54,2,&uStack_54);
      }
      else {
        iVar11 = FUN_0043d0ce();
        if (iVar11 << 0x1e < 0) {
          FUN_0043d574(2,PTR_s_navigation_ui_0054b21c,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054b218,
                       PTR_s_navigation_ui_reflash_page_handl_0054b214,0x954,
                       PTR_s_navigation_ui_reflash_page_handl_0054b1c4,bVar1);
        }
        iVar11 = FUN_0043d0ce();
        if (-1 < iVar11 << 0x1f) {
          iVar11 = FUN_0043d0ce();
          if (-1 < iVar11 << 0x1d) {
            return iVar11 << 0x1d;
          }
        }
        uVar12 = compress_log_output(0x8400000,PTR_s__navigation_ui_navigation_ui_ref_0054b1c8,
                                     PTR_s__navigation_ui_navigation_ui_ref_0054b1c8,bVar1);
      }
    }
    else if (cVar10 == '\n') {
      if (bVar1 == 0xf6) {
        iVar13 = FUN_0043d0ce();
        if (iVar13 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_navigation_ui_0054b21c,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054b218,
                       PTR_s_navigation_ui_reflash_page_handl_0054b214,0x95f,
                       PTR_s_navigation_ui_reflash_page_handl_0054b814);
        }
        iVar13 = FUN_0043d0ce();
        if ((iVar13 << 0x1f < 0) || (iVar13 = FUN_0043d0ce(), iVar13 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054b818,
                              PTR_s__navigation_ui_navigation_ui_ref_0054b818);
        }
        piVar4 = _DAT_0054b9ec;
        if (((*_DAT_0054b9ec != 0) &&
            (iVar13 = FUN_0043e2ea(*(undefined4 *)*_DAT_0054b9ec), iVar13 != 0)) &&
           (uVar12 = FUN_00463fa4(*piVar4), uVar12 != param_1[1])) {
          FUN_00463f5c(*piVar4,param_1[1]);
        }
      }
      if (bVar1 == 0xf7) {
        iVar11 = FUN_0043d0ce();
        if (iVar11 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_navigation_ui_0054b21c,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054b218,
                       PTR_s_navigation_ui_reflash_page_handl_0054b214,0x968,_DAT_0054b9f0);
        }
        iVar11 = FUN_0043d0ce();
        if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
          compress_log_output(0x10000000,_DAT_0054b9f4,_DAT_0054b9f4);
        }
        *pcVar3 = '\x01';
        uVar12 = navigation_send_type_17_allocating();
      }
      else {
        if (bVar1 == 0xf2) {
          iVar13 = FUN_0043d0ce();
          if (iVar13 << 0x1e < 0) {
            FUN_0043d574(4,PTR_s_navigation_ui_0054b21c,
                         PTR_s_D__01_workspace_s200_ap510b_iar__0054b218,
                         PTR_s_navigation_ui_reflash_page_handl_0054b214,0x96f,
                         PTR_s_navigation_ui_reflash_page_handl_0054ba4c);
          }
          iVar13 = FUN_0043d0ce();
          if ((iVar13 << 0x1f < 0) || (iVar13 = FUN_0043d0ce(), iVar13 << 0x1d < 0)) {
            compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054ba50,
                                PTR_s__navigation_ui_navigation_ui_ref_0054ba50);
          }
          if (abStack_dc[0] == 0x48) {
            uVar12 = system_close_page_factory_0046ae9c(1,8);
            return uVar12;
          }
        }
        if (bVar1 == 8) {
          iVar13 = FUN_0043d0ce();
          if (iVar13 << 0x1e < 0) {
            FUN_0043d574(4,PTR_s_navigation_ui_0054b21c,
                         PTR_s_D__01_workspace_s200_ap510b_iar__0054b218,
                         PTR_s_navigation_ui_reflash_page_handl_0054b214,0x982,
                         PTR_s_navigation_ui_reflash_page_handl_0054ba54);
          }
          iVar13 = FUN_0043d0ce();
          if ((iVar13 << 0x1f < 0) || (iVar13 = FUN_0043d0ce(), iVar13 << 0x1d < 0)) {
            compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054ba58,
                                PTR_s__navigation_ui_navigation_ui_ref_0054ba58);
          }
          FUN_00549708();
          *_DAT_0054ba5c = 1;
        }
        if (bVar1 == 9) {
          iVar13 = FUN_0043d0ce();
          if (iVar13 << 0x1e < 0) {
            FUN_0043d574(4,PTR_s_navigation_ui_0054b21c,
                         PTR_s_D__01_workspace_s200_ap510b_iar__0054b218,
                         PTR_s_navigation_ui_reflash_page_handl_0054b214,0x98a,
                         PTR_s_navigation_ui_reflash_page_handl_0054ba60);
          }
          iVar13 = FUN_0043d0ce();
          if ((iVar13 << 0x1f < 0) || (iVar13 = FUN_0043d0ce(), iVar13 << 0x1d < 0)) {
            compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054ba64,
                                PTR_s__navigation_ui_navigation_ui_ref_0054ba64);
          }
          FUN_00549994();
        }
        if (bVar1 == 6) {
          iVar13 = FUN_0043d0ce();
          if (iVar13 << 0x1e < 0) {
            FUN_0043d574(4,PTR_s_navigation_ui_0054b21c,
                         PTR_s_D__01_workspace_s200_ap510b_iar__0054b218,
                         PTR_s_navigation_ui_reflash_page_handl_0054b214,0x98f,
                         PTR_s_navigation_ui_reflash_page_handl_0054ba68);
          }
          iVar13 = FUN_0043d0ce();
          if ((iVar13 << 0x1f < 0) || (iVar13 = FUN_0043d0ce(), iVar13 << 0x1d < 0)) {
            compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054ba6c,
                                PTR_s__navigation_ui_navigation_ui_ref_0054ba6c);
          }
          *pcVar3 = '\x04';
          uStack_5c = *(undefined4 *)PTR_DAT_0054ba70;
          uStack_58 = *(undefined4 *)(PTR_DAT_0054ba70 + 4);
          FUN_0048eb32(_DAT_0054ba74,2,&uStack_5c);
          piVar4 = _DAT_0054b9ec;
          FUN_00463e1c(*_DAT_0054b9ec,1);
          *piVar4 = 0;
          *_DAT_0054ba78 = 1;
          *_DAT_0054ba7c = 0xf0;
          navigation_send_type_6_shared(bVar2,0);
          if (*_DAT_0054b808 != 0) {
            FUN_0044d878(*_DAT_0054b808);
          }
          FUN_0054787c(iVar11);
        }
        if (bVar1 == 0xc) {
          navigation_send_type_12_shared(bVar2,0);
          FUN_004641b6(*_DAT_0054b808,8);
          *_DAT_0054ba80 = 1;
          uStack_bc = *(undefined4 *)PTR_DAT_0054ba84;
          uStack_b8 = *(undefined4 *)(PTR_DAT_0054ba84 + 4);
          FUN_0048eb32(_DAT_0054ba74,2,&uStack_bc);
        }
        uVar12 = (uint)bVar1;
        if (uVar12 == 0xf0) {
          iVar11 = FUN_0043d0ce();
          if (iVar11 << 0x1e < 0) {
            FUN_0043d574(4,PTR_s_navigation_ui_0054b21c,
                         PTR_s_D__01_workspace_s200_ap510b_iar__0054b218,
                         PTR_s_navigation_ui_reflash_page_handl_0054b214,0x9a5,
                         PTR_s_navigation_ui_reflash_page_handl_0054ba88);
          }
          iVar11 = FUN_0043d0ce();
          if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
            compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054ba8c,
                                PTR_s__navigation_ui_navigation_ui_ref_0054ba8c);
          }
          FUN_0044d878(*_DAT_0054b808);
          *pcVar3 = '\b';
          uStack_64 = *(undefined4 *)PTR_DAT_0054ba90;
          uStack_60 = *(undefined4 *)(PTR_DAT_0054ba90 + 4);
          FUN_0048eb32(_DAT_0054ba74,2,&uStack_64);
          piVar4 = _DAT_0054b9ec;
          FUN_00463e1c(*_DAT_0054b9ec,1);
          *piVar4 = 0;
          FUN_005476e4();
          *_DAT_0054ba78 = 1;
          uVar12 = 0xf0;
          *_DAT_0054ba7c = 0xf0;
        }
        if (bVar1 == 0xf4) {
          iVar11 = FUN_0043d0ce();
          if (iVar11 << 0x1e < 0) {
            FUN_0043d574(4,PTR_s_navigation_ui_0054b21c,
                         PTR_s_D__01_workspace_s200_ap510b_iar__0054b218,
                         PTR_s_navigation_ui_reflash_page_handl_0054b214,0x9b1,
                         PTR_s_navigation_ui_reflash_page_handl_0054ba94);
          }
          iVar11 = FUN_0043d0ce();
          if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
            compress_log_output(0x10000000,PTR_s__navigation_ui_navigation_ui_ref_0054ba98,
                                PTR_s__navigation_ui_navigation_ui_ref_0054ba98);
          }
          FUN_004641b6(*_DAT_0054b808,8);
          *_DAT_0054ba80 = 1;
          uStack_6c = *(undefined4 *)PTR_DAT_0054ba9c;
          uStack_68 = *(undefined4 *)(PTR_DAT_0054ba9c + 4);
          uVar12 = FUN_0048eb32(_DAT_0054ba74,2,&uStack_6c);
        }
      }
    }
    else {
      iVar11 = FUN_0043d0ce();
      if (iVar11 << 0x1e < 0) {
        FUN_0043d574(2,PTR_s_navigation_ui_0054c5ac,PTR_s_D__01_workspace_s200_ap510b_iar__0054c5a8,
                     PTR_s_navigation_ui_reflash_page_handl_0054c5a4,0xb5c,
                     PTR_s_unknown_navigation_ui_state___d_0054cc90,*pcVar3);
      }
      iVar11 = FUN_0043d0ce();
      if (-1 < iVar11 << 0x1f) {
        iVar11 = FUN_0043d0ce();
        if (-1 < iVar11 << 0x1d) {
          return iVar11 << 0x1d;
        }
      }
      uVar12 = compress_log_output(0x8400000,_DAT_0054ceac,_DAT_0054ceac,*pcVar3);
    }
  }
  return uVar12;
}

