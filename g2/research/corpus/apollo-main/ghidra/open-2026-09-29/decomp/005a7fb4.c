
int af_direction_compute(int param_1,int param_2)

{
  char cVar1;
  int iVar2;
  
  iVar2 = param_1;
  if (param_2 < param_1) {
    if (param_2 + param_1 < 0 == SCARRY4(param_2,param_1)) {
      cVar1 = '\x01';
      iVar2 = param_2;
      param_2 = param_1;
    }
    else {
      cVar1 = -2;
      param_2 = -param_2;
    }
  }
  else if (param_2 + param_1 < 0 == SCARRY4(param_2,param_1)) {
    cVar1 = '\x02';
  }
  else {
    cVar1 = -1;
    iVar2 = param_2;
    param_2 = -param_1;
  }
  if (iVar2 < 0) {
    iVar2 = -iVar2;
  }
  if (param_2 <= iVar2 * 0xe) {
    cVar1 = '\x04';
  }
  return (int)cVar1;
}

