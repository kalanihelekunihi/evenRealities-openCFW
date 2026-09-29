
undefined4 FUN_10003024(int *param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  undefined4 uStack_54;
  undefined4 uStack_50;
  undefined4 uStack_4c;
  undefined4 uStack_48;
  undefined4 uStack_44;
  undefined4 uStack_40;
  undefined4 uStack_3c;
  undefined4 uStack_38;
  undefined4 uStack_34;
  undefined4 uStack_30;
  undefined4 uStack_2c;
  undefined4 uStack_28;
  
  iVar4 = param_1[1];
  iVar1 = FUN_100041b8();
  if (iVar1 < 0) {
LAB_100030a8:
    uVar2 = 0xffffffff;
  }
  else {
    iVar3 = param_1[0xd];
    param_1[0x1a] = iVar1;
    uStack_4c = 1;
    uStack_44 = 1;
    uStack_54 = 0;
    uStack_40 = 0;
    uStack_50 = FUN_10002fb4(iVar3,param_1 + 0xe);
    if (*param_1 == 0) {
      uStack_48 = 6;
    }
    else {
      if (*param_1 != 1) goto LAB_100030a8;
      uStack_48 = 4;
    }
    uStack_38 = 0;
    uStack_2c = 0;
    uStack_30 = 0;
    uStack_3c = FUN_10002fb4(iVar3,param_1 + 0xe,0);
    uStack_28 = 2;
    uStack_34 = 0;
    FUN_1000432c(iVar1,PTR_LAB_100030b0,param_1);
    FUN_10004340(param_2,iVar4,param_3,iVar1,&uStack_54);
    uVar2 = 0;
  }
  return uVar2;
}

