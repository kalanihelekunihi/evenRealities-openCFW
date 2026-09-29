
undefined4 validated_word_transfer_430ac4(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = address_validate_430a60(param_1,param_3);
  if (iVar1 == 0) {
    uVar2 = 0xffffffff;
  }
  else {
    word_transfer_critical_430b10(param_1,param_2,param_3);
    uVar2 = 0;
  }
  return uVar2;
}

