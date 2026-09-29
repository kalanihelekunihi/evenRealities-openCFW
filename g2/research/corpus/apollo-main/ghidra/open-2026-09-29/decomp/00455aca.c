
undefined4 uxTaskResetEventItemValue(void)

{
  undefined4 uVar1;
  
  uVar1 = *(undefined4 *)(*DAT_0045605c + 0x18);
  *(int *)(*DAT_0045605c + 0x18) = 0x38 - *(int *)(*DAT_0045605c + 0x2c);
  return uVar1;
}

