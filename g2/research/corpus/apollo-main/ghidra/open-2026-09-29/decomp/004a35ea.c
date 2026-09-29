
undefined8 semantic_bus_write(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uStack_8;
  
  uStack_8 = param_1;
  iVar1 = hal_i2c_transfer_joined(4,0x69,&uStack_8,1,param_2,param_3);
  if (iVar1 == 0) {
    uVar2 = 0;
  }
  else {
    uVar2 = 0xffffffff;
  }
  return CONCAT44(param_2,uVar2);
}

