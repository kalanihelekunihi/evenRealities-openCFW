
void __libc_init_array(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar1 = DAT_0000aa20;
  iVar2 = DAT_0000aa1c - DAT_0000aa20;
  for (iVar3 = 0; iVar3 != iVar2 >> 2; iVar3 = iVar3 + 1) {
    (**(code **)(iVar1 + iVar3 * 4))();
  }
  runtime_init_stub();
  iVar1 = DAT_0000aa28;
  iVar2 = DAT_0000aa24 - DAT_0000aa28;
  for (iVar3 = 0; iVar3 != iVar2 >> 2; iVar3 = iVar3 + 1) {
    (**(code **)(iVar1 + iVar3 * 4))();
  }
  return;
}

