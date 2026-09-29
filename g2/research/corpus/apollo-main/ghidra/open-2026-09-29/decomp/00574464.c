
undefined8 pt_cmd_44_handler(int param_1,uint param_2,undefined1 *param_3,undefined1 *param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  undefined1 *puVar4;
  
  uVar3 = param_2;
  puVar4 = param_4;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    uVar3 = 0xa7d;
    FUN_0043d574(3,DAT_005747d4,DAT_005747d0,DAT_00574f4c,0xa7d,DAT_00574f48,puVar4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc000000,DAT_00574f50,DAT_00574f50);
  }
  if ((((param_3 == (undefined1 *)0x0) || (param_4 == (undefined1 *)0x0)) || (param_1 == 0)) ||
     ((param_2 & 0xff) < 4)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar3 = 0xa80;
      FUN_0043d574(1,DAT_005747d4,DAT_005747d0,DAT_00574f4c,0xa80,DAT_00574798,DAT_00574f4c);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_0057479c,DAT_0057479c,DAT_00574f4c);
    }
    uVar2 = 0xffffffff;
  }
  else {
    *param_3 = 0x46;
    param_3[1] = 1;
    param_3[2] = 2;
    param_3[3] = 1;
    param_3[4] = *DAT_005747a0 != '\0';
    *param_4 = 5;
    uVar2 = 0;
  }
  return CONCAT44(uVar3,uVar2);
}

