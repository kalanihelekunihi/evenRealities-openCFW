
undefined4 pt_cmd_39_handler(int param_1,byte param_2,undefined1 *param_3,char *param_4)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;
  undefined1 *puVar5;
  char *pcVar6;
  
  puVar5 = param_3;
  pcVar6 = param_4;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(3,DAT_005735f4,DAT_005735f0,DAT_005741d0,0x91e,DAT_00573f6c,puVar5,pcVar6);
  }
  iVar2 = FUN_0043d0ce();
  if (-1 < iVar2 << 0x1f) {
    iVar2 = FUN_0043d0ce();
    if (-1 < iVar2 << 0x1d) goto LAB_00573518;
  }
  compress_log_output(0xc000000,DAT_00573f70,DAT_00573f70);
LAB_00573518:
  if ((((param_3 == (undefined1 *)0x0) || (param_4 == (char *)0x0)) || (param_1 == 0)) ||
     (param_2 < 4)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005735f4,DAT_005735f0,DAT_005741d0,0x921,DAT_00573c20,DAT_005741d0);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00573c30,DAT_00573c30,DAT_005741d0);
    }
    uVar3 = 0xffffffff;
  }
  else {
    *param_3 = 0x22;
    param_3[1] = 1;
    param_3[2] = 3;
    uVar3 = SVC_NvdbGetSysData(0);
    uVar4 = FUN_0044a43c(uVar3);
    if (uVar4 < 0xf) {
      cVar1 = FUN_0044a43c(uVar3);
    }
    else {
      cVar1 = '\x0e';
    }
    param_3[3] = cVar1;
    FUN_00439be4(param_3 + 4,uVar3,cVar1);
    *param_4 = cVar1 + '\x04';
    uVar3 = 0;
  }
  return uVar3;
}

