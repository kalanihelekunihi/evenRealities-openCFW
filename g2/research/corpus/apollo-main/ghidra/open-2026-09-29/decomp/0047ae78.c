
int FUN_0047ae78(int param_1,byte param_2,undefined1 *param_3)

{
  int iVar1;
  
  iVar1 = 0;
  if ((param_2 & *(byte *)(param_1 + 0x2e)) != 0) {
    if (param_2 == 1) {
      *param_3 = *(undefined1 *)(param_1 + 0x4e);
      iVar1 = param_1 + 0x34;
    }
    else if (param_2 == 2) {
      *param_3 = *(undefined1 *)(param_1 + 0x6a);
      iVar1 = param_1 + 0x50;
    }
    else if (param_2 == 4) {
      iVar1 = param_1 + 7;
    }
    else if (param_2 == 8) {
      iVar1 = param_1 + 0x1e;
    }
  }
  return iVar1;
}

