
undefined8 pt_cmd_6B_handler(int param_1,uint param_2,undefined1 *param_3,undefined1 *param_4)

{
  char cVar1;
  char cVar2;
  char cVar3;
  int iVar4;
  undefined4 uVar5;
  char *pcVar6;
  uint uVar7;
  undefined1 *puVar8;
  
  uVar7 = param_2;
  puVar8 = param_4;
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    uVar7 = 0xe36;
    FUN_0043d574(3,DAT_00577bbc,DAT_00577bb8,DAT_00577bb4,0xe36,DAT_00577bb0,puVar8);
  }
  iVar4 = FUN_0043d0ce();
  if (-1 < iVar4 << 0x1f) {
    iVar4 = FUN_0043d0ce();
    if (-1 < iVar4 << 0x1d) goto LAB_005773b2;
  }
  compress_log_output(0xc000000,DAT_00577bc0,DAT_00577bc0);
LAB_005773b2:
  if ((((param_3 == (undefined1 *)0x0) || (param_4 == (undefined1 *)0x0)) || (param_1 == 0)) ||
     ((param_2 & 0xff) < 4)) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      uVar7 = 0xe39;
      FUN_0043d574(1,DAT_00577bbc,DAT_00577bb8,DAT_00577bb4,0xe39,DAT_00577bc4,DAT_00577bb4);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00577470,DAT_00577470,DAT_00577bb4);
    }
    uVar5 = 0xffffffff;
  }
  else {
    pcVar6 = (char *)FUN_0046d584();
    cVar1 = *pcVar6;
    cVar2 = pcVar6[2];
    cVar3 = pcVar6[4];
    *param_3 = 0x6a;
    param_3[1] = 1;
    param_3[2] = 3;
    param_3[3] = 3;
    param_3[4] = cVar1 + -0x30;
    param_3[5] = cVar2 + -0x30;
    param_3[6] = cVar3 + -0x30;
    *param_4 = 7;
    uVar5 = 0;
  }
  return CONCAT44(uVar7,uVar5);
}

