
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8
FUN_0054e660(int param_1,short *param_2,int param_3,int param_4,undefined4 param_5,uint param_6)

{
  undefined1 *puVar1;
  uint *puVar2;
  byte bVar3;
  undefined1 uVar4;
  int iVar5;
  undefined4 uVar6;
  int iVar7;
  int iVar8;
  uint uVar9;
  int iVar10;
  uint uVar11;
  int iVar12;
  int iVar13;
  uint in_fpscr;
  float fVar14;
  float fVar15;
  float fVar16;
  float fVar17;
  float fVar18;
  short *psVar19;
  undefined1 *puStack_40;
  undefined4 uStack_3c;
  
  if ((param_1 == 0) || (param_2 == (short *)0x0)) {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_navigation_ui_0054ed7c,PTR_s_D__01_workspace_s200_ap510b_iar__0054ed78,
                   PTR_s_navigation_update_rotated_img_0054eda0,0xf3c,
                   PTR_s_Invalid_parameters_for_updating_r_0054ed9c);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__navigation_ui_Invalid_parameter_0054eda4,
                          PTR_s__navigation_ui_Invalid_parameter_0054eda4);
    }
    uVar6 = 0xffffffff;
  }
  else if (*param_2 == 0x4d42) {
    if ((ushort)param_2[0xe] == param_6) {
      if ((param_6 == 4) || (param_6 == 8)) {
        if ((*(int *)(param_2 + 9) != param_3) ||
           (iVar5 = FUN_00509694(*(undefined4 *)(param_2 + 0xb)), iVar5 != param_4)) {
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            uVar6 = FUN_00509694(*(undefined4 *)(param_2 + 0xb));
            FUN_0043d574(2,PTR_s_navigation_ui_0054ed7c,
                         PTR_s_D__01_workspace_s200_ap510b_iar__0054ed78,
                         PTR_s_navigation_update_rotated_img_0054eda0,0xf57,
                         PTR_s_BMP_size_mismatch__expected__dx__0054edc0,param_3,param_4,
                         *(undefined4 *)(param_2 + 9),uVar6);
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            uVar6 = FUN_00509694(*(undefined4 *)(param_2 + 0xb));
            compress_log_output(0x9000000,PTR_s__navigation_ui_BMP_size_mismatch_0054edc4,
                                PTR_s__navigation_ui_BMP_size_mismatch_0054edc4,param_3,param_4,
                                *(undefined4 *)(param_2 + 9),uVar6);
          }
        }
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(3,PTR_s_navigation_ui_0054ed7c,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054ed78,
                       PTR_s_navigation_update_rotated_img_0054eda0,0xf5d,
                       PTR_s_info_header_>colors_used___d_0054edc8,*(undefined4 *)(param_2 + 0x17));
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0xc400000,PTR_s__navigation_ui_info_header_>colo_0054edcc,
                              PTR_s__navigation_ui_info_header_>colo_0054edcc,
                              *(undefined4 *)(param_2 + 0x17));
        }
        if (param_6 == 4) {
          if (*(int *)(param_2 + 0x17) == 0) {
            uVar11 = 0x10;
          }
          else {
            uVar11 = *(uint *)(param_2 + 0x17);
          }
        }
        else if (*(int *)(param_2 + 0x17) == 0) {
          uVar11 = 0x100;
        }
        else {
          uVar11 = *(uint *)(param_2 + 0x17);
        }
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(3,PTR_s_navigation_ui_0054ed7c,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054ed78,
                       PTR_s_navigation_update_rotated_img_0054eda0,0xf63,
                       PTR_s_palette_size___d_0054edd0,uVar11);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0xc400000,PTR_s__navigation_ui_palette_size___d_0054edd4,
                              PTR_s__navigation_ui_palette_size___d_0054edd4,uVar11);
        }
        psVar19 = param_2 + 0x1b;
        iVar7 = *(int *)(param_2 + 5) + (int)param_2;
        iVar5 = param_3;
        if (param_6 == 4) {
          iVar5 = (param_3 + 1) / 2;
        }
        iVar5 = ((iVar5 + 3) / 4) * 4;
        for (iVar12 = 0; iVar13 = _DAT_0054eddc, iVar12 < param_4; iVar12 = iVar12 + 1) {
          for (iVar13 = 0; iVar13 < param_3; iVar13 = iVar13 + 1) {
            iVar10 = iVar12;
            if (0 < *(int *)(param_2 + 0xb)) {
              iVar10 = (param_4 + -1) - iVar12;
            }
            iVar8 = param_3 * iVar12 + iVar13;
            if (param_6 == 4) {
              bVar3 = *(byte *)(iVar7 + iVar5 * iVar10 + iVar13 / 2);
              if (iVar13 << 0x1f < 0) {
                uVar9 = bVar3 & 0xf;
              }
              else {
                uVar9 = (uint)(bVar3 >> 4);
              }
            }
            else {
              uVar9 = (uint)*(byte *)(iVar7 + iVar5 * iVar10 + iVar13);
            }
            bVar3 = (byte)uVar9;
            if (uVar11 <= uVar9) {
              bVar3 = 0;
            }
            uVar9 = (uint)bVar3;
            FUN_00441068((char)psVar19[uVar9 * 2 + 1],*(undefined1 *)((int)psVar19 + uVar9 * 4 + 1),
                         (char)psVar19[uVar9 * 2]);
            uVar4 = FUN_005456d6();
            *(undefined1 *)(_DAT_0054edd8 + iVar8) = uVar4;
          }
        }
        FUN_0043c0e4(_DAT_0054eddc,0x70e4,0xff);
        fVar14 = (float)VectorSignedToFloat(param_5,(byte)(in_fpscr >> 0x16) & 3);
        fVar14 = (fVar14 * fRam0054ec20) / fRam0054ec24;
        fVar15 = (float)FUN_0050968c(fVar14);
        fVar16 = (float)FUN_00509690(fVar14);
        fVar14 = fRam0054ec28;
        for (iVar5 = 0; puVar1 = _DAT_0054ede0, iVar5 < 0xaa; iVar5 = iVar5 + 1) {
          for (iVar7 = 0; iVar7 < 0xaa; iVar7 = iVar7 + 1) {
            fVar17 = (float)VectorSignedToFloat(iVar7,(byte)(in_fpscr >> 0x16) & 3);
            fVar18 = (float)VectorSignedToFloat(iVar5,(byte)(in_fpscr >> 0x16) & 3);
            uVar9 = (uint)((fVar17 - fVar14) * fVar15 + (fVar18 - fVar14) * fVar16 + fVar14);
            uVar11 = (uint)(((fVar18 - fVar14) * fVar15 - (fVar17 - fVar14) * fVar16) + fVar14);
            if ((uVar9 < 0xaa) && (uVar11 < 0xaa)) {
              *(undefined1 *)(iVar13 + iVar5 * 0xaa + iVar7) =
                   *(undefined1 *)(_DAT_0054edd8 + uVar11 * 0xaa + uVar9);
            }
          }
        }
        for (iVar5 = 0; puVar2 = _DAT_0054ede4, iVar5 < 0x78; iVar5 = iVar5 + 1) {
          for (iVar7 = 0; iVar7 < 0x78; iVar7 = iVar7 + 1) {
            puVar1[iVar5 * 0x78 + iVar7] =
                 *(undefined1 *)(iVar13 + (iVar5 + 0x19) * 0xaa + iVar7 + 0x19);
          }
        }
        puStack_40 = puVar1;
        uStack_3c = 0x3840;
        FUN_0047510e(&puStack_40);
        FUN_0043c0e4(puVar2,0x1c,0);
        *puVar2 = *puVar2 & 0xffffff00 | 0x19;
        *puVar2 = *puVar2 & 0xffff00ff | 0x600;
        puVar2[1] = puVar2[1] & 0xffff0000 | 0x78;
        puVar2[1] = puVar2[1] & 0xffff | 0x780000;
        puVar2[2] = puVar2[2] & 0xffff0000 | 0x78;
        *puVar2 = *puVar2 & 0xffff;
        puVar2[3] = 0x3840;
        puVar2[4] = (uint)puVar1;
        puVar2[5] = 0;
        puVar2[6] = 0;
        FUN_00498680(param_1,puVar2);
        iVar5 = FUN_00585cc2();
        if (iVar5 == 0) {
          FUN_00440656(param_1);
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            FUN_0043d574(4,PTR_s_navigation_ui_0054ed7c,
                         PTR_s_D__01_workspace_s200_ap510b_iar__0054ed78,
                         PTR_s_navigation_update_rotated_img_0054eda0,0xffd,PTR_DAT_0054ee00);
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            compress_log_output(0x10000000,PTR_DAT_0054ee04,PTR_DAT_0054ee04);
          }
        }
        else {
          iVar5 = FUN_00585cba();
          if (iVar5 == 0) {
            FUN_00440656(param_1);
            iVar5 = FUN_0043d0ce();
            if (iVar5 << 0x1e < 0) {
              FUN_0043d574(4,PTR_s_navigation_ui_0054ed7c,
                           PTR_s_D__01_workspace_s200_ap510b_iar__0054ed78,
                           PTR_s_navigation_update_rotated_img_0054eda0,0xff8,PTR_DAT_0054edf8);
            }
            iVar5 = FUN_0043d0ce();
            if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
              compress_log_output(0x10000000,PTR_DAT_0054edfc,PTR_DAT_0054edfc);
            }
          }
          else {
            iVar5 = FUN_0045fe04();
            if (iVar5 == 0) {
              FUN_00440656(param_1);
              iVar5 = FUN_0043d0ce();
              if (iVar5 << 0x1e < 0) {
                FUN_0043d574(4,PTR_s_navigation_ui_0054ed7c,
                             PTR_s_D__01_workspace_s200_ap510b_iar__0054ed78,
                             PTR_s_navigation_update_rotated_img_0054eda0,0xff3,PTR_DAT_0054edf0);
              }
              iVar5 = FUN_0043d0ce();
              if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
                compress_log_output(0x10000000,PTR_DAT_0054edf4,PTR_DAT_0054edf4);
              }
            }
            else {
              FUN_00440656();
              iVar5 = FUN_0043d0ce();
              if (iVar5 << 0x1e < 0) {
                FUN_0043d574(4,PTR_s_navigation_ui_0054ed7c,
                             PTR_s_D__01_workspace_s200_ap510b_iar__0054ed78,
                             PTR_s_navigation_update_rotated_img_0054eda0,0xfef,PTR_DAT_0054ede8);
              }
              iVar5 = FUN_0043d0ce();
              if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
                compress_log_output(0x10000000,PTR_DAT_0054edec,PTR_DAT_0054edec);
              }
            }
          }
        }
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_navigation_ui_0054ed7c,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054ed78,
                       PTR_s_navigation_update_rotated_img_0054eda0,0x1002,PTR_DAT_0054ee08,param_3,
                       param_4,0x78,0x78,param_5);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x11400000,PTR_LAB_0054ee0c,PTR_LAB_0054ee0c,param_3,param_4,0x78,0x78
                              ,param_5);
        }
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_navigation_ui_0054ed7c,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054ed78,
                       PTR_s_navigation_update_rotated_img_0054eda0,0x1004,
                       PTR_s_Extracted_pixel_samples__first___0054ee10,*puVar1,puVar1[0x1c20],
                       puVar1[0x383f]);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x10c00000,PTR_s__navigation_ui_Extracted_pixel_s_0054ee14,
                              PTR_s__navigation_ui_Extracted_pixel_s_0054ee14,*puVar1,puVar1[0x1c20]
                              ,puVar1[0x383f]);
        }
        uVar6 = 0;
      }
      else {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(1,PTR_s_navigation_ui_0054ed7c,
                       PTR_s_D__01_workspace_s200_ap510b_iar__0054ed78,
                       PTR_s_navigation_update_rotated_img_0054eda0,0xf50,
                       PTR_s_Unsupported_bit_depth___d__only_4_0054edb8,param_6);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x4400000,PTR_s__navigation_ui_Unsupported_bit_d_0054edbc,
                              PTR_s__navigation_ui_Unsupported_bit_d_0054edbc,param_6);
        }
        uVar6 = 0xffffffff;
      }
    }
    else {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(1,PTR_s_navigation_ui_0054ed7c,PTR_s_D__01_workspace_s200_ap510b_iar__0054ed78,
                     PTR_s_navigation_update_rotated_img_0054eda0,0xf4b,
                     PTR_s_BMP_bit_depth_mismatch__expected_0054edb0,param_6,param_2[0xe]);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x4800000,PTR_s__navigation_ui_BMP_bit_depth_mis_0054edb4,
                            PTR_s__navigation_ui_BMP_bit_depth_mis_0054edb4,param_6,param_2[0xe]);
      }
      uVar6 = 0xffffffff;
    }
  }
  else {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_navigation_ui_0054ed7c,PTR_s_D__01_workspace_s200_ap510b_iar__0054ed78,
                   PTR_s_navigation_update_rotated_img_0054eda0,0xf43,
                   PTR_s_Invalid_BMP_signature_0054eda8);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__navigation_ui_Invalid_BMP_signa_0054edac,
                          PTR_s__navigation_ui_Invalid_BMP_signa_0054edac);
    }
    uVar6 = 0xffffffff;
  }
  return CONCAT44(param_4,uVar6);
}

