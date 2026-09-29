
undefined8
als_function_01(undefined1 param_1,undefined1 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 local_18;
  undefined1 local_17;
  undefined2 uStack_16;
  undefined4 uStack_14;
  
  local_18 = (undefined1)param_3;
  local_17 = (undefined1)((uint)param_3 >> 8);
  uStack_16 = (undefined2)((uint)param_3 >> 0x10);
  uStack_14 = param_4;
  FUN_0043c0e4(&local_18,2,0);
  local_18 = param_1;
  local_17 = param_2;
  FUN_00464d1c(0x10e,&local_18,2,0);
  return CONCAT44(uStack_14,CONCAT22(uStack_16,CONCAT11(local_17,local_18)));
}

