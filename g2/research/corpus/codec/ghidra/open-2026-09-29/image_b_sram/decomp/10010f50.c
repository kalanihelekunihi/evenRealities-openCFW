
/* WARNING: Removing unreachable block (ram,0x10010f6e) */
/* WARNING: Removing unreachable block (ram,0x10011062) */

undefined4
FUN_10010f50(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,int param_5
            )

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  int iVar8;
  undefined4 uVar9;
  
  uVar5 = param_2;
  uVar2 = FUN_10011e50(param_1,param_2,param_1,param_2);
  iVar1 = DAT_10011180;
  uVar6 = param_2;
  uVar3 = FUN_10011e50(param_1,param_2,uVar2,uVar5);
  iVar8 = iVar1 + 0x18;
  uVar9 = *(undefined4 *)(iVar1 + 0x20);
  uVar4 = *(undefined4 *)(iVar1 + 0x24);
  do {
    uVar7 = uVar5;
    FUN_10011e50(uVar2,uVar5,uVar9,uVar4);
    iVar8 = iVar8 + -8;
    uVar9 = FUN_10011de4();
    uVar4 = uVar7;
  } while (iVar8 != iVar1 + -8);
  if (param_5 == 0) {
    FUN_10011e50(uVar2,uVar5,uVar9,uVar7);
    FUN_10011e14();
    FUN_10011e50();
    uVar5 = FUN_10011de4();
    return uVar5;
  }
  uVar4 = FUN_10011e50(param_3,param_4,0,0);
  uVar5 = uVar6;
  uVar2 = FUN_10011e50(uVar3,uVar6,uVar9,uVar7);
  FUN_10011e14(uVar4,param_4,uVar2,uVar5);
  FUN_10011e50();
  uVar5 = FUN_10011e14();
  uVar4 = FUN_10011e50(uVar3,uVar6,DAT_10011184,DAT_10011188);
  uVar5 = FUN_10011de4(uVar5,param_4,uVar4,uVar6);
  uVar5 = FUN_10011e14(param_1,param_2,uVar5,param_4);
  return uVar5;
}

