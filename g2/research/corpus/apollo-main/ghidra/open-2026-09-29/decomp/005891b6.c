
undefined8 FUN_005891b6(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  undefined4 local_10;
  undefined4 local_c;
  
  iVar1 = FUN_0045a568();
  local_10 = param_3;
  local_c = param_4;
  if (iVar1 == 1) {
    *DAT_00589384 = 0;
    *DAT_0058936c = 0;
    *DAT_00589370 = 0;
    *DAT_00589374 = 0;
    *DAT_00589394 = 0;
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_c = DAT_005893d4;
      local_10 = 0x120;
      FUN_0043d574(4,DAT_00589364,DAT_00589360,DAT_005893d8);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_005893dc,DAT_005893dc);
    }
    for (uVar2 = 1; (int)uVar2 < 3; uVar2 = uVar2 + 1) {
      FUN_00588fe4(uVar2 & 0xff);
    }
  }
  return CONCAT44(local_c,local_10);
}

