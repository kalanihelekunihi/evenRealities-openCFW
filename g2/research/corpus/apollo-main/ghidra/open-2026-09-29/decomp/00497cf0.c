
undefined8 service_ancc_state_sync(undefined1 param_1,undefined4 param_2)

{
  undefined1 local_14;
  undefined1 uStack_13;
  undefined2 uStack_12;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  uStack_10 = DAT_00497db0[1];
  local_14 = (undefined1)*DAT_00497db0;
  uStack_12 = (undefined2)((uint)*DAT_00497db0 >> 0x10);
  uStack_13 = param_1;
  uStack_c = param_2;
  FUN_00439be4(&uStack_12,&uStack_c,4);
  FUN_00464f76(4,&local_14,6,0);
  return CONCAT26(uStack_12,CONCAT15(uStack_13,CONCAT14(local_14,5)));
}

