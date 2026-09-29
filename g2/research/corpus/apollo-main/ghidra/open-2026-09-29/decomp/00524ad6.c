
bool ft_corner_is_flat(int param_1,int param_2,int param_3,int param_4)

{
  int iVar1;
  int iVar2;
  
  iVar1 = param_3 + param_1;
  iVar2 = param_4 + param_2;
  if (param_1 < 0) {
    param_1 = -param_1;
  }
  if (param_2 < 0) {
    param_2 = -param_2;
  }
  if (param_2 < param_1) {
    param_1 = param_1 + (param_2 * 3 >> 3);
  }
  else {
    param_1 = param_2 + (param_1 * 3 >> 3);
  }
  if (param_3 < 0) {
    param_3 = -param_3;
  }
  if (param_4 < 0) {
    param_4 = -param_4;
  }
  if (param_4 < param_3) {
    param_3 = param_3 + (param_4 * 3 >> 3);
  }
  else {
    param_3 = param_4 + (param_3 * 3 >> 3);
  }
  if (iVar1 < 0) {
    iVar1 = -iVar1;
  }
  if (iVar2 < 0) {
    iVar2 = -iVar2;
  }
  if (iVar2 < iVar1) {
    iVar1 = iVar1 + (iVar2 * 3 >> 3);
  }
  else {
    iVar1 = iVar2 + (iVar1 * 3 >> 3);
  }
  return (param_3 + param_1) - iVar1 < iVar1 >> 4;
}

