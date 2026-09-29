
undefined8 FUN_005d3362(int param_1,int param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  int local_20;
  int local_1c;
  undefined4 uStack_18;
  
  local_20 = param_2;
  local_1c = param_3;
  uStack_18 = param_4;
  FUN_0043c0e4(param_3,0x10,0);
  if ((*(int *)(*(int *)(*(int *)(param_1 + 4) + 0x80) + 0x34) == 0) &&
     (param_2 = FUN_005d2196(*(undefined4 *)(param_1 + 0x214),param_2), param_2 < 0)) {
    iVar1 = 0x12;
  }
  else {
    iVar1 = (**(code **)(param_1 + 0x250))(*(undefined4 *)(param_1 + 4),param_2,&local_20,&local_1c)
    ;
    if (iVar1 == 0) {
      *(int *)(param_3 + 4) = local_20;
      *(int *)(param_3 + 8) = local_20 + local_1c;
      *(undefined4 *)(param_3 + 0xc) = *(undefined4 *)(param_3 + 4);
      iVar1 = 0;
    }
  }
  return CONCAT44(local_20,iVar1);
}

