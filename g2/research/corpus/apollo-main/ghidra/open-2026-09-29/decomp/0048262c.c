
undefined8 FUN_0048262c(undefined4 param_1,undefined4 param_2,int param_3)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined8 uVar3;
  undefined8 uVar4;
  
  uVar3 = CONCAT44(param_2,param_1);
  uVar1 = 0;
  uVar2 = DAT_00482680;
  for (; param_3 != 0; param_3 = param_3 >> 1) {
    if (param_3 << 0x1f < 0) {
      uVar3 = FUN_004d4354((int)uVar3,(int)((ulonglong)uVar3 >> 0x20),uVar1,uVar2);
    }
    uVar4 = FUN_004d4354(uVar1,uVar2,uVar1,uVar2);
    uVar2 = (undefined4)((ulonglong)uVar4 >> 0x20);
    uVar1 = (undefined4)uVar4;
  }
  return uVar3;
}

