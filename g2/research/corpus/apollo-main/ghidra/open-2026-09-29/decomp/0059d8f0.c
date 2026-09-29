
undefined8 translate_ui_0059d8f0(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 local_18;
  undefined4 local_14;
  
  FUN_0043c0e4(DAT_0059df78,0x2c,0);
  puVar1 = DAT_0059e268;
  uVar2 = FUN_0043de82(param_1);
  *puVar1 = uVar2;
  FUN_0043dfa4(*puVar1,0x370);
  FUN_0043f4c0(*puVar1,0x240,0x120);
  FUN_0043f09a(*puVar1,0,0);
  uVar2 = FUN_0044104c(0);
  FUN_0044127e(*puVar1,uVar2,0);
  FUN_0044129e(*puVar1,0xff,0);
  FUN_0044131c(*puVar1,0,0);
  FUN_0044133a(*puVar1,0,0);
  FUN_00441378(*puVar1,0,0);
  FUN_00441386(*puVar1,0,0);
  FUN_004413be(*puVar1,0,0);
  FUN_0044146a(*puVar1,0,0);
  translate_ui_0059d380(*puVar1,0,0);
  iVar3 = FUN_0043d0ce();
  local_18 = param_2;
  local_14 = param_3;
  if (iVar3 << 0x1e < 0) {
    local_14 = DAT_0059e3b4;
    local_18 = 0xe9;
    FUN_0043d574(3,DAT_0059defc,DAT_0059def8,DAT_0059e3b8);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0xc000000,DAT_0059e5c8,DAT_0059e5c8);
  }
  return CONCAT44(local_14,local_18);
}

