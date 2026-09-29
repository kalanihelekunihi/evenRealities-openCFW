
void case_write_selected_mask(undefined4 param_1)

{
  undefined4 uVar1;
  
  if (*DAT_0800a56c == '\0') {
    uVar1 = 8;
  }
  else {
    uVar1 = 0x10;
  }
  case_register_write_channel(DAT_0800a570,uVar1,param_1);
  return;
}

