
undefined2 FUN_00513748(undefined4 param_1)

{
  undefined1 local_10;
  undefined1 local_f;
  undefined4 uStack_c;
  
  uStack_c = param_1;
  FUN_0043c0e4(&local_10,2,0);
  hal_i2c_transfer_full(2,0x45,&uStack_c,1,&local_10,2);
  return CONCAT11(local_10,local_f);
}

