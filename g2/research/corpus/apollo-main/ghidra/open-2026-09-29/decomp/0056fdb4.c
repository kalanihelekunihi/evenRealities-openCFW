
undefined4 pt_cmd_11_handler(int param_1,uint param_2,undefined1 *param_3,undefined1 *param_4)

{
  byte bVar1;
  int *piVar2;
  undefined1 uVar3;
  int iVar4;
  undefined4 uVar5;
  
  if ((((param_3 == (undefined1 *)0x0) || (param_4 == (undefined1 *)0x0)) || (param_1 == 0)) ||
     ((param_2 & 0xff) < 4)) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      param_1 = 0x3f3;
      param_2 = DAT_0057076c;
      param_3 = DAT_0057077c;
      FUN_0043d574(1,DAT_00570760,DAT_0057075c,DAT_0057077c,0x3f3,DAT_0057076c,DAT_0057077c,param_4)
      ;
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00570770,DAT_00570770,DAT_0057077c,param_1,param_2,param_3);
    }
    uVar5 = 0xffffffff;
  }
  else {
    if (5 < (param_2 & 0xff)) {
      bVar1 = *(byte *)(param_1 + 4);
      FUN_004ac718(*(byte *)(param_1 + 4) & 0x7f);
      FUN_004ac72e(bVar1 >> 7);
      if (6 < (param_2 & 0xff)) {
        if (*(char *)(param_1 + 5) == '\x02') {
          FUN_004ac744(1);
        }
        else {
          FUN_004ac744(0);
        }
      }
    }
    *param_3 = 0x13;
    param_3[1] = 1;
    param_3[2] = 2;
    param_3[3] = 6;
    piVar2 = DAT_005709b0;
    param_3[4] = (char)DAT_005709b0[5] != '\0';
    param_3[5] = (char)((uint)piVar2[2] >> 8);
    param_3[6] = (char)piVar2[2];
    param_3[7] = (char)piVar2[1];
    iVar4 = piVar2[3];
    if (*piVar2 == 0) {
      if (iVar4 < 0) {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(4,DAT_00570760,DAT_0057075c,DAT_0057077c,0x41f,DAT_005709bc,piVar2[3]);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x10400000,DAT_00570b54,DAT_00570b54,piVar2[3]);
        }
        iVar4 = -1;
      }
    }
    else if (0 < iVar4) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(4,DAT_00570760,DAT_0057075c,DAT_0057077c,0x418,DAT_005709b4,piVar2[3]);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_005709b8,DAT_005709b8,piVar2[3]);
      }
      iVar4 = -1;
    }
    param_3[8] = iVar4 < 1;
    uVar3 = FUN_00509694(iVar4);
    param_3[9] = uVar3;
    *param_4 = 10;
    uVar5 = 0;
  }
  return uVar5;
}

