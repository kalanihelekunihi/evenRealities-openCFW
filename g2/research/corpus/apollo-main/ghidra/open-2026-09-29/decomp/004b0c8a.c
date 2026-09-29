
undefined8 FUN_004b0c8a(char param_1,undefined4 param_2)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  
  iVar1 = FUN_004c791a();
  if (param_1 != '\0') {
    FUN_00514cf2(iVar1 + 0x90);
    FUN_00514d00(iVar1 + 0x90);
    FUN_005144ba();
    iVar2 = FUN_0051419a(2,1);
    if (iVar2 != 0) {
      param_2 = DAT_004b107c;
      FUN_0044d25c(3,DAT_004b1054,0x21a,DAT_004b1094,DAT_004b107c,iVar2);
      uVar3 = 0;
      goto LAB_004b0d36;
    }
  }
  FUN_004b0886(iVar1);
  iVar1 = FUN_004b128a();
  if (iVar1 != 0) {
    uVar3 = FUN_004b0594(iVar1);
    param_2 = DAT_004b1098;
    FUN_0044d25c(3,DAT_004b1054,0x22b,DAT_004b1094,DAT_004b1098,iVar1,uVar3);
  }
  iVar1 = FUN_0051564c();
  if (iVar1 != 0) {
    uVar3 = FUN_004b0584(iVar1);
    param_2 = DAT_004b109c;
    FUN_0044d25c(3,DAT_004b1054,0x22f,DAT_004b1094,DAT_004b109c,iVar1,uVar3);
  }
  uVar3 = 1;
LAB_004b0d36:
  return CONCAT44(param_2,uVar3);
}

