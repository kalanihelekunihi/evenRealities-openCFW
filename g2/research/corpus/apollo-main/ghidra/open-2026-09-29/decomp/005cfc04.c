
undefined8
FUN_005cfc04(undefined4 param_1,undefined4 *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 local_10;
  undefined4 local_c;
  
  local_10 = CONCAT31((int3)((uint)param_3 >> 8),3);
  local_c = param_4;
  iVar1 = FUN_005cf9e8(param_1,&local_10,1);
  if (iVar1 == 1) {
    *param_2 = local_c;
    uVar2 = 0;
  }
  else {
    uVar2 = 0xa0;
  }
  return CONCAT44(local_10,uVar2);
}

