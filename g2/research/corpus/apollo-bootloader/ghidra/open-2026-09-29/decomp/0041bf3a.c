
void FUN_0041bf3a(void)

{
  undefined4 uVar1;
  int iVar2;
  
  uVar1 = DAT_0041c988;
  iVar2 = delay_status_change(100,DAT_0041c988,0x100,0x100);
  if ((iVar2 != 0) && (iVar2 = delay_status_change(100,DAT_0041c98c,1,1), iVar2 == 0)) {
    *DAT_0041caf8 = *DAT_0041caf8 | 1;
    delay_status_change(100,uVar1,0x100,0x100);
  }
  return;
}

