
void spotmgr_profile_trim_42ae24(char param_1)

{
  int iVar1;
  
  iVar1 = DAT_0042b6a4;
  *DAT_0042b6a0 = *DAT_0042b6a0 & 0xffffffc0 | *(uint *)(DAT_0042b6a4 + 0x68) >> 2 & 0x3f;
  *DAT_0042b69c = *DAT_0042b69c & 0xfffe7fff | (*(uint *)(iVar1 + 0x68) & 3) << 0xf;
  if (param_1 != '\0') {
    *DAT_0042b6a8 = *DAT_0042b6a8 - *DAT_0042b9bc & 0x3ff | *DAT_0042b6a8 & 0xfffffc00;
  }
  return;
}

