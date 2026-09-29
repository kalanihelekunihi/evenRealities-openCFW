
undefined8 FUN_004cabbc(int param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  
  FUN_004ca81a(param_1,param_3);
  iVar1 = FUN_004caafa(param_1,param_2,param_3,param_4 & 0xff);
  if ((iVar1 == 0) &&
     (iVar1 = (**(code **)(*(int *)(param_1 + 0x68) + 0x10))(*(undefined4 *)(param_1 + 0x68)),
     0 < iVar1)) {
    FUN_004d09b4(DAT_004cb59c,DAT_004cb594,0xdd);
  }
  return CONCAT44(param_4,iVar1);
}

