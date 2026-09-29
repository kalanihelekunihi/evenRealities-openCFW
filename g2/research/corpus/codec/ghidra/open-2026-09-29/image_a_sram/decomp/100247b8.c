
undefined4
gx_spi_flash_readdata(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  
  if (*(uint *)(param_1 + 4) == 0) {
    uVar1 = 0xffffffff;
  }
  else {
    uVar1 = (*(code *)(*(uint *)(param_1 + 4) & 0xfffffffe))(param_2,param_3,param_4);
  }
  return uVar1;
}

