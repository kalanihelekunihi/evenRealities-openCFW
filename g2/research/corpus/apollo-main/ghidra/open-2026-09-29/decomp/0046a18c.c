
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void system_close_selection_animation_0046a18c(undefined4 param_1)

{
  undefined4 *puVar1;
  int *piVar2;
  undefined4 *puVar3;
  undefined4 uVar4;
  int iVar5;
  
  puVar1 = DAT_0046acc4;
  uVar4 = FUN_0043de82(param_1);
  *puVar1 = uVar4;
  piVar2 = _DAT_0046acc8;
  FUN_0043f4c0(*puVar1,200,*_DAT_0046acc8);
  iVar5 = FUN_0043fd9e(param_1);
  FUN_0043f0e0(*puVar1,(iVar5 + -200) / 2);
  iVar5 = FUN_0043fdda(param_1);
  FUN_0043f142(*puVar1,(iVar5 - *piVar2) / 2);
  FUN_0043dfa4(*puVar1,0x2004);
  FUN_0044e368(*puVar1,0);
  uVar4 = FUN_0044104c(0);
  FUN_0044127e(*puVar1,uVar4,0);
  FUN_0044129e(*puVar1,0xff,0);
  uVar4 = FUN_0044104c(0);
  FUN_004412ec(*puVar1,uVar4,0);
  FUN_0044131c(*puVar1,0,0);
  system_close_fifo_reset_00469bf4(*puVar1,0,0);
  puVar3 = _DAT_0046accc;
  uVar4 = FUN_0043de82(*puVar1);
  *puVar3 = uVar4;
  FUN_0043f4c0(*puVar3,0xb8,*piVar2);
  iVar5 = FUN_0045a568();
  if (iVar5 == 1) {
    FUN_0043f0e0(*puVar3,0);
  }
  else {
    FUN_0043f0e0(*puVar3,*_DAT_0046acd0);
  }
  FUN_0043f142(*puVar3,0);
  FUN_0044e368(*puVar3,0);
  FUN_0044e3ca(*puVar3,0xc);
  FUN_0044129e(*puVar3,0,0);
  FUN_0044146a(*puVar3,10,0);
  uVar4 = FUN_0044104c(0xffffff);
  FUN_004412ec(*puVar3,uVar4,0);
  FUN_0044131c(*puVar3,1,0);
  FUN_0044120e(*puVar3,0,0);
  FUN_0044121c(*puVar3,0,0);
  FUN_0044122a(*puVar3,0,0);
  FUN_00441238(*puVar3,0,0);
  return;
}

