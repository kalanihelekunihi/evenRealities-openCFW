
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_005b14ce(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined *param_4)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  puVar1 = _DAT_005b1a0c;
  uVar2 = FUN_0043de82();
  *puVar1 = uVar2;
  FUN_0043f4c0(*puVar1,0x240,0x120);
  FUN_0043f09a(*puVar1,0,0);
  FUN_0044129e(*puVar1,0,0);
  FUN_0044131c(*puVar1,0,0);
  FUN_0044146a(*puVar1,0,0);
  func_0x005b0ac4(*puVar1,0,0);
  FUN_0043dfa4(*puVar1,0x70);
  FUN_005b3cba();
  FUN_0058966c();
  iVar3 = FUN_0043d0ce();
  uStack_10 = param_3;
  uStack_c = param_4;
  if (iVar3 << 0x1e < 0) {
    uStack_c = PTR_s_init_completed_005b1abc;
    uStack_10 = 0x1ad;
    FUN_0043d574(4,DAT_005b15d0,DAT_005b15cc,PTR_s_conversate_ui_init_005b1ac0);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0x10000000,PTR_s__conversate_ui_init_completed_005b1ac4,
                        PTR_s__conversate_ui_init_completed_005b1ac4);
  }
  return CONCAT44(uStack_c,uStack_10);
}

