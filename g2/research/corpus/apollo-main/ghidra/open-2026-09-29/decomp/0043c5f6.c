
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_0043c5f6(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined *param_4)

{
  int *piVar1;
  undefined4 *puVar2;
  char *pcVar3;
  int iVar4;
  undefined4 uVar5;
  undefined4 uStack_18;
  undefined *puStack_14;
  
  pcVar3 = _DAT_0043c798;
  piVar1 = _DAT_0043c788;
  uStack_18 = param_3;
  puStack_14 = param_4;
  if ((*_DAT_0043c798 == '\0') && (*_DAT_0043c788 != 0)) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      puStack_14 = PTR_DAT_0043c7a8;
      uStack_18 = 0x7a;
      FUN_0043d574(3,DAT_0043c764,DAT_0043c760,PTR_s_init_rectangle_system_0043c7ac);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_DAT_0043c7b0,PTR_DAT_0043c7b0);
    }
    puVar2 = _DAT_0043c794;
    uVar5 = FUN_0043de82(*piVar1);
    *puVar2 = uVar5;
    FUN_0043f4c0(*puVar2,0x240,0x30);
    FUN_0043f09a(*puVar2,0,0);
    uVar5 = FUN_00441068(0xff,0xff,0xff);
    FUN_0044127e(*puVar2,uVar5,0);
    FUN_0044131c(*puVar2,0,0);
    FUN_0044129e(*puVar2,0xff,0);
    *_DAT_0043c7b4 = 0;
    *pcVar3 = '\x01';
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      puStack_14 = PTR_DAT_0043c7b8;
      uStack_18 = 0x88;
      FUN_0043d574(3,DAT_0043c764,DAT_0043c760,PTR_s_init_rectangle_system_0043c7ac);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0xc000000,PTR_DAT_0043c7bc);
    }
  }
  return CONCAT44(puStack_14,uStack_18);
}

