
undefined8 pt_cmd_57_handler(int param_1,uint param_2,undefined1 *param_3,undefined1 *param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  undefined1 *puVar4;
  
  uVar3 = param_2;
  puVar4 = param_4;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    uVar3 = 0xbce;
    FUN_0043d574(3,DAT_00575414,DAT_00575410,DAT_00575e84,0xbce,DAT_00575e80,puVar4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc000000,DAT_00575e88,DAT_00575e88);
  }
  if ((((param_1 == 0) || (param_3 == (undefined1 *)0x0)) || (param_4 == (undefined1 *)0x0)) ||
     ((param_2 & 0xff) < 4)) {
    uVar2 = 0xffffffff;
  }
  else {
    *param_3 = 0x57;
    param_3[1] = 1;
    param_3[2] = 3;
    param_3[3] = 1;
    SVC_CodecMicDelay1Bit();
    param_3[4] = 0;
    *param_4 = 5;
    uVar2 = 0;
  }
  return CONCAT44(uVar3,uVar2);
}

