
byte capsense_widget_active_query(uint param_1,int param_2)

{
  byte bVar1;
  
  if (param_1 < 3) {
    if (*(char *)(*(int *)(param_2 + 0xc) + param_1 * 0x90 + 0x7b) == '\a') {
      bVar1 = 0;
    }
    else {
      bVar1 = *(byte *)(*(int *)(param_2 + 0x10) + param_1 * 0x3c + 0x23) & 1;
    }
  }
  else {
    bVar1 = 0;
  }
  return bVar1;
}

