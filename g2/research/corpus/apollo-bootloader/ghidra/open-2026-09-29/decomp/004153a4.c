
undefined8 FUN_004153a4(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  int iVar3;
  uint uVar4;
  
  puVar2 = (undefined4 *)FUN_0041552c(0x60);
  if (puVar2 == (undefined4 *)0x0) {
    puVar2 = (undefined4 *)0x0;
  }
  else {
    *puVar2 = DAT_004155e8;
    iVar3 = FUN_00415ffa(param_2,&DAT_00415580);
    uVar4 = (uint)(iVar3 != 0);
    iVar3 = FUN_00415ffa(param_2,&DAT_00415584);
    if (iVar3 != 0) {
      uVar4 = uVar4 | 0x502;
    }
    iVar3 = FUN_00415ffa(param_2,&DAT_00415588);
    if (iVar3 != 0) {
      uVar4 = uVar4 | 0x902;
    }
    iVar3 = FUN_00415ffa(param_2,&LAB_0041558c);
    puVar1 = DAT_004155ec;
    if (iVar3 != 0) {
      uVar4 = uVar4 | 3;
    }
    iVar3 = FUN_004166aa(*DAT_004155ec,1000);
    if (iVar3 == 0) {
      iVar3 = FUN_00415146(*puVar2,puVar2 + 1,param_1,uVar4);
      FUN_00416710(*puVar1);
      if (iVar3 < 0) {
        FUN_00415558(puVar2);
        puVar2 = (undefined4 *)0x0;
      }
    }
    else {
      FUN_00415558(puVar2);
      puVar2 = (undefined4 *)0x0;
    }
  }
  return CONCAT44(param_4,puVar2);
}

