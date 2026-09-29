
undefined4 bounded_percentage_convert(uint *param_1)

{
  int iVar1;
  uint uVar2;
  uint local_10;
  
  local_10 = 0;
  iVar1 = case_read_stable_u16(4,&local_10);
  if (iVar1 != 0) {
    return 0xffffffff;
  }
  uVar2 = __aeabi_uidiv(((local_10 & 0xffffff00) + (local_10 & 0xff)) * 100,0x6300);
  if (99 < uVar2) {
    uVar2 = 100;
  }
  *param_1 = uVar2;
  return 0;
}

