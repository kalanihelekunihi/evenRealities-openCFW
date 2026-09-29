
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_004d2f48(void)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  undefined4 uVar3;
  int iVar4;
  
  puVar1 = _DAT_004d3478;
  uVar3 = FUN_0043de82();
  *puVar1 = uVar3;
  FUN_0043f506(*puVar1,0x3fffffff);
  FUN_0043f568(*puVar1,0x28);
  FUN_0043f6b8(*puVar1,2,0,0);
  FUN_0043dfa4(*puVar1,0x2004);
  FUN_0044e368(*puVar1,0);
  uVar3 = FUN_0044104c(0);
  FUN_0044127e(*puVar1,uVar3,0);
  FUN_0044129e(*puVar1,0xff,0);
  uVar3 = FUN_0044104c(0);
  FUN_004412ec(*puVar1,uVar3,0);
  FUN_0044131c(*puVar1,0,0);
  FUN_004d2b9a(*puVar1,0,0);
  puVar2 = _DAT_004d347c;
  uVar3 = FUN_0043de82(*puVar1);
  *puVar2 = uVar3;
  FUN_0043f506(*puVar2,0x3fffffff);
  FUN_0043f568(*puVar2,0x28);
  iVar4 = FUN_0045a568();
  if (iVar4 == 1) {
    FUN_0043f0e0(*puVar2,0);
  }
  else {
    FUN_0043f0e0(*puVar2,0x10);
  }
  FUN_0043f142(*puVar2,0);
  FUN_0044e368(*puVar2,0);
  FUN_0044e3ca(*puVar2,0xc);
  FUN_0044129e(*puVar2,0,0);
  FUN_0044146a(*puVar2,10,0);
  uVar3 = FUN_0044104c(0xffffff);
  FUN_004412ec(*puVar2,uVar3,0);
  FUN_0044131c(*puVar2,1,0);
  FUN_0044120e(*puVar2,0,0);
  FUN_0044121c(*puVar2,0,0);
  FUN_0044122a(*puVar2,0xc,0);
  FUN_00441238(*puVar2,0xc,0);
  return;
}

