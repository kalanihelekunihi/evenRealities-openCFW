
undefined4 pt_cmd_46_handler(int param_1,byte param_2,undefined1 *param_3,undefined1 *param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  int iVar4;
  
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(3,DAT_005747d4,DAT_005747d0,DAT_00574f58,0xa93,DAT_00574f54);
  }
  iVar1 = FUN_0043d0ce();
  if (-1 < iVar1 << 0x1f) {
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1d) goto LAB_005745ce;
  }
  compress_log_output(0xc000000,DAT_00574f5c,DAT_00574f5c);
LAB_005745ce:
  if ((((param_3 == (undefined1 *)0x0) || (param_4 == (undefined1 *)0x0)) || (param_1 == 0)) ||
     (param_2 < 4)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005747d4,DAT_005747d0,DAT_00574f58,0xa96,DAT_00574798,DAT_00574f58);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_0057479c,DAT_0057479c,DAT_00574f58);
    }
    uVar2 = 0xffffffff;
  }
  else {
    *param_3 = 0x3d;
    param_3[1] = 1;
    param_3[2] = 3;
    param_3[3] = 0xc;
    iVar1 = DAT_00575224;
    param_3[4] = *(undefined1 *)(DAT_00575224 + 0xaa);
    uVar2 = FUN_0056f178(iVar1 + 0x58,iVar1 + 0x30);
    param_3[5] = (char)uVar2;
    param_3[6] = (char)((uint)uVar2 >> 8);
    param_3[7] = (char)((uint)uVar2 >> 0x10);
    param_3[8] = (char)((uint)uVar2 >> 0x18);
    uVar3 = FUN_0056f178(iVar1 + 0x80,iVar1 + 0x30);
    param_3[9] = (char)uVar3;
    param_3[10] = (char)((uint)uVar3 >> 8);
    param_3[0xb] = (char)((uint)uVar3 >> 0x10);
    param_3[0xc] = (char)((uint)uVar3 >> 0x18);
    param_3[0xd] = *(undefined1 *)(iVar1 + 0xa9);
    param_3[0xe] = *(undefined1 *)(iVar1 + 0xa8);
    param_3[0xf] = *(undefined1 *)(iVar1 + 0xab);
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(3,DAT_005747d4,DAT_005747d0,DAT_00574f58,0xabd,DAT_00575228,
                   *(undefined1 *)(iVar1 + 0xaa),uVar2,uVar3,*(undefined1 *)(iVar1 + 0xa9),
                   *(undefined1 *)(iVar1 + 0xa8),*(undefined1 *)(iVar1 + 0xab));
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0xd800000,DAT_0057540c,DAT_0057540c,*(undefined1 *)(iVar1 + 0xaa),uVar2,
                          uVar3,*(undefined1 *)(iVar1 + 0xa9),*(undefined1 *)(iVar1 + 0xa8),
                          *(undefined1 *)(iVar1 + 0xab));
    }
    *param_4 = 0x10;
    uVar2 = 0;
  }
  return uVar2;
}

