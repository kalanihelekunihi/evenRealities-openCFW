
undefined4 semantic_CodecLoadFirmwarePackage(void)

{
  bool bVar1;
  bool bVar2;
  int *piVar3;
  int *piVar4;
  int *piVar5;
  int *piVar6;
  int *piVar7;
  int iVar8;
  undefined4 uVar9;
  int iVar10;
  undefined4 uVar11;
  uint uVar12;
  int local_5c;
  undefined4 local_58;
  undefined4 local_54;
  undefined4 local_50;
  int local_4c;
  undefined4 local_48;
  uint local_44;
  undefined1 auStack_3c [4];
  int local_38;
  undefined4 local_34;
  int local_30;
  undefined1 auStack_2c [4];
  int local_28;
  undefined4 local_24;
  int local_20;
  
  FUN_0043c0e4(auStack_2c,0x10,0);
  FUN_0043c0e4(auStack_3c,0x10,0);
  bVar2 = false;
  bVar1 = false;
  iVar8 = FUN_0043d0ce();
  if (iVar8 << 0x1e < 0) {
    FUN_0043d574(4,DAT_005787e8,DAT_005787e4,DAT_005787e0,0x55,DAT_005787dc,DAT_005787d8);
  }
  iVar8 = FUN_0043d0ce();
  if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_005787ec,DAT_005787ec,DAT_005787d8);
  }
  piVar3 = DAT_005787f0;
  uVar9 = DAT_005787d8;
  iVar8 = file_open(DAT_005787d8,&DAT_005780dc);
  *piVar3 = iVar8;
  if (*piVar3 == 0) {
    iVar8 = FUN_0043d0ce();
    if (iVar8 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005787e8,DAT_005787e4,DAT_005787e0,0x5b,DAT_005787f4,uVar9,0xffffffff);
    }
    iVar8 = FUN_0043d0ce();
    if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
      compress_log_output(0x4800000,DAT_005787f8,DAT_005787f8,uVar9,0xffffffff);
    }
    uVar9 = 0xffffffff;
  }
  else {
    iVar10 = file_read(&local_4c,1,0x10,*piVar3);
    iVar8 = DAT_00578804;
    if (iVar10 == 0x10) {
      if (local_4c == DAT_00578804) {
        iVar8 = FUN_0043d0ce();
        if (iVar8 << 0x1e < 0) {
          FUN_0043d574(4,DAT_005787e8,DAT_005787e4,DAT_005787e0,0x6e,DAT_00578a68,local_48,local_44)
          ;
        }
        iVar8 = FUN_0043d0ce();
        if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
          compress_log_output(0x10800000,DAT_00578a88,DAT_00578a88,local_48,local_44);
        }
        for (uVar12 = 0; piVar4 = DAT_00578c54, uVar12 < local_44; uVar12 = uVar12 + 1) {
          iVar8 = file_read(&local_5c,1,0x10,*piVar3);
          if (iVar8 != 0x10) {
            iVar8 = FUN_0043d0ce();
            if (iVar8 << 0x1e < 0) {
              FUN_0043d574(1,DAT_005787e8,DAT_005787e4,DAT_005787e0,0x76,DAT_00578a9c,uVar12);
            }
            iVar8 = FUN_0043d0ce();
            if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
              compress_log_output(0x4800000,DAT_00578aa0,DAT_00578aa0,uVar12);
            }
            if (*piVar3 != 0) {
              file_close(*piVar3);
              *piVar3 = 0;
            }
            return 0xffffffff;
          }
          if (local_5c == 1) {
            FUN_00439c04(auStack_2c,&local_5c,0x10);
            bVar2 = true;
            iVar8 = FUN_0043d0ce();
            if (iVar8 << 0x1e < 0) {
              FUN_0043d574(4,DAT_005787e8,DAT_005787e4,DAT_005787e0,0x7f,DAT_00578a94,local_58,
                           local_54,local_50);
            }
            iVar8 = FUN_0043d0ce();
            if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
              compress_log_output(0x10c00000,DAT_00578a98,DAT_00578a98,local_58,local_54,local_50);
            }
          }
          else if (local_5c == 2) {
            FUN_00439c04(auStack_3c,&local_5c,0x10);
            bVar1 = true;
            iVar8 = FUN_0043d0ce();
            if (iVar8 << 0x1e < 0) {
              FUN_0043d574(4,DAT_005787e8,DAT_005787e4,DAT_005787e0,0x84,DAT_00578a8c,local_58,
                           local_54,local_50);
            }
            iVar8 = FUN_0043d0ce();
            if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
              compress_log_output(0x10c00000,DAT_00578a90,DAT_00578a90,local_58,local_54,local_50);
            }
          }
        }
        if ((bool)(bVar2 & bVar1)) {
          *DAT_00578c54 = local_28;
          piVar5 = DAT_00578c58;
          iVar8 = file_heap_allocate(*piVar4);
          *piVar5 = iVar8;
          if (*piVar5 == 0) {
            iVar8 = FUN_0043d0ce();
            if (iVar8 << 0x1e < 0) {
              FUN_0043d574(1,DAT_005787e8,DAT_005787e4,DAT_005787e0,0x93,DAT_00578c5c,*piVar4);
            }
            iVar8 = FUN_0043d0ce();
            if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
              compress_log_output(0x4400000,DAT_00578c60,DAT_00578c60,*piVar4);
            }
            if (*piVar3 != 0) {
              file_close(*piVar3);
              *piVar3 = 0;
            }
            uVar9 = 0xffffffff;
          }
          else {
            file_seek(*piVar3,local_24,0);
            iVar8 = file_read(*piVar5,1,*piVar4,*piVar3);
            if (iVar8 == *piVar4) {
              iVar8 = FUN_0058faac(*piVar5,*piVar4);
              piVar6 = DAT_00578c74;
              if (iVar8 == local_20) {
                *DAT_00578c74 = local_38;
                piVar7 = DAT_00578c78;
                iVar8 = file_heap_allocate(*piVar6);
                *piVar7 = iVar8;
                if (*piVar7 == 0) {
                  iVar8 = FUN_0043d0ce();
                  if (iVar8 << 0x1e < 0) {
                    FUN_0043d574(1,DAT_005787e8,DAT_005787e4,DAT_005787e0,0xb0,DAT_00578c7c,*piVar6)
                    ;
                  }
                  iVar8 = FUN_0043d0ce();
                  if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
                    compress_log_output(0x4400000,DAT_00578c80,DAT_00578c80,*piVar6);
                  }
                  file_heap_free(*piVar5);
                  *piVar5 = 0;
                  if (*piVar3 != 0) {
                    file_close(*piVar3);
                    *piVar3 = 0;
                  }
                  uVar9 = 0xffffffff;
                }
                else {
                  file_seek(*piVar3,local_34,0);
                  iVar8 = file_read(*piVar7,1,*piVar6,*piVar3);
                  if (iVar8 == *piVar6) {
                    iVar8 = FUN_0058faac(*piVar7,*piVar6);
                    if (iVar8 == local_30) {
                      if (*piVar3 != 0) {
                        file_close(*piVar3);
                        *piVar3 = 0;
                      }
                      iVar8 = FUN_0043d0ce();
                      if (iVar8 << 0x1e < 0) {
                        FUN_0043d574(3,DAT_005787e8,DAT_005787e4,DAT_005787e0,0xd1,DAT_00578c94,
                                     *piVar4,*piVar6);
                      }
                      iVar8 = FUN_0043d0ce();
                      if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
                        compress_log_output(0xc800000,DAT_0057912c,DAT_0057912c,*piVar4,*piVar6);
                      }
                      uVar9 = 0;
                    }
                    else {
                      iVar10 = FUN_0043d0ce();
                      if (iVar10 << 0x1e < 0) {
                        FUN_0043d574(1,DAT_005787e8,DAT_005787e4,DAT_005787e0,0xc6,DAT_00578c8c,
                                     iVar8,local_30);
                      }
                      iVar10 = FUN_0043d0ce();
                      if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
                        compress_log_output(0x4800000,DAT_00578c90,DAT_00578c90,iVar8,local_30);
                      }
                      file_heap_free(*piVar5);
                      file_heap_free(*piVar7);
                      *piVar5 = 0;
                      *piVar7 = 0;
                      if (*piVar3 != 0) {
                        file_close(*piVar3);
                        *piVar3 = 0;
                      }
                      uVar9 = 0xffffffff;
                    }
                  }
                  else {
                    iVar8 = FUN_0043d0ce();
                    if (iVar8 << 0x1e < 0) {
                      FUN_0043d574(1,DAT_005787e8,DAT_005787e4,DAT_005787e0,0xba,DAT_00578c84);
                    }
                    iVar8 = FUN_0043d0ce();
                    if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
                      compress_log_output(0x4800000,DAT_00578c88,DAT_00578c88);
                    }
                    file_heap_free(*piVar5);
                    file_heap_free(*piVar7);
                    *piVar5 = 0;
                    *piVar7 = 0;
                    if (*piVar3 != 0) {
                      file_close(*piVar3);
                      *piVar3 = 0;
                    }
                    uVar9 = 0xffffffff;
                  }
                }
              }
              else {
                iVar10 = FUN_0043d0ce();
                if (iVar10 << 0x1e < 0) {
                  FUN_0043d574(1,DAT_005787e8,DAT_005787e4,DAT_005787e0,0xa5,DAT_00578c6c,iVar8,
                               local_20);
                }
                iVar10 = FUN_0043d0ce();
                if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
                  compress_log_output(0x4800000,DAT_00578c70,DAT_00578c70,iVar8,local_20);
                }
                file_heap_free(*piVar5);
                *piVar5 = 0;
                if (*piVar3 != 0) {
                  file_close(*piVar3);
                  *piVar3 = 0;
                }
                uVar9 = 0xffffffff;
              }
            }
            else {
              iVar8 = FUN_0043d0ce();
              if (iVar8 << 0x1e < 0) {
                FUN_0043d574(1,DAT_005787e8,DAT_005787e4,DAT_005787e0,0x9b,DAT_00578c64);
              }
              iVar8 = FUN_0043d0ce();
              if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
                compress_log_output(0x4800000,DAT_00578c68,DAT_00578c68);
              }
              file_heap_free(*piVar5);
              *piVar5 = 0;
              if (*piVar3 != 0) {
                file_close(*piVar3);
                *piVar3 = 0;
              }
              uVar9 = 0xffffffff;
            }
          }
        }
        else {
          iVar8 = FUN_0043d0ce();
          if (iVar8 << 0x1e < 0) {
            uVar9 = DAT_00578aa8;
            if (bVar1) {
              uVar9 = DAT_00578aa4;
            }
            uVar11 = DAT_00578aa8;
            if (bVar2) {
              uVar11 = DAT_00578aa4;
            }
            FUN_0043d574(1,DAT_005787e8,DAT_005787e4,DAT_005787e0,0x8a,DAT_00578c4c,uVar11,uVar9);
          }
          iVar8 = FUN_0043d0ce();
          if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
            uVar9 = DAT_00578aa8;
            if (bVar1) {
              uVar9 = DAT_00578aa4;
            }
            uVar11 = DAT_00578aa8;
            if (bVar2) {
              uVar11 = DAT_00578aa4;
            }
            compress_log_output(0x4800000,DAT_00578c50,DAT_00578c50,uVar11,uVar9);
          }
          if (*piVar3 != 0) {
            file_close(*piVar3);
            *piVar3 = 0;
          }
          uVar9 = 0xffffffff;
        }
      }
      else {
        iVar10 = FUN_0043d0ce();
        if (iVar10 << 0x1e < 0) {
          FUN_0043d574(1,DAT_005787e8,DAT_005787e4,DAT_005787e0,0x69,DAT_00578808,local_4c,iVar8);
        }
        iVar10 = FUN_0043d0ce();
        if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
          compress_log_output(0x4800000,DAT_0057880c,DAT_0057880c,local_4c,iVar8);
        }
        if (*piVar3 != 0) {
          file_close(*piVar3);
          *piVar3 = 0;
        }
        uVar9 = 0xffffffff;
      }
    }
    else {
      iVar8 = FUN_0043d0ce();
      if (iVar8 << 0x1e < 0) {
        FUN_0043d574(1,DAT_005787e8,DAT_005787e4,DAT_005787e0,0x62,DAT_005787fc);
      }
      iVar8 = FUN_0043d0ce();
      if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_00578800,DAT_00578800);
      }
      if (*piVar3 != 0) {
        file_close(*piVar3);
        *piVar3 = 0;
      }
      uVar9 = 0xffffffff;
    }
  }
  return uVar9;
}

