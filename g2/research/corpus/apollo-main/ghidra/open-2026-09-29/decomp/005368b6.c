
void FUN_005368b6(int param_1)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  
  iVar2 = DAT_00536a14;
  bVar1 = false;
  if (*(char *)(DAT_00536a14 + 0x18) == '\x02') {
    if (*(char *)(DAT_00536a14 + 0x1d) != '\0') {
      if (*(char *)(param_1 + 10) == '\x04') {
        if (*(char *)(DAT_00536a14 + 0x1c) != '\0') {
          bVar1 = true;
          *(undefined1 *)(DAT_00536a14 + 0x1c) = 0;
        }
      }
      else {
        iVar3 = DmFindAdType(1,*(undefined1 *)(param_1 + 8),*(undefined4 *)(param_1 + 4));
        if (iVar3 == 0) {
          bVar1 = true;
          *(undefined1 *)(iVar2 + 0x1c) = 1;
        }
        else if ((*(byte *)(iVar3 + 2) & *(byte *)(iVar2 + 0x1d)) == 0) {
          bVar1 = true;
          *(undefined1 *)(iVar2 + 0x1c) = 1;
        }
      }
    }
    if (!bVar1) {
      *(undefined1 *)(param_1 + 2) = 0x26;
      (**(code **)(DAT_00536a18 + 8))(param_1);
    }
  }
  return;
}

