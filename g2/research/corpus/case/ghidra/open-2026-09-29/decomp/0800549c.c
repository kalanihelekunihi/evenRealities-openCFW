
int case_derive_clock(void)

{
  uint *puVar1;
  int iVar2;
  int iVar3;
  
  puVar1 = DAT_08005520;
  if ((DAT_08005520[2] & 0x3f) >> 3 == 0) {
    iVar3 = 1 << ((*DAT_08005520 & 0x3fff) >> 0xb);
    iVar2 = DAT_08005524;
LAB_0800550c:
    iVar2 = __aeabi_uidiv(iVar2,iVar3);
    return iVar2;
  }
  iVar2 = DAT_08005524 >> 1;
  if ((DAT_08005520[2] & 0x3f) >> 3 != 1) {
    if ((DAT_08005520[2] & 0x3f) >> 3 == 2) {
      if ((DAT_08005520[3] & 3) != 3) {
        iVar2 = DAT_08005524;
      }
      iVar2 = __aeabi_uidiv(iVar2,((DAT_08005520[3] & 0x7f) >> 4) + 1);
      iVar3 = (puVar1[3] >> 0x1d) + 1;
      iVar2 = ((puVar1[3] & 0x7fff) >> 8) * iVar2;
      goto LAB_0800550c;
    }
    if ((DAT_08005520[2] & 0x3f) >> 3 == 4) {
      return 0x8000;
    }
    if ((DAT_08005520[2] & 0x3f) >> 3 == 3) {
      return 32000;
    }
    iVar2 = 0;
  }
  return iVar2;
}

