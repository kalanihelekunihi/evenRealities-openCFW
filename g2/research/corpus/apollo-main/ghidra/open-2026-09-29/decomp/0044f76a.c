
undefined8 FUN_0044f76a(int param_1,int param_2)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r7;
  
  if (param_2 == 0) {
    FUN_0044f758();
    iVar2 = DAT_0044f7a4;
  }
  else if (param_1 == DAT_0044f7a4) {
    iVar2 = FUN_0044f718(param_2);
  }
  else {
    iVar2 = FUN_0048432a();
    uVar1 = DAT_0044f7a8;
    if (iVar2 == 0) {
      FUN_0044d25c(3,DAT_0044f7b0,0xa2,DAT_0044f7ac);
      iVar2 = 0;
      unaff_r7 = uVar1;
    }
  }
  return CONCAT44(unaff_r7,iVar2);
}

