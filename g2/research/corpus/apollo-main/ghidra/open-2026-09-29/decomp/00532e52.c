
void FUN_00532e52(void)

{
  int iVar1;
  byte bVar2;
  
  for (bVar2 = 0; iVar1 = DAT_0053345c, bVar2 < 3; bVar2 = bVar2 + 1) {
    *(undefined1 *)((uint)bVar2 * 0x10 + DAT_0053345c + 0xb) = 0;
    *(undefined4 *)(iVar1 + (uint)bVar2 * 0x10) = 0;
  }
  return;
}

