
void FUN_00461620(byte param_1)

{
  uint *puVar1;
  uint *puVar2;
  char cVar3;
  int iVar4;
  int iVar5;
  undefined4 uVar6;
  int *piVar7;
  uint uVar8;
  uint uVar9;
  uint local_11c;
  uint local_118;
  uint local_114;
  uint local_110;
  undefined4 uStack_10c;
  uint local_108;
  undefined4 uStack_104;
  uint local_100;
  undefined4 uStack_fc;
  undefined4 local_f8;
  undefined4 uStack_f4;
  undefined4 local_f0;
  undefined4 uStack_ec;
  undefined4 local_e8;
  undefined4 uStack_e4;
  undefined4 local_e0;
  undefined4 uStack_dc;
  undefined4 local_d8;
  undefined4 uStack_d4;
  undefined4 local_d0;
  undefined4 uStack_cc;
  undefined4 local_c8;
  undefined4 uStack_c4;
  undefined4 local_c0;
  undefined4 uStack_bc;
  undefined1 local_b8;
  undefined1 local_b7;
  undefined1 local_b6;
  undefined1 local_b5;
  undefined1 local_b4;
  undefined1 auStack_b3 [59];
  undefined4 local_78;
  undefined4 local_74;
  undefined4 local_58;
  undefined4 local_48;
  undefined4 local_3c;
  
  piVar7 = DAT_0046255c;
  puVar2 = DAT_00462444;
  puVar1 = DAT_00461b70;
  if (*DAT_00461fb8 == 0) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      local_11c = DAT_0046236c;
      FUN_0043d574(2,DAT_00461e90,DAT_00461e8c,DAT_00462370,0x2e8);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_00462374,DAT_00462374);
    }
  }
  else if (*DAT_00462378 == '\0') {
    if (param_1 == 0) {
      if ((int)*DAT_00461b70 < 1) {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          local_11c = DAT_00462554;
          FUN_0043d574(2,DAT_00461e90,DAT_00461e8c,DAT_00462370,800);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x8000000,DAT_00462558,DAT_00462558);
        }
        FUN_0046137c(1);
      }
      else {
        uVar9 = *DAT_00461b70 - *DAT_00462444;
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          local_110 = *puVar2;
          local_118 = *puVar1;
          local_11c = DAT_00462448;
          local_114 = uVar9;
          FUN_0043d574(4,DAT_00461e90,DAT_00461e8c,DAT_00462370,0x2f9);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          local_11c = *puVar2;
          compress_log_output(0x10c00000,DAT_0046244c,DAT_0046244c,*puVar1,uVar9);
        }
        if ((int)uVar9 < 3) {
          if (uVar9 == 2) {
            if ((int)*puVar2 < 1) {
              *puVar1 = *puVar1 - 1;
              iVar4 = FUN_0043d0ce();
              if (iVar4 << 0x1e < 0) {
                local_118 = *puVar1;
                local_11c = DAT_0046254c;
                FUN_0043d574(4,DAT_00461e90,DAT_00461e8c,DAT_00462370,0x311);
              }
              iVar4 = FUN_0043d0ce();
              if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
                compress_log_output(0x10400000,DAT_00462550,DAT_00462550,*puVar1);
              }
              FUN_00462db4();
              FUN_00462db6();
              FUN_004612f8();
            }
            else {
              *puVar2 = *puVar2 - 1;
              *puVar1 = *puVar1 - 1;
              uVar9 = FUN_00460d6c(*puVar1);
              iVar4 = FUN_0043d0ce();
              if (iVar4 << 0x1e < 0) {
                local_114 = *puVar2;
                local_118 = *puVar1;
                local_11c = DAT_004624f0;
                local_110 = uVar9;
                FUN_0043d574(4,DAT_00461e90,DAT_00461e8c,DAT_00462370,0x30a);
              }
              iVar4 = FUN_0043d0ce();
              if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
                local_11c = uVar9;
                compress_log_output(0x10c00000,DAT_00462548,DAT_00462548,*puVar1,*puVar2);
              }
              FUN_00462db4();
              FUN_00462db6();
              FUN_00460fc6(*DAT_00461b10,uVar9,200);
            }
          }
          else {
            *puVar1 = *puVar1 - 1;
            iVar4 = FUN_0043d0ce();
            if (iVar4 << 0x1e < 0) {
              local_118 = *puVar1;
              local_11c = DAT_00462450;
              FUN_0043d574(4,DAT_00461e90,DAT_00461e8c,DAT_00462370,0x319);
            }
            iVar4 = FUN_0043d0ce();
            if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
              compress_log_output(0x10400000,DAT_004624ec,DAT_004624ec,*puVar1);
            }
            FUN_00462db4();
            FUN_00462db6();
            FUN_004612f8();
          }
        }
        else {
          *puVar1 = *puVar1 - 1;
          iVar4 = FUN_0043d0ce();
          if (iVar4 << 0x1e < 0) {
            local_118 = *puVar1;
            local_11c = DAT_00462450;
            FUN_0043d574(4,DAT_00461e90,DAT_00461e8c,DAT_00462370,0x2fe);
          }
          iVar4 = FUN_0043d0ce();
          if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
            compress_log_output(0x10400000,DAT_004624ec,DAT_004624ec,*puVar1);
          }
          FUN_00462db4();
          FUN_00462db6();
          FUN_004612f8();
        }
      }
    }
    else if (param_1 == 2) {
      iVar5 = FUN_0043d0ce();
      iVar4 = DAT_0046257c;
      piVar7 = DAT_00462578;
      if (iVar5 << 0x1e < 0) {
        uVar6 = FUN_00460084(*DAT_00462578 * 0x34 + DAT_0046257c + 4);
        local_118 = FUN_0045fffe(*piVar7 * 0x34 + iVar4 + 4,uVar6);
        local_114 = *(uint *)(iVar4 + *piVar7 * 0x34 + 0x24);
        local_11c = DAT_00462580;
        FUN_0043d574(4,DAT_00461e90,DAT_00461e8c,DAT_00462370,0x35d);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        iVar4 = DAT_0046257c;
        piVar7 = DAT_00462578;
        uVar6 = FUN_00460084(*DAT_00462578 * 0x34 + DAT_0046257c + 4);
        uVar6 = FUN_0045fffe(*piVar7 * 0x34 + iVar4 + 4,uVar6);
        compress_log_output(0x10800000,DAT_00462584,DAT_00462584,uVar6,
                            *(undefined4 *)(iVar4 + *piVar7 * 0x34 + 0x24));
      }
      piVar7 = DAT_00462578;
      uVar6 = *(undefined4 *)(DAT_00462588 + *DAT_00462578 * 4);
      FUN_004503d6(&local_78);
      local_74 = DAT_0046258c;
      local_78 = uVar6;
      FUN_004506ce(&local_78,0x140,0x168);
      local_48 = 0x96;
      local_58 = DAT_00462590;
      local_3c = 0x96;
      FUN_00450408(&local_78);
      iVar4 = DAT_0046257c;
      iVar5 = *(int *)(*piVar7 * 0x34 + DAT_0046257c + 0x24);
      if (iVar5 == 1) {
        iVar4 = FUN_0045a568();
        if (iVar4 == 1) {
          FUN_00465748(7,3,0,0);
          service_ancc_state_sync(2,500);
        }
      }
      else if (iVar5 == 2) {
        iVar4 = FUN_0045a568();
        if (iVar4 == 1) {
          FUN_00465748(7,3,0,0);
          piVar7 = (int *)FUN_0045f6b4(*DAT_0046288c);
          if (piVar7 == (int *)0x0) {
            FUN_0045a8ee(0xb,0,0,500);
            local_c0 = *DAT_00462a30;
            uStack_bc = DAT_00462a30[1];
            FUN_0048eb32(DAT_004628a8,2,&local_c0);
          }
          else if (*piVar7 == 0xb) {
            iVar4 = FUN_0043d0ce();
            if (iVar4 << 0x1e < 0) {
              local_11c = DAT_00462a34;
              FUN_0043d574(3,DAT_0046289c,DAT_00462898,DAT_00462370,0x3aa);
            }
            iVar4 = FUN_0043d0ce();
            if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
              compress_log_output(0xc000000,DAT_00462a38,DAT_00462a38);
            }
          }
          else {
            FUN_0045a8ee(0xb,0,0,500);
            local_c8 = *DAT_00462a3c;
            uStack_c4 = DAT_00462a3c[1];
            FUN_0048eb32(DAT_004628a8,2,&local_c8);
          }
        }
      }
      else if (iVar5 == 3) {
        iVar4 = FUN_0045a568();
        if (iVar4 == 1) {
          FUN_00465748(7,3,0,0);
          piVar7 = (int *)FUN_0045f6b4(*DAT_0046288c);
          if (piVar7 == (int *)0x0) {
            FUN_0045a8ee(6,0,0,500);
            local_d0 = *DAT_00462a40;
            uStack_cc = DAT_00462a40[1];
            FUN_0048eb32(DAT_004628a8,2,&local_d0);
          }
          else if (*piVar7 == 6) {
            iVar4 = FUN_0043d0ce();
            if (iVar4 << 0x1e < 0) {
              local_11c = DAT_00462a44;
              FUN_0043d574(3,DAT_0046289c,DAT_00462898,DAT_00462370,0x3bf);
            }
            iVar4 = FUN_0043d0ce();
            if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
              compress_log_output(0xc000000,DAT_00462a48,DAT_00462a48);
            }
          }
          else {
            FUN_0045a8ee(6,0,0,500);
            local_d8 = *DAT_00462a4c;
            uStack_d4 = DAT_00462a4c[1];
            FUN_0048eb32(DAT_004628a8,2,&local_d8);
          }
        }
      }
      else if (iVar5 == 4) {
        iVar4 = FUN_0045a568();
        if (iVar4 == 1) {
          FUN_00465748(7,3,0,0);
          piVar7 = (int *)FUN_0045f6b4(*DAT_0046288c);
          if (piVar7 == (int *)0x0) {
            FUN_0045a8ee(5,0,0,500);
            local_e0 = *DAT_00462a50;
            uStack_dc = DAT_00462a50[1];
            FUN_0048eb32(DAT_004628a8,2,&local_e0);
          }
          else if (*piVar7 == 5) {
            iVar4 = FUN_0043d0ce();
            if (iVar4 << 0x1e < 0) {
              local_11c = DAT_00462a54;
              FUN_0043d574(3,DAT_0046289c,DAT_00462898,DAT_00462370,0x3d3);
            }
            iVar4 = FUN_0043d0ce();
            if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
              compress_log_output(0xc000000,DAT_00462a58,DAT_00462a58);
            }
          }
          else {
            FUN_0045a8ee(5,0,0,500);
            local_e8 = *DAT_00462a5c;
            uStack_e4 = DAT_00462a5c[1];
            FUN_0048eb32(DAT_004628a8,2,&local_e8);
          }
        }
      }
      else if (iVar5 == 5) {
        iVar4 = FUN_0045a568();
        if (iVar4 == 1) {
          FUN_00465748(7,3,0,0);
          piVar7 = (int *)FUN_0045f6b4(*DAT_0046288c);
          if (piVar7 == (int *)0x0) {
            FUN_0045a8ee(8,0,0,500);
            local_f0 = *DAT_00462a60;
            uStack_ec = DAT_00462a60[1];
            FUN_0048eb32(DAT_004628a8,2,&local_f0);
          }
          else if (*piVar7 == 8) {
            iVar4 = FUN_0043d0ce();
            if (iVar4 << 0x1e < 0) {
              local_11c = DAT_00462a64;
              FUN_0043d574(3,DAT_0046289c,DAT_00462898,DAT_00462370,1000);
            }
            iVar4 = FUN_0043d0ce();
            if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
              compress_log_output(0xc000000,DAT_00462a68,DAT_00462a68);
            }
          }
          else {
            FUN_0045a8ee(8,0,0,500);
            local_f8 = *DAT_00462a6c;
            uStack_f4 = DAT_00462a6c[1];
            FUN_0048eb32(DAT_004628a8,2,&local_f8);
          }
        }
      }
      else if (iVar5 == 6) {
        iVar4 = FUN_0045a568();
        if (iVar4 == 1) {
          FUN_00465748(7,3,0,0);
          service_even_ai_fn_0049832e(1,500);
        }
      }
      else if (iVar5 == 7) {
        iVar4 = FUN_0045a568();
        if (iVar4 == 1) {
          FUN_00465748(7,3,0,0);
          piVar7 = (int *)FUN_0045f6b4(*DAT_0046288c);
          if (piVar7 == (int *)0x0) {
            FUN_0045a8ee(1,0,0,500);
          }
          else if (*piVar7 == 1) {
            iVar4 = FUN_0043d0ce();
            if (iVar4 << 0x1e < 0) {
              local_11c = DAT_00462a70;
              FUN_0043d574(3,DAT_0046289c,DAT_00462898,DAT_00462a74,0x410);
            }
            iVar4 = FUN_0043d0ce();
            if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
              compress_log_output(0xc000000,DAT_00462a78,DAT_00462a78);
            }
          }
          else {
            FUN_0045a8ee(1,0,0,500);
          }
        }
      }
      else if (iVar5 == 8) {
        iVar4 = FUN_0045a568();
        if (iVar4 == 1) {
          FUN_00465748(7,3,0,0);
          cVar3 = silent_mode_status_get();
          if (cVar3 == '\0') {
            local_11c = CONCAT31(local_11c._1_3_,1);
          }
          else {
            local_11c = (uint)local_11c._1_3_ << 8;
          }
          FUN_00464f76(0x10a,&local_11c,1,0,4);
        }
      }
      else if (iVar5 == 0xffe) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          local_118 = *(uint *)(*piVar7 * 0x34 + iVar4 + 0x30);
          local_11c = DAT_00462878;
          FUN_0043d574(3,DAT_00461e90,DAT_00461e8c,DAT_00462370,0x36f);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0xc400000,DAT_0046287c,DAT_0046287c,
                              *(undefined4 *)(*piVar7 * 0x34 + iVar4 + 0x30));
        }
        uVar9 = *(uint *)(*piVar7 * 0x34 + iVar4 + 0x30);
        FUN_0043c0e4(&local_b8,0x40,0);
        FUN_0043c0e4(&local_b8,0x40,0);
        local_b8 = 0;
        local_b7 = (undefined1)uVar9;
        local_b6 = (undefined1)(uVar9 >> 8);
        local_b5 = (undefined1)(uVar9 >> 0x10);
        local_b4 = (undefined1)(uVar9 >> 0x18);
        uVar6 = FUN_0044a43c(*piVar7 * 0x34 + iVar4 + 4);
        FUN_00439be4(auStack_b3,iVar4 + *piVar7 * 0x34 + 4,uVar6);
        iVar4 = FUN_0045a568();
        if (iVar4 == 1) {
          FUN_00465748(7,3,0,0);
          piVar7 = (int *)FUN_0045f6b4(*DAT_0046288c);
          if (piVar7 == (int *)0x0) {
            FUN_0045a8ee(0xffe,&local_b8,0x40,500);
          }
          else if (*piVar7 == 0xffe) {
            iVar4 = FUN_0043d0ce();
            if (iVar4 << 0x1e < 0) {
              local_11c = DAT_00462880;
              FUN_0043d574(4,DAT_00461e90,DAT_00461e8c,DAT_00462370,0x381);
            }
            iVar4 = FUN_0043d0ce();
            if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
              compress_log_output(0x10000000,DAT_00462884,DAT_00462884);
            }
            uVar8 = FUN_00492ce6();
            if (uVar8 == uVar9) {
              iVar4 = FUN_0043d0ce();
              if (iVar4 << 0x1e < 0) {
                local_11c = DAT_00462888;
                local_118 = uVar8;
                FUN_0043d574(3,DAT_00461e90,DAT_00461e8c,DAT_00462370,900);
              }
              iVar4 = FUN_0043d0ce();
              if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
                compress_log_output(0xc400000,DAT_00462890,DAT_00462890,uVar8);
              }
            }
            else {
              iVar4 = FUN_0043d0ce();
              if (iVar4 << 0x1e < 0) {
                local_11c = DAT_00462894;
                local_118 = uVar8;
                local_114 = uVar9;
                FUN_0043d574(3,DAT_0046289c,DAT_00462898,DAT_00462370,0x386);
              }
              iVar4 = FUN_0043d0ce();
              if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
                compress_log_output(0xc800000,DAT_004628a0,DAT_004628a0,uVar8,uVar9);
              }
              FUN_00464c36(0xffe,0,0,0);
              FUN_0045a8ee(0xffe,&local_b8,0x40,500);
              uStack_fc = *(undefined4 *)(DAT_004628a4 + 4);
              local_100 = uVar9;
              FUN_0048eb32(DAT_004628a8,2,&local_100);
            }
          }
          else if (*piVar7 == 0xe0) {
            iVar4 = FUN_0043d0ce();
            if (iVar4 << 0x1e < 0) {
              local_11c = DAT_004628ac;
              FUN_0043d574(4,DAT_0046289c,DAT_00462898,DAT_00462370,0x38c);
            }
            iVar4 = FUN_0043d0ce();
            if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
              compress_log_output(0x10000000,DAT_004628b0,DAT_004628b0);
            }
            uVar8 = FUN_004935fe();
            if (uVar8 == uVar9) {
              iVar4 = FUN_0043d0ce();
              if (iVar4 << 0x1e < 0) {
                local_11c = DAT_004628b4;
                local_118 = uVar8;
                FUN_0043d574(3,DAT_0046289c,DAT_00462898,DAT_00462370,0x38f);
              }
              iVar4 = FUN_0043d0ce();
              if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
                compress_log_output(0xc400000,DAT_004628b8,DAT_004628b8,uVar8);
              }
            }
            else {
              iVar4 = FUN_0043d0ce();
              if (iVar4 << 0x1e < 0) {
                local_11c = DAT_004628bc;
                local_118 = uVar8;
                local_114 = uVar9;
                FUN_0043d574(3,DAT_0046289c,DAT_00462898,DAT_00462370,0x391);
              }
              iVar4 = FUN_0043d0ce();
              if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
                compress_log_output(0xc800000,DAT_004628c0,DAT_004628c0,uVar8,uVar9);
              }
              FUN_00464c36(0xe0,0,0,0);
              FUN_0045a8ee(0xffe,&local_b8,0x40,500);
              uStack_104 = *(undefined4 *)(DAT_00462a28 + 4);
              local_108 = uVar9;
              FUN_0048eb32(DAT_004628a8,2,&local_108);
            }
          }
          else {
            FUN_0045a8ee(0xffe,&local_b8,0x40,500);
            uStack_10c = *(undefined4 *)(DAT_00462a2c + 4);
            local_110 = uVar9;
            FUN_0048eb32(DAT_004628a8,2,&local_110);
          }
        }
      }
    }
    else if (param_1 < 2) {
      if ((int)*DAT_00461b70 < *DAT_0046255c + -1) {
        uVar9 = *DAT_00461b70 - *DAT_00462444;
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          local_110 = *puVar2;
          local_118 = *puVar1;
          local_11c = DAT_00462560;
          local_114 = uVar9;
          FUN_0043d574(4,DAT_00461e90,DAT_00461e8c,DAT_00462370,0x32b);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          local_11c = *puVar2;
          compress_log_output(0x10c00000,DAT_00462564,DAT_00462564,*puVar1,uVar9);
        }
        if ((int)uVar9 < 2) {
          *puVar1 = *puVar1 + 1;
          iVar4 = FUN_0043d0ce();
          if (iVar4 << 0x1e < 0) {
            local_118 = *puVar1;
            local_11c = DAT_00462450;
            FUN_0043d574(4,DAT_00461e90,DAT_00461e8c,DAT_00462370,0x330);
          }
          iVar4 = FUN_0043d0ce();
          if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
            compress_log_output(0x10400000,DAT_004624ec,DAT_004624ec,*puVar1);
          }
          FUN_00462db4();
          FUN_00462db6();
          FUN_004612f8();
        }
        else if (uVar9 == 2) {
          iVar4 = *piVar7 + -5;
          if (iVar4 < 0) {
            iVar4 = 0;
          }
          if ((int)*puVar2 < iVar4) {
            *puVar2 = *puVar2 + 1;
            *puVar1 = *puVar1 + 1;
            uVar9 = FUN_00460d6c(*puVar1);
            iVar4 = FUN_0043d0ce();
            if (iVar4 << 0x1e < 0) {
              local_114 = *puVar2;
              local_118 = *puVar1;
              local_11c = DAT_004624f0;
              local_110 = uVar9;
              FUN_0043d574(4,DAT_00461e90,DAT_00461e8c,DAT_00462370,0x33f);
            }
            iVar4 = FUN_0043d0ce();
            if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
              local_11c = uVar9;
              compress_log_output(0x10c00000,DAT_00462548,DAT_00462548,*puVar1,*puVar2);
            }
            FUN_00462db4();
            FUN_00462db6();
            FUN_00460fc6(*DAT_00461b10,uVar9,200);
          }
          else {
            *puVar1 = *puVar1 + 1;
            iVar4 = FUN_0043d0ce();
            if (iVar4 << 0x1e < 0) {
              local_118 = *puVar1;
              local_11c = DAT_00462568;
              FUN_0043d574(4,DAT_00461e90,DAT_00461e8c,DAT_00462370,0x346);
            }
            iVar4 = FUN_0043d0ce();
            if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
              compress_log_output(0x10400000,DAT_0046256c,DAT_0046256c,*puVar1);
            }
            FUN_00462db4();
            FUN_00462db6();
            FUN_004612f8();
          }
        }
        else {
          *puVar1 = *puVar1 + 1;
          iVar4 = FUN_0043d0ce();
          if (iVar4 << 0x1e < 0) {
            local_118 = *puVar1;
            local_11c = DAT_00462450;
            FUN_0043d574(4,DAT_00461e90,DAT_00461e8c,DAT_00462370,0x34e);
          }
          iVar4 = FUN_0043d0ce();
          if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
            compress_log_output(0x10400000,DAT_004624ec,DAT_004624ec,*puVar1);
          }
          FUN_00462db4();
          FUN_00462db6();
          FUN_004612f8();
        }
      }
      else {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          local_11c = DAT_00462570;
          FUN_0043d574(2,DAT_00461e90,DAT_00461e8c,DAT_00462370,0x355);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x8000000,DAT_00462574,DAT_00462574);
        }
        FUN_0046137c(0);
      }
    }
    else if (param_1 == 3) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        local_11c = DAT_00462da8;
        FUN_0043d574(4,DAT_0046289c,DAT_00462898,DAT_00462a74,0x43c);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_00462dac,DAT_00462dac);
      }
    }
    else {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        local_118 = (uint)param_1;
        local_11c = DAT_00462db0;
        FUN_0043d574(2,DAT_0046289c,DAT_00462898,DAT_00462a74,0x43f);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_00463010,DAT_00463010,param_1);
      }
    }
  }
  else {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      local_11c = DAT_0046237c;
      FUN_0043d574(4,DAT_00461e90,DAT_00461e8c,DAT_00462370,0x2ee);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_00462380);
    }
  }
  return;
}

