
undefined4 case_configure_mode_wait(uint param_1)

{
  uint *puVar1;
  int iVar2;
  
  puVar1 = DAT_08005088;
  *DAT_08005088 = *DAT_08005088 & 0xfffff9ff | param_1;
  if (param_1 == 0x200) {
    iVar2 = __aeabi_uidiv(*DAT_0800508c * 6,DAT_08005090);
    iVar2 = iVar2 + 1;
    while ((int)(puVar1[5] << 0x15) < 0) {
      if (iVar2 == 0) {
        return 3;
      }
      iVar2 = iVar2 + -1;
    }
  }
  return 0;
}

