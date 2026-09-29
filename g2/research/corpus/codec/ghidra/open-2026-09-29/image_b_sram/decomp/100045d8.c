
int FUN_100045d8(int param_1,undefined1 *param_2,int param_3)

{
  undefined4 *puVar1;
  int iVar2;
  undefined1 *puVar3;
  
  iVar2 = param_1 * 0x80 + DAT_10004610;
  if (param_3 < 1) {
    param_3 = 0;
  }
  else {
    puVar3 = param_2 + param_3;
    do {
      puVar1 = *(undefined4 **)(iVar2 + 4);
      do {
      } while ((puVar1[5] & 1) == 0);
      *param_2 = (char)*puVar1;
      param_2 = param_2 + 1;
    } while (puVar3 != param_2);
  }
  return param_3;
}

