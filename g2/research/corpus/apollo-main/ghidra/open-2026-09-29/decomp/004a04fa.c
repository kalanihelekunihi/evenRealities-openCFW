
undefined4 dmDiscCancel(int param_1)

{
  undefined4 unaff_r7;
  
  if (*(char *)(param_1 + 3) == '\0') {
    GattValueUpdate(*DAT_004a06b4);
  }
  return unaff_r7;
}

