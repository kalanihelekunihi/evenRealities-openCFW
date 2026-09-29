
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8
hw_config_retry_43048e(byte param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  
  puVar1 = _DAT_00430644;
  iVar4 = DAT_00430640;
  iVar3 = 0;
  if (param_1 == 4) {
    FUN_0041d92c(**(undefined4 **)(DAT_00430640 + 0x48),*_DAT_00430644);
    FUN_0041d92c(*(undefined4 *)(*(int *)(iVar4 + 0x48) + 4),*puVar1);
  }
  iVar4 = 0;
  while ((iVar4 < 1000 &&
         (iVar3 = hw_config_transaction_42c988
                            (*(undefined4 *)(DAT_00430640 + (uint)param_1 * 0x10 + 4),2,1),
         iVar3 != 0))) {
    FUN_0041f9d8(10);
    iVar4 = iVar4 + 1;
  }
  if (iVar3 == 0) {
    uVar2 = 0;
  }
  else {
    uVar2 = 4;
  }
  return CONCAT44(param_4,uVar2);
}

