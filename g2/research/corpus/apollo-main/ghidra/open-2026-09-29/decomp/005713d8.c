
undefined4 pt_cmd_1A_handler(int param_1,byte param_2,undefined1 *param_3,undefined1 *param_4)

{
  undefined1 uVar1;
  int *piVar2;
  uint *puVar3;
  uint *puVar4;
  int iVar5;
  undefined4 uVar6;
  uint uVar7;
  int iVar8;
  uint uVar9;
  int iVar10;
  undefined1 auStack_118 [32];
  undefined1 auStack_f8 [212];
  
  iVar5 = FUN_0043d0ce();
  if (iVar5 << 0x1e < 0) {
    FUN_0043d574(3,DAT_00571fd8,DAT_00571fd4,DAT_00571e3c,0x5e6,DAT_00571e38,
                 *(undefined1 *)(param_1 + 5));
  }
  iVar5 = FUN_0043d0ce();
  if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
    compress_log_output(0xc400000,DAT_00571e40,DAT_00571e40,*(undefined1 *)(param_1 + 5));
  }
  if ((((param_3 == (undefined1 *)0x0) || (param_4 == (undefined1 *)0x0)) || (param_1 == 0)) ||
     (param_2 < 6)) {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00571fd8,DAT_00571fd4,DAT_00571e3c,0x5e9,DAT_00571cb8,DAT_00571e3c);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00571cbc,DAT_00571cbc,DAT_00571e3c);
    }
    uVar6 = 0xffffffff;
  }
  else {
    FUN_0043c0e4(auStack_f8,0xd2,0);
    iVar10 = 0;
    uVar1 = *(undefined1 *)(param_1 + 5);
    iVar5 = productModeGet();
    if (iVar5 == 1) {
      *param_3 = 0x1b;
      param_3[1] = 1;
      param_3[2] = 3;
      param_3[3] = 0xd8;
      param_3[4] = uVar1;
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(3,DAT_00571fd8,DAT_00571fd4,DAT_00571e3c,0x605,DAT_00571fe4,uVar1);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0xc400000,DAT_00571fe8,DAT_00571fe8,uVar1);
      }
      FUN_0043c0e4(auStack_118,0x20,0);
      service_audio_current_recording_path(uVar1,auStack_118,0x20);
      if ((*DAT_00571fec == '\0') || (iVar5 = FUN_0046cacc(auStack_118,DAT_00571ff0), iVar5 != 0)) {
        piVar2 = DAT_00571ff4;
        if (*DAT_00571ff4 != 0) {
          file_heap_free(*DAT_00571ff4);
          *piVar2 = 0;
        }
        *DAT_00571fec = '\0';
        *DAT_00571ff8 = 0;
        *DAT_00571ffc = 0;
        iVar5 = file_open(auStack_118,&DAT_00571908);
        if (iVar5 == 0) {
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            FUN_0043d574(1,DAT_00571fd8,DAT_00571fd4,DAT_00571e3c,0x61f,DAT_00572000,auStack_118);
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            compress_log_output(0x4400000,DAT_00572004,DAT_00572004,auStack_118);
          }
          *param_3 = 0x1b;
          param_3[1] = 1;
          param_3[2] = 3;
          param_3[3] = 2;
          param_3[4] = 3;
          param_3[5] = uVar1;
          *param_4 = 6;
          return 0;
        }
        uVar7 = FUN_0056f23a(iVar5);
        iVar8 = FUN_0043d0ce();
        if (iVar8 << 0x1e < 0) {
          FUN_0043d574(3,DAT_00571fd8,DAT_00571fd4,DAT_00571e3c,0x62d,DAT_00572008,auStack_118,uVar7
                      );
        }
        iVar8 = FUN_0043d0ce();
        if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
          compress_log_output(0xc800000,DAT_00572210,DAT_00572210,auStack_118,uVar7);
        }
        if ((int)uVar7 < 1) {
          iVar10 = FUN_0043d0ce();
          if (iVar10 << 0x1e < 0) {
            FUN_0043d574(1,DAT_00571fd8,DAT_00571fd4,DAT_00571e3c,0x630,DAT_00572214,uVar7,
                         auStack_118);
          }
          iVar10 = FUN_0043d0ce();
          if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
            compress_log_output(0x4800000,DAT_00572218,DAT_00572218,uVar7,auStack_118);
          }
          file_close(iVar5);
          *param_3 = 0x1b;
          param_3[1] = 1;
          param_3[2] = 3;
          param_3[3] = 2;
          param_3[4] = 3;
          param_3[5] = uVar1;
          *param_4 = 6;
          return 0;
        }
        if (DAT_0057221c <= (int)uVar7) {
          iVar10 = FUN_0043d0ce();
          if (iVar10 << 0x1e < 0) {
            FUN_0043d574(1,DAT_00571fd8,DAT_00571fd4,DAT_00571e3c,0x63f,DAT_00572220,uVar7);
          }
          iVar10 = FUN_0043d0ce();
          if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
            compress_log_output(0x4400000,DAT_00572224,DAT_00572224,uVar7);
          }
          file_close(iVar5);
          *param_3 = 0x1b;
          param_3[1] = 1;
          param_3[2] = 3;
          param_3[3] = 2;
          param_3[4] = 3;
          param_3[5] = uVar1;
          *param_4 = 6;
          return 0;
        }
        uVar9 = uVar7;
        iVar8 = FUN_0043d0ce();
        if (iVar8 << 0x1e < 0) {
          FUN_0043d574(3,DAT_00571fd8,DAT_00571fd4,DAT_00571e3c,0x64e,DAT_00572228,uVar9);
        }
        iVar8 = FUN_0043d0ce();
        if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
          compress_log_output(0xc400000,DAT_00572370,DAT_00572370,uVar9);
        }
        iVar8 = file_heap_allocate(uVar9);
        *piVar2 = iVar8;
        if (*piVar2 == 0) {
          iVar10 = FUN_0043d0ce();
          if (iVar10 << 0x1e < 0) {
            FUN_0043d574(1,DAT_00571fd8,DAT_00571fd4,DAT_00571e3c,0x652,DAT_00572374,uVar7);
          }
          iVar10 = FUN_0043d0ce();
          if ((iVar10 << 0x1f < 0) || (iVar10 = FUN_0043d0ce(), iVar10 << 0x1d < 0)) {
            compress_log_output(0x4400000,DAT_00572378,DAT_00572378,uVar7);
          }
          file_close(iVar5);
          *param_3 = 0x1b;
          param_3[1] = 1;
          param_3[2] = 3;
          param_3[3] = 2;
          param_3[4] = 3;
          param_3[5] = uVar1;
          *param_4 = 6;
          return 0;
        }
        uVar9 = file_read(*piVar2,1,uVar7,iVar5);
        iVar8 = FUN_0043d0ce();
        if (iVar8 << 0x1e < 0) {
          FUN_0043d574(3,DAT_00571fd8,DAT_00571fd4,DAT_00571e3c,0x661,DAT_0057237c,uVar9);
        }
        iVar8 = FUN_0043d0ce();
        if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
          compress_log_output(0xc400000,DAT_00572380,DAT_00572380,uVar9);
        }
        file_close(iVar5);
        if (uVar9 != uVar7) {
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            FUN_0043d574(1,DAT_00571fd8,DAT_00571fd4,DAT_00571e3c,0x665,DAT_00572384,uVar7,uVar9);
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            compress_log_output(0x4800000,DAT_00572388,DAT_00572388,uVar7,uVar9);
          }
          file_heap_free(*piVar2);
          *piVar2 = 0;
          *param_3 = 0x1b;
          param_3[1] = 1;
          param_3[2] = 3;
          param_3[3] = 2;
          param_3[4] = 3;
          param_3[5] = uVar1;
          *param_4 = 6;
          return 0;
        }
        *DAT_00571ffc = uVar7;
        *DAT_00571ff8 = 0;
        *DAT_00571fec = '\x01';
        FUN_0048d540(DAT_00571ff0,auStack_118);
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(3,DAT_00571fd8,DAT_00571fd4,DAT_00571e3c,0x679,DAT_005724d8,auStack_118,uVar7
                      );
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0xc800000,DAT_005724dc,DAT_005724dc,auStack_118,uVar7);
        }
      }
      if (*(char *)(param_1 + 4) == '\x01') {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(4,DAT_00571fd8,DAT_00571fd4,DAT_00571e3c,0x680,DAT_005724e0);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_005724e4,DAT_005724e4);
        }
        if (*DAT_00571ff8 < 0xd2) {
          *DAT_00571ff8 = 0;
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            FUN_0043d574(2,DAT_00571fd8,DAT_00571fd4,DAT_00571e3c,0x686,DAT_005724e8);
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            compress_log_output(0x8000000,DAT_005724ec,DAT_005724ec);
          }
        }
        else {
          *DAT_00571ff8 = *DAT_00571ff8 - 0xd2;
        }
      }
      puVar4 = DAT_00571ffc;
      puVar3 = DAT_00571ff8;
      iVar5 = 0xd2;
      if (*DAT_00571ffc < *DAT_00571ff8 + 0xd2) {
        iVar5 = *DAT_00571ffc - *DAT_00571ff8;
      }
      if (iVar5 == 0) {
        FUN_0043c0e4(auStack_f8,0xd2,0);
      }
      else {
        FUN_00439be4(auStack_f8,*DAT_00571ff8 + *DAT_00571ff4,iVar5);
        *puVar3 = iVar5 + *puVar3;
      }
      *DAT_005724f0 = iVar5;
      FUN_00439be4(param_3 + 10,auStack_f8,0xd2);
      if (*puVar3 < *puVar4) {
        param_3[9] = 0;
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(3,DAT_00571fd8,DAT_00571fd4,DAT_00571e3c,0x6af,DAT_005726dc,*puVar4 - *puVar3
                      );
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0xc400000,DAT_0057292c,DAT_0057292c,*puVar4 - *puVar3);
        }
      }
      else {
        param_3[9] = 1;
        piVar2 = DAT_00571ff4;
        if (*DAT_00571ff4 != 0) {
          file_heap_free(*DAT_00571ff4);
          *piVar2 = 0;
        }
        *DAT_00571fec = '\0';
        *puVar4 = 0;
        *puVar3 = 0;
        FUN_0043c0e4(DAT_00571ff0,0x20,0);
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(3,DAT_00571fd8,DAT_00571fd4,DAT_00571e3c,0x6aa,DAT_005726d4,*puVar4);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0xc400000,DAT_005726d8,DAT_005726d8,*puVar4);
        }
      }
      for (iVar5 = 0; iVar5 < 0xdc; iVar5 = iVar5 + 1) {
        if (3 < iVar5 - 5U) {
          iVar10 = iVar10 + (uint)(byte)param_3[iVar5];
        }
      }
      param_3[5] = (char)((uint)iVar10 >> 0x18);
      param_3[6] = (char)((uint)iVar10 >> 0x10);
      param_3[7] = (char)((uint)iVar10 >> 8);
      param_3[8] = (char)iVar10;
      *param_4 = 0xdc;
      uVar6 = 0;
    }
    else {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(1,DAT_00571fd8,DAT_00571fd4,DAT_00571e3c,0x5f4,DAT_00571fdc);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_00571fe0,DAT_00571fe0);
      }
      *param_3 = 0x1b;
      param_3[1] = 1;
      param_3[2] = 3;
      param_3[3] = 2;
      param_3[4] = 5;
      param_3[5] = uVar1;
      *param_4 = 6;
      uVar6 = 0;
    }
  }
  return uVar6;
}

