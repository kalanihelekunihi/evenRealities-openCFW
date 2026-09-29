
undefined8 bq27427_execute_control_word(undefined1 param_1)

{
  int iVar1;
  undefined4 unaff_r7;
  
  iVar1 = bq27427_i2c_write_reg(0,param_1,0);
  if (iVar1 == 0) {
    FUN_004910f4(100);
    iVar1 = 0;
  }
  return CONCAT44(unaff_r7,iVar1);
}

