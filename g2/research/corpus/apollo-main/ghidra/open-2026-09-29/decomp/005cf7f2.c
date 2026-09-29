
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

longlong semantic_production_test_screen_event
                   (int param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  uint uStack_18;
  
  puVar1 = _DAT_005cf8dc;
  uStack_18 = param_4;
  if (param_1 == 2) {
    uVar2 = FUN_0043de82(param_4);
    *puVar1 = uVar2;
    FUN_0043dfa4(*puVar1,0x10);
    FUN_0043f506(*puVar1,0x280);
    FUN_0043f568(*puVar1,0x1e0);
    FUN_0043dfa4(*puVar1,0x10);
    uVar2 = FUN_0044104c(0);
    FUN_0044127e(*puVar1,uVar2,0);
    FUN_0044129e(*puVar1,0xff,0);
    uStack_18 = param_4 & 0xff000000;
    FUN_004412ec(*puVar1,uStack_18,0);
    for (iVar4 = 0; iVar4 < 3; iVar4 = iVar4 + 1) {
      for (iVar5 = 0; iVar5 < 3; iVar5 = iVar5 + 1) {
        uVar2 = FUN_0043de82(*puVar1);
        FUN_0043f4c0(uVar2,10,10);
        uVar3 = FUN_00441068(0xff,0xff,0xff);
        FUN_0044127e(uVar2,uVar3,0);
        FUN_0044131c(uVar2,0,0);
        FUN_0043f09a(uVar2,iVar5 * 200 + 0x42,iVar4 * 100 + 0x15);
      }
    }
    *(undefined4 *)(_DAT_005cf8e0 + 4) = *puVar1;
  }
  return (ulonglong)uStack_18 << 0x20;
}

