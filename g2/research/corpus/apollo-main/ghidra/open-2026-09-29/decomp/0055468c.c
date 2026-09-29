
void FUN_0055468c(void)

{
  int iVar1;
  int iVar2;
  
  iVar2 = FUN_0045a568();
  iVar1 = DAT_00554d28;
  if (iVar2 == 1) {
    if (*(int *)(DAT_00554d28 + 0x24) != 0) {
      iVar2 = service_time_rtc_refresh();
      iVar2 = iVar2 - *(int *)(iVar1 + 0x24);
      if (iVar2 != *DAT_005551d4) {
        *DAT_005551d4 = iVar2;
        FUN_00589b68(0x12,iVar2);
      }
    }
  }
  return;
}

