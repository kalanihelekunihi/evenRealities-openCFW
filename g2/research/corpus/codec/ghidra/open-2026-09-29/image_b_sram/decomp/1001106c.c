
/* WARNING: Removing unreachable block (ram,0x10011086) */
/* WARNING: Removing unreachable block (ram,0x10011176) */

void FUN_1001106c(undefined4 param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  undefined4 uVar7;
  uint uVar8;
  int iVar9;
  
  iVar1 = DAT_1001118c;
  uVar8 = param_2 & 0x7fffffff;
  uVar4 = param_2;
  uVar2 = FUN_10011e50(param_1,param_2,param_1,param_2);
  iVar9 = iVar1 + 0x20;
  uVar7 = *(undefined4 *)(iVar1 + 0x28);
  uVar6 = *(uint *)(iVar1 + 0x2c);
  do {
    uVar5 = uVar4;
    FUN_10011e50(uVar2,uVar4,uVar7,uVar6);
    iVar9 = iVar9 + -8;
    uVar7 = FUN_10011de4();
    uVar6 = uVar5;
  } while (iVar1 + -8 != iVar9);
  uVar6 = uVar4;
  FUN_10011e50(uVar2,uVar4,uVar7,uVar5);
  uVar7 = FUN_10011e50();
  uVar3 = FUN_10011e50(param_1,param_2,param_3,param_4);
  FUN_10011e14(uVar7,uVar6,uVar3,param_2);
  FUN_10011e50(uVar2,uVar4,0,0);
  uVar2 = FUN_10011e14();
  if ((int)uVar8 <= DAT_10011190) {
    FUN_10011e14(0,0,uVar2,uVar4);
    return;
  }
  if (uVar8 == 0) {
    uVar3 = 0;
    uVar7 = FUN_10011e14(0,0,0,0);
  }
  else {
    uVar7 = 0;
    uVar3 = 0;
  }
  uVar2 = FUN_10011e14(uVar2,uVar4,0,0);
  FUN_10011e14(uVar7,uVar3,uVar2,uVar4);
  return;
}

