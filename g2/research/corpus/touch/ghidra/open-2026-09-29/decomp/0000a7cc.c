
void __aeabi_uidivmod(undefined4 param_1,int param_2)

{
  if (param_2 != 0) {
    __aeabi_uidiv();
    return;
  }
  __aeabi_idiv0(0);
  return;
}

