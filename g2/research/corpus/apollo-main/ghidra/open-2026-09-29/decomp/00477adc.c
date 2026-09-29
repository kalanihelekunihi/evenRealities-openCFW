
void _connUpdateFinishInd(undefined2 *param_1)

{
  undefined2 uVar1;
  undefined1 uVar2;
  bool bVar3;
  char *pcVar4;
  char *pcVar5;
  int *piVar6;
  undefined1 uVar7;
  char cVar8;
  int iVar9;
  undefined4 uVar10;
  undefined4 uVar11;
  
  uVar1 = *param_1;
  dmGetConnParamPtr();
  iVar9 = FUN_0043d0ce();
  uVar2 = (undefined1)uVar1;
  if (iVar9 << 0x1e < 0) {
    uVar7 = DmConnRole(uVar2);
    FUN_0043d574(4,DAT_004782bc,DAT_004782b8,DAT_004782b4,0x161,DAT_004782b0,
                 *(undefined1 *)(param_1 + 2),uVar7);
  }
  iVar9 = FUN_0043d0ce();
  if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
    uVar7 = DmConnRole(uVar2);
    compress_log_output(0x10800000,DAT_004782c0,DAT_004782c0,*(undefined1 *)(param_1 + 2),uVar7);
  }
  iVar9 = FUN_0043d0ce();
  if (iVar9 << 0x1e < 0) {
    FUN_0043d574(4,DAT_004782bc,DAT_004782b8,DAT_004782b4,0x162,DAT_004782c4,param_1[4],param_1[4],
                 param_1[5]);
  }
  iVar9 = FUN_0043d0ce();
  if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
    compress_log_output(0x10c00000,DAT_004782c8,DAT_004782c8,param_1[4],param_1[4],param_1[5]);
  }
  iVar9 = FUN_0043d0ce();
  if (iVar9 << 0x1e < 0) {
    FUN_0043d574(4,DAT_004782bc,DAT_004782b8,DAT_004782b4,0x163,DAT_004782cc,
                 ((uint)(ushort)param_1[4] * 0x4e2) / 1000);
  }
  iVar9 = FUN_0043d0ce();
  if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_004782d0,DAT_004782d0,
                        ((uint)(ushort)param_1[4] * 0x4e2) / 1000);
  }
  iVar9 = FUN_0043d0ce();
  if (iVar9 << 0x1e < 0) {
    FUN_0043d574(4,DAT_004782bc,DAT_004782b8,DAT_004782b4,0x164,DAT_004782d4,param_1[5]);
  }
  iVar9 = FUN_0043d0ce();
  if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_004782d8,DAT_004782d8,param_1[5]);
  }
  iVar9 = FUN_0043d0ce();
  if (iVar9 << 0x1e < 0) {
    FUN_0043d574(4,DAT_004782bc,DAT_004782b8,DAT_004782b4,0x165,DAT_004786b4,
                 ((uint)(ushort)param_1[6] * 10000) / 1000);
  }
  iVar9 = FUN_0043d0ce();
  if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_004786b8,DAT_004786b8,
                        ((uint)(ushort)param_1[6] * 10000) / 1000);
  }
  iVar9 = DmConnRole(uVar2);
  if (iVar9 == 1) {
    iVar9 = FUN_0043d0ce();
    if (iVar9 << 0x1e < 0) {
      uVar10 = DAT_004782a0;
      if (*DAT_004786bc == -0x5d) {
        uVar10 = DAT_0047829c;
      }
      FUN_0043d574(4,DAT_004782bc,DAT_004782b8,DAT_004782b4,0x169,DAT_004786c0,uVar10);
    }
    iVar9 = FUN_0043d0ce();
    if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
      uVar10 = DAT_004782a0;
      if (*DAT_004786bc == -0x5d) {
        uVar10 = DAT_0047829c;
      }
      compress_log_output(0x10400000,DAT_004786c4,DAT_004786c4,uVar10);
    }
    iVar9 = FUN_0043d0ce();
    if (iVar9 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004782bc,DAT_004782b8,DAT_004782b4,0x16a,DAT_004786cc,param_1[4],param_1[4]
                   ,param_1[5],*(undefined2 *)(DAT_004786c8 + 4),*(undefined2 *)(DAT_004786c8 + 6),
                   *(undefined2 *)(DAT_004786c8 + 8));
    }
    iVar9 = FUN_0043d0ce();
    if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
      compress_log_output(0x11800000,DAT_004786d0,DAT_004786d0,param_1[4],param_1[4],param_1[5],
                          *(undefined2 *)(DAT_004786c8 + 4),*(undefined2 *)(DAT_004786c8 + 6),
                          *(undefined2 *)(DAT_004786c8 + 8));
    }
    bVar3 = false;
    if (*(char *)(param_1 + 2) != '\0') {
      bVar3 = true;
      iVar9 = FUN_0043d0ce();
      if (iVar9 << 0x1e < 0) {
        FUN_0043d574(2,DAT_004782bc,DAT_004782b8,DAT_004782b4,0x172,DAT_004786d4,
                     *(undefined1 *)(param_1 + 2));
      }
      iVar9 = FUN_0043d0ce();
      if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_004786d8,DAT_004786d8,*(undefined1 *)(param_1 + 2));
      }
      if ((*(char *)(param_1 + 2) == '\f') || (*(char *)(param_1 + 2) == ';')) {
        iVar9 = FUN_0043d0ce();
        if (iVar9 << 0x1e < 0) {
          FUN_0043d574(2,DAT_004782bc,DAT_004782b8,DAT_004782b4,0x177,DAT_004786dc,
                       *(undefined1 *)(param_1 + 2));
        }
        iVar9 = FUN_0043d0ce();
        if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
          compress_log_output(0x8400000,DAT_004786e0,DAT_004786e0,*(undefined1 *)(param_1 + 2));
        }
        uVar10 = osKernelGetTickCount();
        *DAT_004786e4 = uVar10;
        *DAT_004786e8 = 1;
        *DAT_004786ec = 0;
        uVar10 = DAT_004782ac;
        fw_event_loop_remove_delayed(DAT_004782ac);
        fw_event_loop_push_delayed(uVar10,*DAT_004786bc,30000);
        return;
      }
    }
    piVar6 = DAT_00478700;
    pcVar5 = DAT_004786bc;
    pcVar4 = DAT_00478298;
    if (*DAT_00478298 == '\0') {
      if ((ushort)param_1[4] < 0x19) {
        cVar8 = -0x5d;
      }
      else {
        cVar8 = -0x5c;
      }
    }
    else if ((ushort)param_1[4] < 0x48) {
      cVar8 = -0x5d;
    }
    else {
      cVar8 = -0x5c;
    }
    if (cVar8 == *DAT_004786bc) {
      *(undefined2 *)(*DAT_00478700 + 0x18) = param_1[4];
      *(undefined2 *)(*piVar6 + 0x1a) = param_1[5];
      *(undefined2 *)(*piVar6 + 0x1c) = param_1[6];
      *DAT_00478704 = *pcVar5;
      *(bool *)(*piVar6 + 0x1e) = *pcVar5 == -0x5d;
      iVar9 = FUN_0043d0ce();
      if (iVar9 << 0x1e < 0) {
        uVar10 = DAT_004782a0;
        if (*pcVar5 == -0x5d) {
          uVar10 = DAT_0047829c;
        }
        FUN_0043d574(3,DAT_004782bc,DAT_004782b8,DAT_004782b4,0x1a5,DAT_00478708,uVar10);
      }
      iVar9 = FUN_0043d0ce();
      if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
        uVar10 = DAT_004782a0;
        if (*pcVar5 == -0x5d) {
          uVar10 = DAT_0047829c;
        }
        compress_log_output(0xc400000,DAT_0047870c,DAT_0047870c,uVar10);
      }
      *DAT_004786e8 = 0;
      *DAT_004786ec = 0;
    }
    else {
      iVar9 = FUN_0043d0ce();
      if (iVar9 << 0x1e < 0) {
        uVar10 = DAT_004782a0;
        if (*pcVar5 == -0x5d) {
          uVar10 = DAT_0047829c;
        }
        FUN_0043d574(1,DAT_004782bc,DAT_004782b8,DAT_004782b4,0x18d,DAT_004786f0,uVar10);
      }
      iVar9 = FUN_0043d0ce();
      if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
        uVar10 = DAT_004782a0;
        if (*pcVar5 == -0x5d) {
          uVar10 = DAT_0047829c;
        }
        compress_log_output(0x4400000,DAT_004786f4,DAT_004786f4,uVar10);
      }
      if (bVar3) {
        iVar9 = FUN_0043d0ce();
        if (iVar9 << 0x1e < 0) {
          FUN_0043d574(2,DAT_004782bc,DAT_004782b8,DAT_004782b4,0x191,DAT_004786f8);
        }
        iVar9 = FUN_0043d0ce();
        if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
          compress_log_output(0x8000000,DAT_004786fc,DAT_004786fc);
        }
        uVar10 = osKernelGetTickCount();
        *DAT_004786e4 = uVar10;
        *DAT_004786e8 = 1;
        *DAT_004786ec = 0;
        uVar10 = DAT_004782ac;
        fw_event_loop_remove_delayed(DAT_004782ac);
        fw_event_loop_push_delayed(uVar10,*pcVar5,10000);
      }
      else {
        *DAT_004786e8 = 0;
        *DAT_004786ec = 0;
        uVar10 = DAT_004782ac;
        fw_event_loop_remove_delayed(DAT_004782ac);
        if (*pcVar5 == -0x5d) {
          uVar11 = 2000;
        }
        else {
          uVar11 = 4000;
        }
        fw_event_loop_push_delayed(uVar10,*pcVar5,uVar11);
      }
    }
    if (*pcVar4 != '\0') {
      iVar9 = FUN_0043d0ce();
      if (iVar9 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004782bc,DAT_004782b8,DAT_004782b4,0x1ad,DAT_00478710,*pcVar5);
      }
      iVar9 = FUN_0043d0ce();
      if ((iVar9 << 0x1f < 0) || (iVar9 = FUN_0043d0ce(), iVar9 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_00478714,DAT_00478714,*pcVar5);
      }
      uVar10 = DAT_004782ac;
      if (*pcVar5 == -0x5c) {
        *pcVar4 = '\0';
      }
      else {
        fw_event_loop_remove_delayed(DAT_004782ac);
        fw_event_loop_push_delayed(uVar10,0xa4,60000);
      }
    }
  }
  return;
}

