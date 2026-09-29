
void als_function_27(void)

{
  uint uVar1;
  int iVar2;
  
  uVar1 = FUN_00513748(0);
  uVar1 = (uVar1 & 0xfff) * (1 << ((uVar1 & 0xffff) >> 0xc));
  if (*(int *)(DAT_004ae970 + 0x28) == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004ae4dc,DAT_004ae4d8,DAT_004ae978,0x1aa,DAT_004ae974);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_004ae97c,DAT_004ae97c);
    }
    uVar1 = uVar1 / 10;
  }
  else {
    uVar1 = (*(int *)(DAT_004ae970 + 0x28) * uVar1) / DAT_004ae980;
  }
  als_function_08(uVar1);
  return;
}

