
undefined4 pt_cmd_63_handler(int param_1,byte param_2,undefined1 *param_3,char *param_4)

{
  undefined1 uVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;
  byte bVar5;
  undefined4 local_18;
  
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(3,DAT_00577358,DAT_00577354,DAT_00577570,0xd82,DAT_00577478);
  }
  iVar2 = FUN_0043d0ce();
  if (-1 < iVar2 << 0x1f) {
    iVar2 = FUN_0043d0ce();
    if (-1 < iVar2 << 0x1d) goto LAB_00576aa4;
  }
  compress_log_output(0xc000000,DAT_00577574,DAT_00577574);
LAB_00576aa4:
  if ((((param_3 == (undefined1 *)0x0) || (param_4 == (char *)0x0)) || (param_1 == 0)) ||
     (param_2 < 4)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00577358,DAT_00577354,DAT_00577570,0xd85,DAT_00577360,DAT_00577570);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00577470,DAT_00577470,DAT_00577570);
    }
    uVar3 = 0xffffffff;
  }
  else {
    *param_3 = 0x62;
    param_3[1] = 1;
    param_3[2] = 3;
    param_3[3] = 5;
    bVar5 = 4;
    local_18 = nvdbBuzzerFrequencyGet();
    for (uVar4 = 0; uVar4 < 4; uVar4 = uVar4 + 1) {
      param_3[bVar5] = *(undefined1 *)((int)&local_18 + uVar4);
      bVar5 = bVar5 + 1;
    }
    uVar1 = nvdbBuzzerDutyGet();
    param_3[bVar5] = uVar1;
    *param_4 = bVar5 + 1;
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,DAT_00577358,DAT_00577354,DAT_00577570,0xd96,DAT_00577578,local_18,uVar1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc800000,DAT_00577780,DAT_00577780,local_18,uVar1);
    }
    uVar3 = 0;
  }
  return uVar3;
}

