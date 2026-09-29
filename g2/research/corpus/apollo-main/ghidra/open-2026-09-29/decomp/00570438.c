
undefined8 pt_cmd_45_handler(int param_1,uint param_2,undefined1 *param_3,undefined1 *param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  undefined1 *puVar4;
  
  uVar3 = param_2;
  puVar4 = param_4;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    uVar3 = 0x485;
    FUN_0043d574(3,DAT_00570760,DAT_0057075c,DAT_00570d38,0x485,DAT_00570d34,puVar4);
  }
  iVar1 = FUN_0043d0ce();
  if (-1 < iVar1 << 0x1f) {
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1d) goto LAB_00570482;
  }
  compress_log_output(0xc000000,DAT_00570d3c,DAT_00570d3c);
LAB_00570482:
  if ((((param_3 == (undefined1 *)0x0) || (param_4 == (undefined1 *)0x0)) || (param_1 == 0)) ||
     ((param_2 & 0xff) < 4)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar3 = 0x488;
      FUN_0043d574(1,DAT_00570760,DAT_0057075c,DAT_00570d38,0x488,DAT_0057076c,DAT_00570d38);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00570770,DAT_00570770,DAT_00570d38);
    }
    uVar2 = 0xffffffff;
  }
  else {
    *param_3 = 0x39;
    param_3[1] = 1;
    param_3[2] = 3;
    param_3[3] = 4;
    param_3[4] = 0;
    iVar1 = DAT_00570d2c;
    param_3[5] = *(undefined1 *)(DAT_00570d2c + 0x2c);
    param_3[6] = 0;
    param_3[7] = *(undefined1 *)(iVar1 + 0x2d);
    *param_4 = 8;
    uVar2 = 0;
  }
  return CONCAT44(uVar3,uVar2);
}

