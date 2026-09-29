
int gx8002_aout_get_db(int param_1,undefined2 *param_2)

{
  int iVar1;
  int iVar2;
  
  iVar1 = 0;
  iVar2 = 0x25;
  do {
    if ((int)*(short *)(iRam10205028 + iVar1 * 4) == (uRam00000014 & 0x1ffffff) >> 0x10) break;
    iVar1 = iVar1 + 1;
    iVar2 = iVar2 + -1;
  } while (iVar2 != 0);
  *param_2 = *(undefined2 *)(iVar1 * 4 + iRam10205028 + 2);
  return (int)*(short *)(param_1 + 0x12);
}

