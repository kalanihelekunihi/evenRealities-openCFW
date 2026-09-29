
undefined8 hal_i2c_irq_handler(undefined4 param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int local_10;
  undefined4 uStack_c;
  
  iVar1 = DAT_00504760;
  local_10 = param_3;
  uStack_c = param_4;
  iVar2 = FUN_0055c4d0(*(undefined4 *)(DAT_00504760 + 0x44),1,&local_10);
  if ((iVar2 == 0) && (local_10 != 0)) {
    FUN_0055c518(*(undefined4 *)(iVar1 + 0x44),local_10);
    FUN_0055c558(*(undefined4 *)(iVar1 + 0x44),local_10);
  }
  return CONCAT44(uStack_c,local_10);
}

