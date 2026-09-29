
undefined8 FUN_005696d4(int param_1,byte param_2,undefined4 *param_3,undefined4 *param_4)

{
  undefined4 uVar1;
  undefined4 local_18;
  undefined4 local_14;
  
  local_14 = 0;
  local_18 = 0;
  if ((param_1 == 0) || (1 < param_2)) {
    uVar1 = 6;
  }
  else {
    uVar1 = FUN_005686be(param_1 + (uint)param_2 * 0x20 + 0x34,&local_14,&local_18);
  }
  if (param_3 != (undefined4 *)0x0) {
    *param_3 = local_14;
  }
  if (param_4 != (undefined4 *)0x0) {
    *param_4 = local_18;
  }
  return CONCAT44(local_18,uVar1);
}

