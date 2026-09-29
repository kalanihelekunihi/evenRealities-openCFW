
undefined8 FUN_004d51c0(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uVar4;
  
  uVar4 = param_2;
  cVar1 = (**(code **)(*param_1 + 0x24))(param_1,param_2,0,param_3,param_2,param_3,param_4);
  if (cVar1 == '\x01') {
    uVar4 = DAT_004d5270;
    FUN_0044d25c(3,DAT_004d523c,0x159,DAT_004d5274,DAT_004d5270,param_2,param_1[2]);
    uVar2 = 0;
  }
  else {
    while (cVar1 == '\x02') {
      iVar3 = FUN_004d5172(param_1,param_3);
      if (iVar3 == 0) {
        uVar2 = 0;
        goto LAB_004d522a;
      }
      cVar1 = (**(code **)(*param_1 + 0x24))(param_1,param_2,0,param_3);
    }
    uVar2 = (**(code **)(*param_1 + 0x10))(param_1,param_2,param_3);
  }
LAB_004d522a:
  return CONCAT44(uVar4,uVar2);
}

