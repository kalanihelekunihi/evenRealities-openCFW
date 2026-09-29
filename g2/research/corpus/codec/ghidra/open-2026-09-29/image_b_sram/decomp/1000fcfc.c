
int FUN_1000fcfc(undefined4 param_1,uint param_2,undefined4 *param_3)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  
  uVar6 = DAT_1001005c;
  uVar10 = param_2 & 0x3fffffff;
  if ((int)uVar10 <= DAT_10010054) {
    *param_3 = param_1;
    param_3[1] = param_2;
    param_3[2] = 0;
    param_3[3] = 0;
    return 0;
  }
  if (DAT_10010058 < (int)uVar10) {
    if (DAT_1001006c < (int)uVar10) {
      uVar10 = ((uVar10 >> 0x14) - 0x469) / 0x36;
      uVar3 = FUN_10011e50(param_1,param_2,*(undefined4 *)(PTR_DAT_10010070 + uVar10 * 8),
                           *(undefined4 *)(PTR_DAT_10010070 + (uVar10 * 2 + 1) * 4));
      uVar10 = param_2;
      uVar3 = FUN_10011e14(uVar3,param_2,0);
      uVar6 = param_2;
      uVar2 = FUN_10011e50(0,param_2,0,DAT_10010074);
      uVar7 = uVar10;
      uVar5 = FUN_10011e50(uVar3,uVar10,0,DAT_10010078);
      uVar2 = FUN_10011de4(uVar2,uVar6,uVar5,uVar7);
      uVar5 = FUN_10011e50(0,param_2,0,DAT_10010078);
      uVar7 = uVar6;
      uVar5 = FUN_10011de4(uVar2,uVar6,uVar5,param_2);
      uVar8 = uVar7;
      uVar1 = FUN_10011e14();
      FUN_10011e14(uVar2,uVar6,uVar1,uVar8,param_2);
      FUN_10011e50(uVar3,uVar10,0,DAT_10010074);
      uVar3 = FUN_10011de4();
      FUN_1000fc5c(uVar5,uVar7,DAT_1001007c,DAT_10010080);
      FUN_10012050();
      FUN_10011e50();
      FUN_10011de4();
      iVar4 = FUN_100122f8();
      uVar2 = FUN_1000fc5c(uVar5,uVar7,DAT_1001007c,DAT_10010084);
      FUN_10011de4(uVar3,uVar10,uVar2,uVar7);
      FUN_1000fc5c();
      uVar3 = FUN_10012050();
      *param_3 = uVar3;
      param_3[1] = uVar10;
      return iVar4 / 2;
    }
    uVar6 = param_2;
    uVar3 = FUN_1000fc58(param_1);
    uVar7 = uVar6;
    FUN_10011e50();
    FUN_10011de4();
    iVar4 = FUN_100122f8();
    uVar2 = FUN_10012290();
    uVar8 = uVar7;
    uVar5 = FUN_10011e50();
    uVar3 = FUN_10011e14(uVar3,uVar6,uVar5,uVar8);
    uVar9 = uVar7;
    uVar5 = FUN_10011e50(uVar2,uVar7,DAT_10010064,DAT_10010068);
    uVar8 = uVar6;
    uVar5 = FUN_10011e14(uVar3,uVar6,uVar5,uVar7);
    uVar7 = uVar6;
    if (0x10 < (int)(((int)uVar10 >> 0x14) - ((uVar8 & 0x3fffffff) >> 0x14))) {
      uVar10 = uVar9;
      uVar5 = FUN_10011e50(uVar2,uVar9,0,DAT_10010068);
      uVar5 = FUN_10011e14(uVar3,uVar6,uVar5,uVar10);
      uVar10 = uVar9;
      uVar3 = FUN_10011e50(uVar2,uVar9,0,DAT_10010094);
      uVar7 = uVar6;
      uVar3 = FUN_10011e14(uVar5,uVar6,uVar3,uVar9);
      FUN_10011e14(uVar5,uVar6,uVar3,uVar7);
      FUN_10011e14();
      FUN_10011e50(uVar2,uVar10,DAT_10010098,DAT_1001009c,uVar2,uVar10,uVar9);
      uVar2 = FUN_10011e14();
      uVar8 = uVar7;
      uVar5 = FUN_10011e14(uVar3,uVar7,uVar2,uVar10);
    }
    *param_3 = uVar5;
    param_3[1] = uVar8;
    FUN_10011e14(uVar3,uVar7,uVar5,uVar8);
    uVar3 = FUN_10011e14();
    param_3[2] = uVar3;
    param_3[3] = uVar7;
    if ((int)param_2 < 0) {
      param_3[1] = uVar8;
      param_3[3] = uVar7;
      iVar4 = -iVar4;
    }
  }
  else {
    uVar7 = DAT_1001005c;
    if ((int)param_2 < 1) {
      uVar7 = DAT_10010060;
    }
    uVar3 = 0;
    iVar4 = 1;
    if ((int)param_2 < 1) {
      iVar4 = -1;
    }
    uVar1 = FUN_10011e14(param_1,param_2,0,uVar7);
    uVar2 = DAT_10010064;
    uVar5 = DAT_10010068;
    if (uVar10 == uVar6) {
      uVar2 = uVar3;
      uVar5 = FUN_10011e50(0,0,0,DAT_10010068);
      uVar1 = FUN_10011e14(uVar1,param_2,uVar5,uVar2);
      uVar2 = DAT_100100a0;
      uVar5 = DAT_10010094;
    }
    uVar2 = FUN_10011e50(0,0,uVar2,uVar5);
    uVar10 = param_2;
    uVar3 = FUN_10011e14(uVar1,param_2,uVar2,uVar3);
    *param_3 = uVar3;
    param_3[1] = uVar10;
    FUN_10011e14(uVar1,param_2,uVar3,uVar10);
    uVar3 = FUN_10011e14();
    param_3[2] = uVar3;
    param_3[3] = param_2;
  }
  return iVar4;
}

