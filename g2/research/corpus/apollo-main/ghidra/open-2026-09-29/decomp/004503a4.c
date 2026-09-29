
void FUN_004503a4(void)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = DAT_00450b30;
  FUN_00482b00(DAT_00450b30 + 0xac,0x60);
  uVar2 = FUN_00464466(0x450759,0x10,0);
  *(undefined4 *)(iVar1 + 0xa8) = uVar2;
  FUN_004509da();
  *(undefined1 *)(iVar1 + 0xa4) = 0;
  *(undefined1 *)(iVar1 + 0xa5) = 0;
  return;
}

