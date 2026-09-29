
void td_record_flags_clear_all(void)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  iVar1 = DAT_00597c08;
  uVar3 = *(uint *)(DAT_00597c08 + 0x9568);
  if (10 < uVar3) {
    uVar3 = 10;
  }
  for (uVar2 = 0; uVar2 < uVar3; uVar2 = uVar2 + 1) {
    *(undefined4 *)(uVar2 * 0x90 + iVar1 + 0x9684) = 0;
  }
  *(undefined4 *)(iVar1 + 0x95f4) = 0;
  return;
}

