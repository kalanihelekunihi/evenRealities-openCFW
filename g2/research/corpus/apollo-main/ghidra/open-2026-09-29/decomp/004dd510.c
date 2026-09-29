
int * FUN_004dd510(int param_1,int param_2,int param_3,int param_4)

{
  int iVar1;
  int *piVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  uint uVar5;
  int iVar6;
  int iVar7;
  uint local_54c;
  uint local_548;
  uint local_544;
  uint local_540;
  uint local_53c;
  uint local_538;
  uint local_534;
  uint local_530;
  uint local_52c;
  int local_528;
  undefined1 local_524;
  undefined1 auStack_523 [1283];
  
  if ((param_1 == 0) || (param_2 == 0)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004de154,DAT_004de150,DAT_004de14c,0x1b5,DAT_004de148,param_1,param_2);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4800000,DAT_004de158,DAT_004de158,param_1,param_2);
    }
    piVar2 = (int *)0x0;
  }
  else if ((*(int *)(param_2 + 0x20) == 0) || (0x14 < *(uint *)(param_2 + 0x20))) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004de154,DAT_004de150,DAT_004de14c,0x1bb,DAT_004de15c,
                   *(undefined4 *)(param_2 + 0x20),0x14);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4800000,DAT_004de160,DAT_004de160,*(undefined4 *)(param_2 + 0x20),0x14);
    }
    piVar2 = (int *)0x0;
  }
  else {
    FUN_00439c04(&local_54c,param_2,0x52c);
    if (0x240 < local_54c) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(2,DAT_004de154,DAT_004de150,DAT_004de14c,0x1c4,DAT_004de164,local_54c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_004de168,DAT_004de168,local_54c);
      }
      local_54c = 0x240;
    }
    if (0x120 < local_548) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(2,DAT_004de154,DAT_004de150,DAT_004de14c,0x1ca,DAT_004de16c,local_548);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_004de170,DAT_004de170,local_548);
      }
      local_548 = 0x120;
    }
    if (0x240 < local_544) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(2,DAT_004de154,DAT_004de150,DAT_004de14c,0x1d0,DAT_004de174,local_544);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_004de178,DAT_004de178,local_544);
      }
      local_544 = 0x240;
    }
    if (0x120 < local_540) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(2,DAT_004de154,DAT_004de150,DAT_004de14c,0x1d6,DAT_004de28c,local_540);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_004de290,DAT_004de290,local_540);
      }
      local_540 = 0x120;
    }
    if (5 < local_53c) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(2,DAT_004de154,DAT_004de150,DAT_004de14c,0x1dc,DAT_004de294,local_53c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_004de298,DAT_004de298,local_53c);
      }
      local_53c = 5;
    }
    if (0x10 < local_538) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(2,DAT_004de154,DAT_004de150,DAT_004de14c,0x1e2,DAT_004de29c,local_538);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_004de2a0,DAT_004de2a0,local_538);
      }
      local_538 = 0x10;
    }
    if (10 < local_534) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(2,DAT_004de154,DAT_004de150,DAT_004de14c,0x1e8,DAT_004de2a4,local_534);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_004de2a8,DAT_004de2a8,local_534);
      }
      local_534 = 10;
    }
    if (0x20 < local_530) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(2,DAT_004de154,DAT_004de150,DAT_004de14c,0x1ee,DAT_004de2ac,local_530);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_004de2b0,DAT_004de2b0,local_530);
      }
      local_530 = 0x20;
    }
    if (0x14 < local_52c) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(2,DAT_004de154,DAT_004de150,DAT_004de14c,0x1f5,DAT_004de2b4,local_52c,0x14,0x14
                    );
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8c00000,DAT_004de2b8,DAT_004de2b8,local_52c,0x14,0x14);
      }
      local_52c = 0x14;
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004de154,DAT_004de150,DAT_004de14c,0x1fd,DAT_004de2bc,local_52c,local_54c,
                   local_548,local_544,local_540);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x11400000,DAT_004de2c0,DAT_004de2c0,local_52c,local_54c,local_548,
                          local_544,local_540);
    }
    piVar2 = (int *)file_heap_allocate(0x580);
    if (piVar2 == (int *)0x0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(1,DAT_004de154,DAT_004de150,DAT_004de14c,0x205,DAT_004de2c4);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_004de2c8,DAT_004de2c8);
      }
      piVar2 = (int *)0x0;
    }
    else {
      FUN_0043c0e4(piVar2,0x580,0);
      piVar2[0x16] = local_52c;
      piVar2[0x17] = 0;
      piVar2[0x18] = 0;
      *(undefined1 *)(piVar2 + 0x15f) = 0;
      *(undefined1 *)((int)piVar2 + 0x6d) = local_524;
      for (uVar5 = 0; uVar5 < local_52c; uVar5 = uVar5 + 1) {
        FUN_0044b5a0((int)piVar2 + uVar5 * 0x40 + 0x6e,auStack_523 + uVar5 * 0x40,0x3f);
        *(undefined1 *)((int)piVar2 + uVar5 * 0x40 + 0xad) = 0;
      }
      piVar2[0x15d] = param_3;
      piVar2[0x15e] = param_4;
      piVar2[0x19] = local_530 * -2 + local_540;
      piVar2[0x1a] = piVar2[0x19] / 0x28;
      if (piVar2[0x1a] < 1) {
        piVar2[0x1a] = 1;
      }
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004de154,DAT_004de150,DAT_004de14c,0x222,DAT_004de2cc,piVar2[0x19],
                     piVar2[0x1a],*(undefined1 *)((int)piVar2 + 0x6d));
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10c00000,DAT_004de2d0,DAT_004de2d0,piVar2[0x19],piVar2[0x1a],
                            *(undefined1 *)((int)piVar2 + 0x6d));
      }
      iVar1 = ui_common_api_fn_00509c1c();
      piVar2[0x15c] = iVar1;
      if (piVar2[0x15c] == 0) {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(1,DAT_004de154,DAT_004de150,DAT_004de14c,0x227,DAT_004de2d4);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_004de2d8,DAT_004de2d8);
        }
        file_heap_free(piVar2);
        piVar2 = (int *)0x0;
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004de154,DAT_004de150,DAT_004de14c,0x22b,DAT_004de2dc);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004de2e0,DAT_004de2e0);
        }
        iVar1 = FUN_0043de82(param_1);
        *piVar2 = iVar1;
        if (*piVar2 == 0) {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            FUN_0043d574(1,DAT_004de154,DAT_004de150,DAT_004de14c,0x230,DAT_004de2e4);
          }
          iVar1 = FUN_0043d0ce();
          if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
            compress_log_output(0x4000000,DAT_004de2e8,DAT_004de2e8);
          }
          ui_common_api_fn_00509c96(piVar2[0x15c]);
          file_heap_free(piVar2);
          piVar2 = (int *)0x0;
        }
        else {
          FUN_0043f506(*piVar2,local_544);
          FUN_0043f568(*piVar2,local_540);
          FUN_0043f0e0(*piVar2,local_54c);
          FUN_0043f142(*piVar2,local_548);
          FUN_0044e368(*piVar2,0);
          FUN_0044e3ca(*piVar2,0xc);
          FUN_0044129e(*piVar2,0,0);
          FUN_0044146a(*piVar2,local_534,0);
          if (local_53c == 0) {
            FUN_0044131c(*piVar2,0,0);
          }
          else {
            FUN_0044131c(*piVar2,local_53c,0);
            uVar3 = FUN_004dcd32(local_538);
            uVar4 = FUN_0044104c(uVar3);
            FUN_004412ec(*piVar2,uVar4,0);
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              FUN_0043d574(4,DAT_004de154,DAT_004de150,DAT_004de14c,0x245,DAT_004de2ec,local_53c,
                           uVar3);
            }
            iVar1 = FUN_0043d0ce();
            if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
              compress_log_output(0x10800000,DAT_004de2f0,DAT_004de2f0,local_53c,uVar3);
            }
          }
          FUN_0044120e(*piVar2,local_530,0);
          FUN_0044121c(*piVar2,local_530,0);
          FUN_0044122a(*piVar2,local_530,0);
          FUN_00441238(*piVar2,local_530,0);
          uVar5 = local_52c;
          iVar6 = local_52c * 0x28;
          iVar7 = local_530 * -2 + local_540;
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            FUN_0043d574(4,DAT_004de154,DAT_004de150,DAT_004de14c,600,DAT_004de2f4,iVar6,iVar7,uVar5
                        );
          }
          iVar1 = FUN_0043d0ce();
          if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
            compress_log_output(0x10c00000,DAT_004de2f8,DAT_004de2f8,iVar6,iVar7,uVar5);
          }
          if (iVar7 < iVar6) {
            if (iVar7 % 0x28 < 0 == SBORROW4(iVar7,(iVar7 / 0x28) * 0x28)) {
              iVar1 = 0;
            }
            else {
              iVar1 = 0x2c;
            }
            iVar1 = iVar1 + 0x10;
            iVar7 = iVar1 + iVar6;
            *(undefined1 *)(piVar2 + 0x1b) = 0;
            iVar6 = FUN_0043d0ce();
            if (iVar6 << 0x1e < 0) {
              FUN_0043d574(4,DAT_004de154,DAT_004de150,DAT_004de14c,0x26a,DAT_004de304,iVar7,iVar1);
            }
            iVar6 = FUN_0043d0ce();
            if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
              compress_log_output(0x10800000,DAT_004de308,DAT_004de308,iVar7,iVar1);
            }
          }
          else {
            iVar7 = iVar7 + 0x10;
            *(undefined1 *)(piVar2 + 0x1b) = 1;
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              FUN_0043d574(4,DAT_004de154,DAT_004de150,DAT_004de14c,0x25f,DAT_004de2fc,iVar7);
            }
            iVar1 = FUN_0043d0ce();
            if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
              compress_log_output(0x10400000,DAT_004de300,DAT_004de300,iVar7);
            }
          }
          iVar1 = FUN_0043de82(*piVar2);
          piVar2[1] = iVar1;
          if (piVar2[1] == 0) {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              FUN_0043d574(1,DAT_004de154,DAT_004de150,DAT_004de14c,0x26f,DAT_004de30c);
            }
            iVar1 = FUN_0043d0ce();
            if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
              compress_log_output(0x4000000,DAT_004de310,DAT_004de310);
            }
            FUN_0044d7b8(*piVar2);
            ui_common_api_fn_00509c96(piVar2[0x15c]);
            file_heap_free(piVar2);
            piVar2 = (int *)0x0;
          }
          else {
            FUN_0043f506(piVar2[1],local_544);
            FUN_0043f568(piVar2[1],iVar7);
            FUN_0043f0e0(piVar2[1],0);
            FUN_0043f142(piVar2[1],0);
            FUN_0044129e(piVar2[1],0,0);
            FUN_0044131c(piVar2[1],0,0);
            FUN_004dccd8(piVar2[1],0,0);
            FUN_0043dfa4(piVar2[1],0x10);
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              FUN_0043d574(4,DAT_004de154,DAT_004de150,DAT_004de14c,0x281,DAT_004de314,uVar5);
            }
            iVar1 = FUN_0043d0ce();
            if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
              compress_log_output(0x10400000,DAT_004de318,DAT_004de318,uVar5);
            }
            for (iVar1 = 0; iVar1 < (int)uVar5; iVar1 = iVar1 + 1) {
              iVar6 = FUN_0043de82(piVar2[1]);
              piVar2[iVar1 + 2] = iVar6;
              if (piVar2[iVar1 + 2] == 0) {
                iVar6 = FUN_0043d0ce();
                if (iVar6 << 0x1e < 0) {
                  FUN_0043d574(1,DAT_004de154,DAT_004de150,DAT_004de14c,0x287,DAT_004de324,iVar1);
                }
                iVar6 = FUN_0043d0ce();
                if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
                  compress_log_output(0x4400000,DAT_004de328,DAT_004de328,iVar1);
                }
                FUN_0044d7b8(*piVar2);
                ui_common_api_fn_00509c96(piVar2[0x15c]);
                file_heap_free(piVar2);
                return (int *)0x0;
              }
              FUN_0044122a(piVar2[iVar1 + 2],0xc,0);
              FUN_00441238(piVar2[iVar1 + 2],0xc,0);
              if (local_528 == 0) {
                FUN_0043f4c0(piVar2[iVar1 + 2],0x3fffffff,0x28);
              }
              else {
                FUN_0043f4c0(piVar2[iVar1 + 2],local_528,0x28);
              }
              FUN_0043f0e0(piVar2[iVar1 + 2],0);
              uVar3 = FUN_004dcd0a(piVar2,iVar1);
              FUN_0043f142(piVar2[iVar1 + 2],uVar3);
              uVar3 = FUN_0044104c(0);
              FUN_0044127e(piVar2[iVar1 + 2],uVar3,0);
              FUN_0044129e(piVar2[iVar1 + 2],0,0);
              FUN_0044146a(piVar2[iVar1 + 2],10,0);
              FUN_0044131c(piVar2[iVar1 + 2],0,0);
              FUN_0043dfa4(piVar2[iVar1 + 2],0x10);
              uVar3 = FUN_00499416(piVar2[iVar1 + 2]);
              FUN_0049942e(uVar3,auStack_523 + iVar1 * 0x40);
              FUN_0044143e(uVar3,*DAT_004de320,0);
              if (local_528 == 0) {
                iVar6 = local_544 - 0x18;
                FUN_0043f506(uVar3,0x3fffffff);
                FUN_00441180(uVar3,iVar6,0);
                FUN_00499678(uVar3,1);
              }
              else {
                FUN_0043f506(uVar3,local_528 + -0x18);
                FUN_0043f568(uVar3,0x3fffffff);
                FUN_004411aa(uVar3,0x28,0);
                FUN_00499678(uVar3,1);
              }
              FUN_004409fa(uVar3);
              if (iVar1 == 0) {
                uVar4 = FUN_0044104c(0xffffff);
                FUN_0044140e(uVar3,uVar4,0);
              }
              else {
                uVar4 = FUN_0044104c(DAT_004de31c);
                FUN_0044140e(uVar3,uVar4,0);
              }
            }
            FUN_0043f66c(param_1);
            FUN_0044ea04(*piVar2,0,0);
            FUN_004dcdbe(piVar2);
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              FUN_0043d574(4,DAT_004de154,DAT_004de150,DAT_004de14c,0x2da,DAT_004de32c,
                           *(undefined1 *)((int)piVar2 + 0x6d));
            }
            iVar1 = FUN_0043d0ce();
            if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
              compress_log_output(0x10400000,DAT_004de330,DAT_004de330,
                                  *(undefined1 *)((int)piVar2 + 0x6d));
            }
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              FUN_0043d574(3,DAT_004de154,DAT_004de150,DAT_004de14c,0x2dd,DAT_004de334,uVar5,
                           local_54c,local_548);
            }
            iVar1 = FUN_0043d0ce();
            if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
              compress_log_output(0xcc00000,DAT_004de338,DAT_004de338,uVar5,local_54c,local_548);
            }
          }
        }
      }
    }
  }
  return piVar2;
}

