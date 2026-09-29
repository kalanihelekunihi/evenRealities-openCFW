
int FUN_005e505a(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  
  iVar1 = td_active_session();
  iVar5 = *(int *)(DAT_005e53b4 + 0x288);
  iVar2 = td_counter_b_get();
  if ((((iVar5 == 0) || (iVar3 = td_record_status_get(iVar5), iVar3 != 2)) ||
      (iVar3 = td_record_in_use_get(iVar5), iVar3 != 0)) &&
     (((iVar2 == 0 || (iVar5 = td_record_status_get(iVar2), iVar5 != 2)) ||
      (iVar3 = td_record_in_use_get(iVar2), iVar5 = iVar2, iVar3 != 0)))) {
    if (iVar1 != 0) {
      for (uVar4 = 0; uVar4 < *(uint *)(iVar1 + 8); uVar4 = uVar4 + 1) {
        if ((*(char *)(uVar4 * 0x90 + iVar1 + 0x122) == '\x02') &&
           (iVar5 = td_record_in_use_get(*(undefined4 *)(uVar4 * 0x90 + iVar1 + 0x9c)), iVar5 == 0))
        {
          return *(int *)(iVar1 + uVar4 * 0x90 + 0x9c);
        }
      }
    }
    iVar5 = 0;
  }
  return iVar5;
}

