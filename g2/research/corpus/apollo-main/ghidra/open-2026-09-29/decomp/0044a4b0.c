
undefined4 compress_log_manager_reconcile(void)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  undefined4 in_r3;
  char cVar4;
  uint uVar5;
  byte bVar6;
  uint uVar7;
  
  iVar2 = DAT_0044a9bc;
  if (*(char *)(DAT_0044a9bc + 6) != '\0') {
    iVar3 = compress_log_file_exists(*(undefined1 *)(DAT_0044a9bc + 4));
    if (iVar3 == 0) {
      *(undefined4 *)(iVar2 + 8) = 0;
    }
    cVar4 = '\0';
    bVar1 = false;
    uVar5 = (uint)*(byte *)(iVar2 + 5);
    for (bVar6 = 0; bVar6 < *(byte *)(iVar2 + 6); bVar6 = bVar6 + 1) {
      uVar7 = ((uint)*(byte *)(iVar2 + 5) + (uint)bVar6) % 5;
      iVar3 = compress_log_file_exists(uVar7);
      if (iVar3 != 0) {
        if (!bVar1) {
          bVar1 = true;
          uVar5 = uVar7;
        }
        cVar4 = cVar4 + '\x01';
      }
    }
    if ((cVar4 == *(char *)(iVar2 + 6)) && (uVar5 == *(byte *)(iVar2 + 5))) {
      return in_r3;
    }
    *(char *)(iVar2 + 5) = (char)uVar5;
    *(char *)(iVar2 + 6) = cVar4;
    compress_log_manager_save();
  }
  return in_r3;
}

