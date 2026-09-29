
void case_write_selected_mask_alt(undefined4 param_1)

{
  undefined4 uVar1;
  
  if (*DAT_0800a590 == '\0') {
    uVar1 = 0x10;
  }
  else {
    uVar1 = 8;
  }
  case_register_write_channel(DAT_0800a594,uVar1,param_1);
  return;
}

