
undefined8 FUN_00460424(undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  undefined1 local_14;
  undefined1 local_13;
  undefined2 uStack_12;
  undefined4 uStack_10;
  
  local_14 = (undefined1)param_3;
  local_13 = (undefined1)((uint)param_3 >> 8);
  uStack_12 = (undefined2)((uint)param_3 >> 0x10);
  uStack_10 = param_4;
  FUN_0043c0e4(&local_14,2,0,param_4,param_2);
  local_14 = 0;
  uVar1 = 4;
  local_13 = param_1;
  FUN_00464f76(3,&local_14,2,0);
  return CONCAT26(uStack_12,CONCAT15(local_13,CONCAT14(local_14,uVar1)));
}

