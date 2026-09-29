
undefined8 FUN_0055448e(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 local_18;
  undefined4 local_14;
  
  puVar1 = DAT_00554d28;
  local_18 = param_3;
  local_14 = param_4;
  if (param_1 == 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      local_14 = DAT_00554f30;
      local_18 = 0x12d;
      FUN_0043d574(1,DAT_00554d3c,DAT_00554d38,DAT_00554f34);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00554f38,DAT_00554f38);
    }
  }
  else {
    FUN_0043c0e4(DAT_00554d28,0x48,0);
    puVar2 = DAT_00554f3c;
    uVar4 = FUN_0043de82(param_1);
    *puVar2 = uVar4;
    FUN_0043f4c0(*puVar2,0x240,0x120);
    FUN_0043f09a(*puVar2,0,0);
    FUN_0044129e(*puVar2,0,0);
    FUN_0044131c(*puVar2,0,0);
    FUN_0044146a(*puVar2,0,0);
    FUN_00554080(*puVar2,0,0);
    FUN_0043dfa4(*puVar2,0x70);
    uVar4 = FUN_0043de82(*puVar2);
    *puVar1 = uVar4;
    FUN_0043f4c0(*puVar1,0x240,0x120);
    FUN_0043f09a(*puVar1,0,0);
    FUN_0044129e(*puVar1,0,0);
    FUN_0044131c(*puVar1,0,0);
    FUN_0044146a(*puVar1,0,0);
    FUN_00554080(*puVar1,0,0);
    FUN_0043dfa4(*puVar1,0x10);
    uVar4 = FUN_0043de82(*puVar2);
    puVar1[4] = uVar4;
    FUN_0043f4c0(puVar1[4],0x240,0x120);
    FUN_0043f09a(puVar1[4],0,0);
    FUN_0044129e(puVar1[4],0,0);
    FUN_0044131c(puVar1[4],0,0);
    FUN_00554080(puVar1[4],0,0);
    FUN_0044146a(puVar1[4],0,0);
    FUN_0043dfa4(puVar1[4],0x10);
    FUN_00589152();
    FUN_0058966c();
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      local_14 = DAT_00554f40;
      local_18 = 0x158;
      FUN_0043d574(3,DAT_00554d3c,DAT_00554d38,DAT_00554f34);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc000000,DAT_005551cc);
    }
  }
  return CONCAT44(local_14,local_18);
}

