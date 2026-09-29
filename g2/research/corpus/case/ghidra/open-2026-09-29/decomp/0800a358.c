
void case_validate_magic_state(void)

{
  int iVar1;
  undefined2 uVar2;
  
  iVar1 = DAT_0800a378;
  if ((*(ushort *)(DAT_0800a378 + 2) < 2) || (*(char *)(DAT_0800a378 + 1) != 'Z')) {
    uVar2 = 0;
  }
  else {
    *DAT_0800a37c = 0x5a;
    uVar2 = 1;
  }
  *(undefined2 *)(iVar1 + 2) = uVar2;
  return;
}

