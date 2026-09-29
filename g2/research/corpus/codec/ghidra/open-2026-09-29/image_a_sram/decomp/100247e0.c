
undefined4 gx_spi_flash_getinfo(int param_1,undefined4 param_2)

{
  undefined4 uVar1;
  
  if (*(uint *)(param_1 + 0x34) == 0) {
    uVar1 = 0xffffffff;
  }
  else {
    uVar1 = (*(code *)(*(uint *)(param_1 + 0x34) & 0xfffffffe))(param_2);
  }
  return uVar1;
}

