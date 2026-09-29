
void dual_side_indicator_update(void)

{
  int iVar1;
  char *pcVar2;
  undefined4 uVar3;
  
  case_update_cached_byte(5,3);
  case_update_cached_byte(6,0x81);
  case_update_cached_byte(7,0x20);
  pcVar2 = DAT_08009a98;
  iVar1 = DAT_08009a94;
  if ((((*(char *)(DAT_08009a94 + 0x10) == '\0') || (*(char *)(DAT_08009a94 + 0x15) == '\0')) ||
      (*(char *)(DAT_08009a94 + 0x31) != '\0')) ||
     ((*DAT_08009a98 != '\0' && (*(char *)(DAT_08009a94 + 0x11) == '\0')))) {
    uVar3 = 0xae;
  }
  else {
    uVar3 = 0xaf;
  }
  case_update_cached_byte(3,uVar3);
  if (((*(char *)(iVar1 + 0x11) == '\0') || (*(char *)(iVar1 + 0x15) == '\0')) ||
     ((*(char *)(DAT_08009a94 + 0x4d) != '\0' ||
      ((*pcVar2 != '\0' && (*(char *)(iVar1 + 0x10) == '\0')))))) {
    uVar3 = 0xae;
  }
  else {
    uVar3 = 0xaf;
  }
  case_update_cached_byte(4,uVar3);
  return;
}

