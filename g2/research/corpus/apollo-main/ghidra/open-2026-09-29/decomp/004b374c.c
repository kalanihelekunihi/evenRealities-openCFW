
void FUN_004b374c(undefined4 param_1,int param_2)

{
  int iVar1;
  byte bVar2;
  
  FUN_004b35f0(param_2);
  *(undefined1 *)(param_2 + 4) = 0;
  *(undefined1 *)(param_2 + 0xd) = 0;
  iVar1 = DAT_004b3c8c;
  *(undefined1 *)(DAT_004b3c8c + 0x74) = 0;
  if (*(char *)(param_2 + 9) != '\0') {
    *(undefined1 *)(param_2 + 9) = 0;
    *(undefined1 *)(iVar1 + 0x5d) = 0;
    for (bVar2 = 0; bVar2 < 2; bVar2 = bVar2 + 1) {
      FUN_004b33d2(bVar2,0);
    }
  }
  return;
}

