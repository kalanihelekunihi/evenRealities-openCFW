
void case_copy_head8_to_tail8(void)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  
  iVar1 = DAT_0800d268;
  uVar2 = 0;
  iVar3 = DAT_0800d268 + 8;
  do {
    *(undefined1 *)(iVar3 + uVar2) = *(undefined1 *)(iVar1 + uVar2);
    uVar2 = uVar2 + 1 & 0xff;
  } while (uVar2 < 8);
  return;
}

