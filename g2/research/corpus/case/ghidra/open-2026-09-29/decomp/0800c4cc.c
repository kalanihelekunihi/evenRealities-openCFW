
undefined4 case_read_word_protected(undefined4 *param_1)

{
  undefined4 uVar1;
  
  ulSetInterruptMaskFromISR();
  uVar1 = *param_1;
  vClearInterruptMaskFromISR();
  return uVar1;
}

