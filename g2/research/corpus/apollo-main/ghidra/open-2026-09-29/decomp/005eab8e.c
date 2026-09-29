
undefined4 FUN_005eab8e(void)

{
  int iVar1;
  undefined2 uVar2;
  int iVar3;
  undefined4 in_r3;
  
  iVar1 = DAT_005eb28c;
  FUN_00439710(DAT_005eb28c + 0x3c,DAT_005eb28c + 0x3e,0x7e);
  *(undefined2 *)(iVar1 + 0xba) = 0;
  iVar3 = td_session_record_at(0x3f);
  if (iVar3 == 0) {
    *(undefined2 *)(iVar1 + 0xba) = 0x1c;
  }
  else {
    uVar2 = FUN_005ea67a();
    *(undefined2 *)(iVar1 + 0xba) = uVar2;
  }
  FUN_005ea6da(0);
  *(undefined1 *)(iVar1 + 0x1c2) = 0;
  return in_r3;
}

