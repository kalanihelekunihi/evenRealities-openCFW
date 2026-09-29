
uint FUN_005a40ca(void)

{
  bool bVar1;
  uint uVar2;
  
  uVar2 = FUN_00473940();
  if (*DAT_005a48f4 == '\x02') {
    FUN_005a23f8();
  }
  else if (*DAT_005a48f4 == '\a') {
    FUN_005a2b14();
  }
  FUN_004802ce();
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((uVar2 & 1) == 1);
  }
  return uVar2;
}

