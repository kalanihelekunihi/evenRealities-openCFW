
bool FUN_00585a32(int param_1)

{
  int iVar1;
  bool bVar2;
  
  if (*(char *)(param_1 + 0x19) == '\0') {
    iVar1 = FUN_00597db0(*(undefined4 *)(param_1 + 8));
    bVar2 = iVar1 < 0;
  }
  else {
    bVar2 = true;
  }
  return bVar2;
}

