
void Ins_AND(uint *param_1)

{
  byte bVar1;
  
  if ((*param_1 == 0) || (param_1[1] == 0)) {
    bVar1 = 0;
  }
  else {
    bVar1 = 1;
  }
  *param_1 = (uint)bVar1;
  return;
}

