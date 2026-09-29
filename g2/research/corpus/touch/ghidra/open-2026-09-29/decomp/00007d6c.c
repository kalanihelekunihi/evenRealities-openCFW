
int capsense_widget_data_pointer(uint param_1,int param_2)

{
  int iVar1;
  int *piVar2;
  
  if (param_1 < 3) {
    piVar2 = (int *)(*(int *)(param_2 + 0xc) + param_1 * 0x90);
    if (*(byte *)((int)piVar2 + 0x7b) - 2 < 4) {
      iVar1 = *piVar2 + 0x24;
    }
    else {
      iVar1 = 0;
    }
  }
  else {
    iVar1 = 0;
  }
  return iVar1;
}

