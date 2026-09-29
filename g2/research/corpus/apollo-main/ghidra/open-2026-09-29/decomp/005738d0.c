
undefined8 pt_cmd_3D_handler(int param_1,byte param_2,undefined1 *param_3,byte *param_4)

{
  char cVar1;
  uint *puVar2;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  byte bVar6;
  uint in_fpscr;
  undefined4 uVar7;
  undefined4 extraout_s1;
  undefined4 extraout_s1_00;
  double dVar8;
  double dVar9;
  uint local_28 [2];
  
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    FUN_0043d574(3,DAT_00573f80,DAT_00573f7c,DAT_005741dc,0x960,DAT_00573f74);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0xc000000,DAT_00573f84,DAT_00573f84);
  }
  if ((((param_3 == (undefined1 *)0x0) || (param_4 == (byte *)0x0)) || (param_1 == 0)) ||
     (param_2 < 5)) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00573f80,DAT_00573f7c,DAT_005741dc,0x963,DAT_00573c20,DAT_005741dc);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00573c30,DAT_00573c30,DAT_005741dc);
    }
    uVar4 = 0xffffffff;
  }
  else {
    *param_3 = 0x2e;
    param_3[1] = 1;
    param_3[2] = 3;
    param_3[3] = 6;
    cVar1 = *(char *)(param_1 + 4);
    uVar4 = FUN_0058f8e4();
    uVar7 = FUN_0058f970(uVar4);
    local_28[0] = (uint)(0.0 < (double)CONCAT44(extraout_s1_00,uVar7)) *
                  (int)(longlong)(double)CONCAT44(extraout_s1_00,uVar7);
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(3,DAT_00573f80,DAT_00573f7c,DAT_005741dc,0x971,DAT_00574458,cVar1);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc800000,DAT_0057445c,DAT_0057445c,cVar1,CONCAT44(extraout_s1,uVar4));
    }
    iVar3 = productModeGet();
    if (iVar3 == 1) {
      param_3[4] = 0;
      puVar2 = DAT_0057454c;
      if (cVar1 == '\x04') {
        *DAT_00574460 = local_28[0];
      }
      else if (cVar1 == '\x01') {
        *DAT_0057454c = local_28[0];
        iVar3 = DAT_00574558;
        if (*DAT_00574460 == 0) {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(1,DAT_00573f80,DAT_00573f7c,DAT_005741dc,0x980,DAT_00574550);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x4000000,DAT_00574554,DAT_00574554);
          }
        }
        else {
          dVar8 = (double)VectorUnsignedToFloat(*DAT_00574460,(byte)(in_fpscr >> 0x16) & 3);
          dVar9 = (double)VectorUnsignedToFloat(*puVar2,(byte)(in_fpscr >> 0x16) & 3);
          *(int *)(DAT_00574558 + 0x28) =
               (int)((((float)(DAT_00573c3c / dVar8) + (float)(DAT_00573c44 / dVar9)) / 2.0) *
                    DAT_00573c4c);
          SVC_NvdbWriteSysData(2,iVar3 + 0x28);
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(4,DAT_00573f80,DAT_00573f7c,DAT_005741dc,0x988,DAT_0057455c);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x10000000,DAT_00574560,DAT_00574560);
          }
        }
      }
      else {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(1,DAT_00573f80,DAT_00573f7c,DAT_005741dc,0x98d,DAT_00574564);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_00574568,DAT_00574568);
        }
      }
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(1,DAT_00573f80,DAT_00573f7c,DAT_005741dc,0x992,DAT_00573f68);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_005741cc,DAT_005741cc);
      }
      param_3[4] = 5;
    }
    param_3[5] = cVar1;
    bVar6 = 6;
    for (uVar5 = 0; uVar5 < 4; uVar5 = uVar5 + 1) {
      param_3[bVar6] = *(undefined1 *)((int)local_28 + uVar5);
      bVar6 = bVar6 + 1;
    }
    if (local_28[0] < DAT_00574788) {
      if (local_28[0] == 0) {
        param_3[4] = 2;
      }
    }
    else {
      param_3[4] = 1;
    }
    *param_4 = bVar6;
    uVar4 = 0;
  }
  return CONCAT44(param_4,uVar4);
}

