
undefined8 FUN_004d5172(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = (**(code **)(*param_1 + 0x20))(param_1,param_2);
  if (iVar1 != 0) {
    (**(code **)(*param_1 + 0x14))
              (param_1,iVar1,param_2,*(code **)(*param_1 + 0x14),param_3,param_4);
    uVar2 = FUN_004d5396(iVar1);
    (*(code *)param_1[6])(uVar2,param_2);
    FUN_004d54da(iVar1);
  }
  else {
    param_3 = DAT_004d5268;
    FUN_0044d25c(3,DAT_004d523c,0x14b,DAT_004d526c);
  }
  return CONCAT44(param_3,(uint)(iVar1 != 0));
}

