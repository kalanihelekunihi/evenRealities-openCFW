
undefined8 FUN_0052edf0(undefined4 param_1,char param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  
  iVar1 = FUN_0052dd1c(0);
  if (iVar1 == 0) {
    uVar3 = *DAT_0052f1f8;
  }
  else {
    FUN_0052dd24();
    uVar3 = *DAT_0052f208;
  }
  iVar1 = FUN_0052e8be(param_1);
  if (iVar1 == 0) {
    if ((param_2 == '\0') && (iVar2 = FUN_0052e7c0(param_1), iVar2 != 0)) {
      FUN_004733ee(DAT_0052f290);
    }
    else {
      FUN_004733ee(DAT_0052f278);
      if (*DAT_0052f270 != '\0') {
        FUN_0052ed34(param_1);
      }
      iVar1 = FUN_0052e9b4(param_1);
      if (iVar1 == 0) {
        iVar1 = FUN_0052ebca(param_1,uVar3);
        if (iVar1 == 0) {
          FUN_004733ee(DAT_0052f280,uVar3);
          iVar1 = FUN_0052ec84(param_1);
          if (iVar1 == 0) {
            FUN_004733ee(DAT_0052f284);
          }
          else {
            FUN_004733ee(DAT_0052f28c,iVar1);
          }
        }
        else {
          FUN_004733ee(DAT_0052f288,iVar1);
        }
      }
      else {
        FUN_004733ee(DAT_0052f27c,iVar1);
      }
    }
  }
  else {
    FUN_004733ee(DAT_0052f274,iVar1);
  }
  if (iVar1 == 0) {
    FUN_00480f0c(0xf,*DAT_0052f294);
  }
  return CONCAT44(param_4,iVar1);
}

