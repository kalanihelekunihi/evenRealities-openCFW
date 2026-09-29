
undefined8 FUN_004d0868(undefined4 param_1,int param_2,uint param_3)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;
  int iVar7;
  
  if ((param_2 == 0) || (param_3 != 0)) {
    if (param_2 == 0) {
      iVar1 = FUN_004d0722(param_1,param_3);
    }
    else {
      uVar2 = FUN_004cfe04(param_2);
      uVar3 = FUN_004cfe44(uVar2);
      uVar4 = FUN_004cfd70(uVar2);
      iVar1 = FUN_004cfd70(uVar3);
      iVar7 = *DAT_004d0964;
      uVar5 = FUN_004cff42(param_3,4);
      iVar6 = FUN_004cfdb4(uVar2);
      if (iVar6 != 0) {
        FUN_004d09b4(DAT_004d09b0,DAT_004d09a0,0x4d1);
      }
      if ((uVar4 < uVar5) &&
         ((iVar6 = FUN_004cfdb4(uVar3), iVar6 == 0 || (iVar7 + iVar1 + uVar4 < uVar5)))) {
        iVar1 = FUN_004d0722(param_1,param_3);
        if (iVar1 != 0) {
          if (uVar4 < param_3) {
            param_3 = uVar4;
          }
          FUN_00439be4(iVar1,param_2,param_3);
          FUN_004d0808(param_1,param_2);
        }
      }
      else {
        if (uVar4 < uVar5) {
          FUN_004d033a(param_1,uVar2);
          FUN_004cfeac(uVar2);
        }
        FUN_004d03f0(param_1,uVar2,uVar5);
        iVar1 = param_2;
      }
    }
  }
  else {
    FUN_004d0808(param_1,param_2);
    iVar1 = 0;
  }
  return CONCAT44(param_1,iVar1);
}

