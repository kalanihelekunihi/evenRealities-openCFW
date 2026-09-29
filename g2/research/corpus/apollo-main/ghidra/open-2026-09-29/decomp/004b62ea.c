
undefined4
dmConnExecCback(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  
  for (bVar1 = 0; bVar1 < 5; bVar1 = bVar1 + 1) {
    if (*(int *)(DAT_004b6520 + (uint)bVar1 * 4 + 0x90) != 0) {
      (**(code **)(DAT_004b6520 + (uint)bVar1 * 4 + 0x90))(param_1);
    }
  }
  return param_4;
}

