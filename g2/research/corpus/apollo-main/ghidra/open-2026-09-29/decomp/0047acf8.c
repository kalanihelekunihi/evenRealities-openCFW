
undefined8 FUN_0047acf8(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  char cVar3;
  undefined4 local_18;
  undefined4 local_14;
  
  iVar2 = DAT_0047ae64;
  iVar1 = FUN_0043d0ce();
  local_18 = param_3;
  local_14 = param_4;
  if (iVar1 << 0x1e < 0) {
    local_14 = DAT_0047b6e0;
    local_18 = 0x45a;
    FUN_0043d574(4,DAT_0047ae28,DAT_0047adcc,DAT_0047b6e4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_0047b6e8,DAT_0047b6e8);
  }
  for (cVar3 = '\n'; cVar3 != '\0'; cVar3 = cVar3 + -1) {
    *(undefined1 *)(iVar2 + 0x2f) = 0;
    *(undefined1 *)(iVar2 + 0x30) = 0;
    FUN_0043c0e4(iVar2,6,0);
    iVar2 = iVar2 + 200;
  }
  FUN_004787a4();
  return CONCAT44(local_14,local_18);
}

