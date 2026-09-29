
void case_dispatch_pending(uint param_1)

{
  int iVar1;
  
  iVar1 = DAT_08004d28;
  if ((*(uint *)(DAT_08004d28 + 0xc) & param_1) != 0) {
    *(uint *)(DAT_08004d28 + 0xc) = param_1;
    case_hook_08004d2c(param_1);
  }
  if ((*(uint *)(iVar1 + 0x10) & param_1) != 0) {
    *(uint *)(iVar1 + 0x10) = param_1;
    case_hook_08004d00(param_1);
  }
  return;
}

