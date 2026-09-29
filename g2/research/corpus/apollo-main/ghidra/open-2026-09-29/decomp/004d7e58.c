
int * skip_utf8_bom(int *param_1)

{
  int iVar1;
  
  if (((param_1 == (int *)0x0) || (*param_1 == 0)) || (param_1[2] != 0)) {
    param_1 = (int *)0x0;
  }
  else if (((param_1 != (int *)0x0) && (param_1[2] + 4U < (uint)param_1[1])) &&
          (iVar1 = FUN_0044b610(*param_1 + param_1[2],&DAT_004d7f90,3), iVar1 == 0)) {
    param_1[2] = param_1[2] + 3;
  }
  return param_1;
}

