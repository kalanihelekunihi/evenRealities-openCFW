
void spotmgr_trim_enable_42adb8(char param_1)

{
  uint *puVar1;
  uint uVar2;
  
  if (param_1 != '\0') {
    *DAT_0042b69c = *DAT_0042b69c | 0x18000;
    *DAT_0042b6a0 = *DAT_0042b6a0 & 0xffffffc0 | *(uint *)(DAT_0042b6a4 + 0x68) >> 0xe & 0x3f;
  }
  puVar1 = DAT_0042b6a8;
  if ((*DAT_0042b6a8 & 0x3ff) + 7 < 0x400) {
    *DAT_0042b9bc = 7;
  }
  else {
    *DAT_0042b9bc = 0x3ff - (*DAT_0042b6a8 & 0x3ff);
  }
  uVar2 = *puVar1;
  *puVar1 = *DAT_0042b9bc + uVar2 & 0x3ff | uVar2 & 0xfffffc00;
  return;
}

