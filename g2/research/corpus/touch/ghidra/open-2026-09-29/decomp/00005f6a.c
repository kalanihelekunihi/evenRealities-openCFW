
void touch_sub_2c6a(int param_1,int param_2,int param_3)

{
  uint uVar1;
  
  if (*(char *)(*(int *)(param_3 + 0xc) + param_1 * 0x90 + 0x7a) == '\x01') {
    uVar1 = (uint)*(byte *)(*(int *)(param_3 + 8) + 0x57);
  }
  else {
    uVar1 = 0;
  }
  if (param_2 == 0) {
    uVar1 = *(ushort *)(*(int *)(param_3 + 0x10) + param_1 * 0x3c + 4) * uVar1;
  }
  __aeabi_uidiv(uVar1,100);
  return;
}

