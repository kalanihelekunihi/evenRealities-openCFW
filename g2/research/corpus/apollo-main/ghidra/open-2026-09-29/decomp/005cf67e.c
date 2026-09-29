
longlong semantic_pdt_gray_screen_event
                   (int param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  char cVar4;
  int iVar5;
  uint local_28;
  
  puVar1 = DAT_005cf79c;
  local_28 = param_3;
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
    local_28 = param_3 & 0xff000000;
    FUN_004412ec(*puVar1,local_28,0);
    for (iVar5 = 0; iVar5 < 8; iVar5 = iVar5 + 1) {
      uVar2 = FUN_0043de82(*puVar1);
      FUN_0043dfa4(uVar2,0x10);
      FUN_0043f4c0(uVar2,0x48,0x120);
      FUN_0043f09a(uVar2,iVar5 * 0x48,0);
      FUN_0044131c(uVar2,0,0);
      FUN_0044146a(uVar2,0,0);
      cVar4 = *(char *)(DAT_005cf7a0 + iVar5) * '\x11';
      uVar3 = FUN_00441068(cVar4,cVar4,cVar4);
      FUN_0044127e(uVar2,uVar3,0);
      FUN_0044129e(uVar2,0xff,0);
    }
    *(undefined4 *)(DAT_005cf7a4 + 4) = *puVar1;
  }
  return (ulonglong)local_28 << 0x20;
}

