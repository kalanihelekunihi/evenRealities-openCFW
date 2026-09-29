
void FUN_004f82f8(void)

{
  int *piVar1;
  int iVar2;
  
  piVar1 = DAT_004f8fbc;
  if (((*DAT_004f8fbc != 0) && (iVar2 = FUN_0043e2ea(*(undefined4 *)*DAT_004f8fbc), iVar2 != 0)) &&
     (*(char *)(*piVar1 + 0x18) == '\x01')) {
    FUN_00463f34(*piVar1);
  }
  return;
}

