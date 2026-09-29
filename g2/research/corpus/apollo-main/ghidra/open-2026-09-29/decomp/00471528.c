
undefined8 FUN_00471528(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  undefined1 local_14;
  undefined1 local_13;
  undefined2 uStack_12;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  local_14 = (undefined1)param_2;
  local_13 = (undefined1)((uint)param_2 >> 8);
  uStack_12 = (undefined2)((uint)param_2 >> 0x10);
  uStack_10 = param_3;
  uStack_c = param_4;
  FUN_0043c0e4(&local_14,10,0,param_4,param_1);
  local_14 = 2;
  local_13 = 0;
  uVar1 = 5;
  FUN_00465480(0x20,&local_14,2,0);
  return CONCAT26(uStack_12,CONCAT15(local_13,CONCAT14(local_14,uVar1)));
}

