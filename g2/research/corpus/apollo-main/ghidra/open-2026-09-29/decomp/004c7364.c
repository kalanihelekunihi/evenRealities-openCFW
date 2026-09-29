
undefined8 FUN_004c7364(undefined4 *param_1,int param_2,byte param_3,undefined4 param_4)

{
  byte bVar1;
  undefined4 local_10;
  
  bVar1 = 0;
  local_10 = param_4;
  if (param_3 == 0) {
    *(int *)(param_1[2] + 8) = param_2;
  }
  else if (param_3 == 2) {
    bVar1 = (**(code **)(param_1[1] + 0x1c))(param_1[1],*param_1,param_2,2);
    if ((bVar1 == 0) &&
       (bVar1 = (**(code **)(param_1[1] + 0x20))(param_1[1],*param_1,&local_10), bVar1 == 0)) {
      *(undefined4 *)(param_1[2] + 8) = local_10;
    }
  }
  else if (param_3 < 2) {
    *(int *)(param_1[2] + 8) = param_2 + *(int *)(param_1[2] + 8);
  }
  return CONCAT44(local_10,(uint)bVar1);
}

