
undefined4 FUN_0041c9ca(uint param_1)

{
  undefined4 uVar1;
  undefined1 local_4;
  
  local_4 = (char)param_1;
  if (((*DAT_0041cbf8 << 0xe < 0) || (*DAT_0041cbf8 << 0xf < 0)) && (local_4 == '\x03')) {
    uVar1 = 1;
  }
  else {
    *DAT_0041cbfc = (param_1 & 0xff) << 8 | (param_1 >> 8 & 0xff) << 4 | param_1 >> 0x10 & 0xff;
    uVar1 = 0;
  }
  return uVar1;
}

