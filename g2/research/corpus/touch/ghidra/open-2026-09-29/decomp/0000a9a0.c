
void __aeabi_idivmod(undefined4 param_1,int param_2)

{
  if (param_2 != 0) {
    __aeabi_idiv();
    return;
  }
  __aeabi_idiv0(0);
  return;
}

