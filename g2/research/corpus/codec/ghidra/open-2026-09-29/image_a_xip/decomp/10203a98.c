
void gx8002_dma_deallocate(int param_1)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  
  uVar2 = func_0x10025560();
  iVar1 = DAT_10203ad8;
  *(undefined1 *)(param_1 + DAT_10203ad8 + 0x370) = 0;
  for (iVar3 = 0; iVar3 != *(int *)(iVar1 + 4); iVar3 = iVar3 + 1) {
    if (*(char *)(DAT_10203ad8 + iVar3 + 0x370) == '\x01') goto LAB_10203aca;
  }
  func_0x10025080(0x19,0);
LAB_10203aca:
  func_0x1002556c(uVar2);
  return;
}

