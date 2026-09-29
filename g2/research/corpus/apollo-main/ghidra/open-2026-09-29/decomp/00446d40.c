
void _fileRawDataParse(undefined4 param_1,uint param_2)

{
  bool bVar1;
  char *pcVar2;
  int *piVar3;
  int *piVar4;
  undefined4 uVar5;
  char cVar6;
  undefined1 uVar7;
  uint uVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  uint uVar12;
  uint uVar13;
  undefined1 auStack_1024 [4096];
  
  piVar3 = DAT_0044786c;
  pcVar2 = DAT_00447114;
  if (*(char *)((int)DAT_0044786c + 0x6d) == '\x01') {
    uVar8 = *(uint *)(DAT_00447114 + 0x28);
    if (uVar8 == 0) {
      iVar9 = FUN_0043d0ce();
      if (iVar9 << 0x1e < 0) {
        FUN_0043d574(4,DAT_00447a24,DAT_00447a20,DAT_00447a1c,0x574,DAT_004471b0);
      }
      iVar9 = FUN_0043d0ce();
      if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_00447210,DAT_00447210);
      }
      if (*(int *)(pcVar2 + 0x3c) == 0) {
        FUN_00439be4(pcVar2 + 0x40,param_1,0x20);
      }
      if (*(int *)(pcVar2 + 0x2c) == 0) {
        if ((*pcVar2 != '\x01') || (*(int *)(pcVar2 + 0x38) == 0)) {
          iVar9 = FUN_0043d0ce();
          if (iVar9 << 0x1e < 0) {
            FUN_0043d574(1,DAT_00447a24,DAT_00447a20,DAT_00447a1c,0x583,DAT_00447a28,*pcVar2,
                         *(undefined4 *)(pcVar2 + 0x38));
          }
          iVar9 = FUN_0043d0ce();
          if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
            compress_log_output(0x4800000,DAT_00447a2c,DAT_00447a2c,*pcVar2,
                                *(undefined4 *)(pcVar2 + 0x38));
          }
          _evenOtaReplyToAPP(0xc1,2,6);
          return;
        }
        cVar6 = semantic_OtaBufferedFlashWrite
                          (param_2 & 0xffff,param_1,
                           *(int *)(pcVar2 + 0x3c) + *(int *)(pcVar2 + 0x38),
                           param_2 + *(int *)(pcVar2 + 0x3c) == *(int *)(pcVar2 + 0xc));
        if (cVar6 == '\x01') {
          FUN_0047cbc4(param_1,param_2,piVar3 + 0x17);
          *(uint *)(pcVar2 + 0x3c) = param_2 + *(int *)(pcVar2 + 0x3c);
          piVar3[0x19] = param_2 + piVar3[0x19];
          _evenOtaReplyToAPP(0xc1,2,0);
          if (piVar3[0x16] != 0) {
            uVar7 = FUN_0047cc60((int)((ulonglong)(uint)piVar3[0x19] * 100),
                                 (int)((ulonglong)(uint)piVar3[0x19] * 100 >> 0x20),piVar3[0x16],0);
            *(undefined1 *)(piVar3 + 0x1b) = uVar7;
          }
          piVar4 = DAT_00447a30;
          iVar9 = osKernelGetTickCount();
          *piVar4 = iVar9;
          iVar9 = FUN_0043d0ce();
          if (iVar9 << 0x1e < 0) {
            FUN_0043d574(4,DAT_00447a24,DAT_00447a20,DAT_00447a1c,0x59d,DAT_00447a3c,
                         (char)piVar3[0x1b],*piVar4 - *DAT_00447a34,
                         (param_2 * 1000 >> 10) / (uint)(*piVar4 - *DAT_00447a38),
                         ((uint)(piVar3[0x19] * 1000) >> 10) / (uint)(*piVar4 - *DAT_00447a34));
          }
          iVar9 = FUN_0043d0ce();
          if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
            compress_log_output(0x11000000,DAT_00447a40,DAT_00447a40,(char)piVar3[0x1b],
                                *piVar4 - *DAT_00447a34,
                                (param_2 * 1000 >> 10) / (uint)(*piVar4 - *DAT_00447a38),
                                ((uint)(piVar3[0x19] * 1000) >> 10) /
                                (uint)(*piVar4 - *DAT_00447a34));
          }
        }
        else {
          _evenOtaReplyToAPP(0xc1,2,6);
        }
      }
    }
    else if (uVar8 == 2) {
      iVar9 = FUN_0043d0ce();
      if (iVar9 << 0x1e < 0) {
        FUN_0043d574(4,DAT_00447a24,DAT_00447a20,DAT_00447a1c,0x5ad,DAT_004474bc);
      }
      iVar9 = FUN_0043d0ce();
      if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004474c0,DAT_004474c0);
      }
    }
    else if (uVar8 < 2) {
      iVar9 = FUN_0043d0ce();
      if (iVar9 << 0x1e < 0) {
        FUN_0043d574(4,DAT_00447a24,DAT_00447a20,DAT_00447a1c,0x5a8,DAT_004474b4);
      }
      iVar9 = FUN_0043d0ce();
      if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004474b8,DAT_004474b8);
      }
    }
    else if (uVar8 == 4) {
      iVar9 = FUN_0043d0ce();
      if (iVar9 << 0x1e < 0) {
        FUN_0043d574(4,DAT_00447a24,DAT_00447a20,DAT_00447a1c,0x5b7,DAT_00447558);
      }
      iVar9 = FUN_0043d0ce();
      if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_0044755c,DAT_0044755c);
      }
    }
    else if (uVar8 < 4) {
      iVar9 = FUN_0043d0ce();
      if (iVar9 << 0x1e < 0) {
        FUN_0043d574(4,DAT_00447a24,DAT_00447a20,DAT_00447a1c,0x5b2,DAT_00447550);
      }
      iVar9 = FUN_0043d0ce();
      if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_00447554,DAT_00447554);
      }
    }
    else if (uVar8 == 6) {
      iVar9 = FUN_0043d0ce();
      if (iVar9 << 0x1e < 0) {
        FUN_0043d574(4,DAT_00447a24,DAT_00447a20,DAT_00447a1c,0x5c1,DAT_00447a44);
      }
      iVar9 = FUN_0043d0ce();
      if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_00447a48,DAT_00447a48);
      }
    }
    else if (uVar8 < 6) {
      iVar9 = FUN_0043d0ce();
      if (iVar9 << 0x1e < 0) {
        FUN_0043d574(4,DAT_00447a24,DAT_00447a20,DAT_00447a1c,0x5bc,DAT_00447560);
      }
      iVar9 = FUN_0043d0ce();
      if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_00447564,DAT_00447564);
      }
    }
    if (*(int *)(pcVar2 + 0x2c) == 3) {
      osKernelGetTickCount();
      uVar8 = file_write(param_1,1,param_2,*piVar3);
      if (uVar8 == param_2) {
        file_seek(*piVar3,piVar3[0x19],0);
        uVar5 = DAT_00447a4c;
        uVar8 = file_read(DAT_00447a4c,1,param_2,*piVar3);
        if (uVar8 == param_2) {
          iVar9 = FUN_004751c8(uVar5,param_1,param_2);
          if (iVar9 == 0) {
            bVar1 = true;
          }
          else {
            bVar1 = false;
          }
        }
        else {
          bVar1 = false;
          iVar9 = FUN_0043d0ce();
          if (iVar9 << 0x1e < 0) {
            FUN_0043d574(1,DAT_00447a24,DAT_00447a20,DAT_00447a1c,0x5d6,DAT_00447a50,param_2,uVar8);
          }
          iVar9 = FUN_0043d0ce();
          if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
            compress_log_output(0x4800000,DAT_00447a54,DAT_00447a54,param_2,uVar8);
          }
        }
      }
      else {
        bVar1 = false;
        iVar9 = FUN_0043d0ce();
        if (iVar9 << 0x1e < 0) {
          FUN_0043d574(1,DAT_00447a24,DAT_00447a20,DAT_00447a1c,0x5da,DAT_00447a58,param_2,uVar8);
        }
        iVar9 = FUN_0043d0ce();
        if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
          compress_log_output(0x4800000,DAT_00447a5c,DAT_00447a5c,param_2,uVar8);
        }
      }
      osKernelGetTickCount();
      if (bVar1) {
        FUN_0047cbc4(param_1,param_2,piVar3 + 0x17);
        *(uint *)(pcVar2 + 0x3c) = param_2 + *(int *)(pcVar2 + 0x3c);
        piVar3[0x19] = param_2 + piVar3[0x19];
        _evenOtaReplyToAPP(0xc1,2,0);
        if (piVar3[0x16] != 0) {
          uVar7 = FUN_0047cc60((int)((ulonglong)(uint)piVar3[0x19] * 100),
                               (int)((ulonglong)(uint)piVar3[0x19] * 100 >> 0x20),piVar3[0x16],0);
          *(undefined1 *)(piVar3 + 0x1b) = uVar7;
        }
        piVar4 = DAT_00447a30;
        iVar9 = osKernelGetTickCount();
        *piVar4 = iVar9;
        iVar9 = FUN_0043d0ce();
        if (iVar9 << 0x1e < 0) {
          FUN_0043d574(4,DAT_00447a24,DAT_00447a20,DAT_00447a1c,0x5ec,DAT_00447a3c,
                       (char)piVar3[0x1b],*piVar4 - *DAT_00447a34,
                       (param_2 * 1000 >> 10) / (uint)(*piVar4 - *DAT_00447a38),
                       ((uint)(piVar3[0x19] * 1000) >> 10) / (uint)(*piVar4 - *DAT_00447a34));
        }
        iVar9 = FUN_0043d0ce();
        if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
          compress_log_output(0x11000000,DAT_00447a40,DAT_00447a40,(char)piVar3[0x1b],
                              *piVar4 - *DAT_00447a34,
                              (param_2 * 1000 >> 10) / (uint)(*piVar4 - *DAT_00447a38),
                              ((uint)(piVar3[0x19] * 1000) >> 10) / (uint)(*piVar4 - *DAT_00447a34))
          ;
        }
      }
      else {
        iVar9 = FUN_0043d0ce();
        if (iVar9 << 0x1e < 0) {
          FUN_0043d574(1,DAT_00447a24,DAT_00447a20,DAT_00447a1c,0x5f0,DAT_00447e94);
        }
        iVar9 = FUN_0043d0ce();
        if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_00447e98,DAT_00447e98);
        }
        if ((char)piVar3[1] == '\x01') {
          if (*piVar3 == 0) {
            iVar9 = 0;
          }
          else {
            iVar9 = file_close(*piVar3);
            *piVar3 = 0;
          }
          if (iVar9 < 0) {
            iVar10 = FUN_0043d0ce();
            if (iVar10 << 0x1e < 0) {
              FUN_0043d574(1,DAT_00447a24,DAT_00447a20,DAT_00447a1c,0x5f7,DAT_00447e9c,
                           (int)piVar3 + 5,iVar9);
            }
            iVar10 = FUN_0043d0ce();
            if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
              compress_log_output(0x4800000,DAT_00447ea0,DAT_00447ea0,(int)piVar3 + 5,iVar9);
            }
          }
          *(undefined1 *)(piVar3 + 1) = 0;
        }
        iVar10 = (int)piVar3 + 5;
        iVar9 = file_remove(iVar10);
        if ((iVar9 < 0) && (iVar9 != -2)) {
          iVar11 = FUN_0043d0ce();
          if (iVar11 << 0x1e < 0) {
            FUN_0043d574(1,DAT_00447a24,DAT_00447a20,DAT_00447a1c,0x5fe,DAT_00447ea4,iVar10,iVar9);
          }
          iVar11 = FUN_0043d0ce();
          if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
            compress_log_output(0x4800000,DAT_00447ea8,DAT_00447ea8,iVar10,iVar9);
          }
        }
        *pcVar2 = '\0';
        piVar3[0x19] = 0;
        pcVar2[0x3c] = '\0';
        pcVar2[0x3d] = '\0';
        pcVar2[0x3e] = '\0';
        pcVar2[0x3f] = '\0';
        piVar3[0x17] = 0;
        _evenOtaReplyToAPP(0xc1,2,6);
      }
    }
    else if (*(int *)(pcVar2 + 0x2c) == 1) {
      iVar9 = osKernelGetTickCount();
      uVar8 = *(int *)(pcVar2 + 0x3c) + *(int *)(pcVar2 + 0x38);
      iVar10 = FUN_0043d0ce();
      if (iVar10 << 0x1e < 0) {
        FUN_0043d574(4,DAT_00447a24,DAT_00447a20,DAT_00447a1c,0x60e,DAT_00447eac,uVar8,
                     *(undefined4 *)(pcVar2 + 0x3c),param_2);
      }
      iVar10 = FUN_0043d0ce();
      if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
        compress_log_output(0x10c00000,DAT_00447eb0,DAT_00447eb0,uVar8,
                            *(undefined4 *)(pcVar2 + 0x3c),param_2);
      }
      uVar13 = uVar8 & 0xfffff000;
      uVar12 = param_2 + uVar8 & 0xfffff000;
      iVar10 = 0;
      if ((uVar8 & 0xfff) == 0) {
        iVar10 = FUN_0043d0ce();
        if (iVar10 << 0x1e < 0) {
          FUN_0043d574(4,DAT_00447a24,DAT_00447a20,DAT_00447a1c,0x61b,DAT_00447eb4,uVar8);
        }
        iVar10 = FUN_0043d0ce();
        if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
          compress_log_output(0x10400000,DAT_00447eb8,DAT_00447eb8,uVar8);
        }
        iVar10 = FUN_0047075c(uVar8);
        if (iVar10 != 0) {
          iVar9 = FUN_0043d0ce();
          if (iVar9 << 0x1e < 0) {
            FUN_0043d574(1,DAT_00447a24,DAT_00447a20,DAT_00447a1c,0x61e,DAT_00447ebc,uVar8,iVar10);
          }
          iVar9 = FUN_0043d0ce();
          if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
            compress_log_output(0x4800000,DAT_00447ec0,DAT_00447ec0,uVar8,iVar10);
          }
          _evenOtaReplyToAPP(0xc1,2,6);
          return;
        }
        iVar10 = FUN_0043d0ce();
        if (iVar10 << 0x1e < 0) {
          FUN_0043d574(4,DAT_00447a24,DAT_00447a20,DAT_00447a1c,0x622,DAT_00447ec4,uVar8);
        }
        iVar10 = FUN_0043d0ce();
        if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
          compress_log_output(0x10400000,DAT_00447ec8,DAT_00447ec8,uVar8);
        }
        iVar10 = 1;
      }
      if (uVar13 < uVar12) {
        while (uVar13 = uVar13 + 0x1000, uVar13 <= uVar12) {
          iVar11 = FUN_0043d0ce();
          if (iVar11 << 0x1e < 0) {
            FUN_0043d574(4,DAT_00447a24,DAT_00447a20,DAT_00447a1c,0x62b,DAT_00447ecc,uVar13);
          }
          iVar11 = FUN_0043d0ce();
          if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
            compress_log_output(0x10400000,DAT_00447ed0,DAT_00447ed0,uVar13);
          }
          iVar11 = FUN_0047075c(uVar13);
          if (iVar11 != 0) {
            iVar9 = FUN_0043d0ce();
            if (iVar9 << 0x1e < 0) {
              FUN_0043d574(1,DAT_00447a24,DAT_00447a20,DAT_00447a1c,0x62e,DAT_00447ebc,uVar13,iVar11
                          );
            }
            iVar9 = FUN_0043d0ce();
            if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
              compress_log_output(0x4800000,DAT_00447ec0,DAT_00447ec0,uVar13,iVar11);
            }
            _evenOtaReplyToAPP(0xc1,2,6);
            return;
          }
          iVar11 = FUN_0043d0ce();
          if (iVar11 << 0x1e < 0) {
            FUN_0043d574(4,DAT_00447a24,DAT_00447a20,DAT_00447a1c,0x632,DAT_00447ec4,uVar13);
          }
          iVar11 = FUN_0043d0ce();
          if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
            compress_log_output(0x10400000,DAT_00447ec8,DAT_00447ec8,uVar13);
          }
          iVar10 = iVar10 + 1;
        }
      }
      if (iVar10 == 0) {
        iVar10 = FUN_0043d0ce();
        if (iVar10 << 0x1e < 0) {
          FUN_0043d574(4,DAT_00447a24,DAT_00447a20,DAT_00447a1c,0x639,DAT_00447ed4);
        }
        iVar10 = FUN_0043d0ce();
        if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_00447ed8,DAT_00447ed8);
        }
      }
      else {
        iVar11 = FUN_0043d0ce();
        if (iVar11 << 0x1e < 0) {
          FUN_0043d574(4,DAT_00447a24,DAT_00447a20,DAT_00447a1c,0x63b,DAT_00447edc,iVar10);
        }
        iVar11 = FUN_0043d0ce();
        if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
          compress_log_output(0x10400000,DAT_00447ee0,DAT_00447ee0,iVar10);
        }
      }
      iVar10 = FUN_004709c0(uVar8,param_1,param_2);
      if (iVar10 == 0) {
        iVar10 = FUN_004709c8(uVar8,auStack_1024,param_2);
        if (iVar10 == 0) {
          iVar10 = FUN_004751c8(auStack_1024,param_1,param_2);
          if (iVar10 == 0) {
            iVar10 = osKernelGetTickCount();
            FUN_0047cbc4(param_1,param_2,piVar3 + 0x17);
            *(uint *)(pcVar2 + 0x3c) = param_2 + *(int *)(pcVar2 + 0x3c);
            piVar3[0x19] = param_2 + piVar3[0x19];
            _evenOtaReplyToAPP(0xc1,2,0);
            if (piVar3[0x16] != 0) {
              uVar7 = FUN_0047cc60((int)((ulonglong)(uint)piVar3[0x19] * 100),
                                   (int)((ulonglong)(uint)piVar3[0x19] * 100 >> 0x20),piVar3[0x16],0
                                  );
              *(undefined1 *)(piVar3 + 0x1b) = uVar7;
            }
            iVar11 = FUN_0043d0ce();
            if (iVar11 << 0x1e < 0) {
              FUN_0043d574(4,DAT_00447a24,DAT_00447a20,DAT_00447a1c,0x66a,DAT_00447efc,
                           (char)piVar3[0x1b],iVar10 - iVar9,
                           (param_2 * 1000 >> 10) / (uint)(iVar10 - iVar9),
                           ((uint)(piVar3[0x19] * 1000) >> 10) / (uint)(iVar10 - iVar9));
            }
            iVar11 = FUN_0043d0ce();
            if ((iVar11 << 0x1f < 0) || (iVar11 = FUN_0043d0ce(), iVar11 << 0x1d < 0)) {
              compress_log_output(0x11000000,DAT_004486e0,DAT_004486e0,(char)piVar3[0x1b],
                                  iVar10 - iVar9,(param_2 * 1000 >> 10) / (uint)(iVar10 - iVar9),
                                  ((uint)(piVar3[0x19] * 1000) >> 10) / (uint)(iVar10 - iVar9));
            }
          }
          else {
            iVar9 = FUN_0043d0ce();
            if (iVar9 << 0x1e < 0) {
              FUN_0043d574(1,DAT_00447a24,DAT_00447a20,DAT_00447a1c,0x651,DAT_00447ef4,uVar8);
            }
            iVar9 = FUN_0043d0ce();
            if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
              compress_log_output(0x4400000,DAT_00447ef8,DAT_00447ef8,uVar8);
            }
            _evenOtaReplyToAPP(0xc1,2,6);
          }
        }
        else {
          iVar9 = FUN_0043d0ce();
          if (iVar9 << 0x1e < 0) {
            FUN_0043d574(1,DAT_00447a24,DAT_00447a20,DAT_00447a1c,0x64a,DAT_00447eec,uVar8,iVar10);
          }
          iVar9 = FUN_0043d0ce();
          if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
            compress_log_output(0x4800000,DAT_00447ef0,DAT_00447ef0,uVar8,iVar10);
          }
          _evenOtaReplyToAPP(0xc1,2,6);
        }
      }
      else {
        iVar9 = FUN_0043d0ce();
        if (iVar9 << 0x1e < 0) {
          FUN_0043d574(1,DAT_00447a24,DAT_00447a20,DAT_00447a1c,0x641,DAT_00447ee4,uVar8,iVar10);
        }
        iVar9 = FUN_0043d0ce();
        if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
          compress_log_output(0x4800000,DAT_00447ee8,DAT_00447ee8,uVar8,iVar10);
        }
        _evenOtaReplyToAPP(0xc1,2,6);
      }
    }
  }
  return;
}

