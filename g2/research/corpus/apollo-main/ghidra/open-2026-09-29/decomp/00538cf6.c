
undefined8
WsfQueueCount(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  ushort uVar1;
  
  uVar1 = 0;
  WsfCsEnter();
  for (param_1 = (undefined4 *)*param_1; param_1 != (undefined4 *)0x0;
      param_1 = (undefined4 *)*param_1) {
    uVar1 = uVar1 + 1;
  }
  WsfCsExit();
  return CONCAT44(param_4,(uint)uVar1);
}

