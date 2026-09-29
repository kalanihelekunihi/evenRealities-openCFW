
void semantic_OtaEraseRange(int param_1,uint param_2)

{
  int *piVar1;
  
  while( true ) {
    piVar1 = DAT_0044542c;
    if (param_2 == 0) {
      return;
    }
    (**(code **)(*DAT_0044542c + 0x20))(param_1);
    if (param_2 <= *(uint *)(*piVar1 + 4)) break;
    param_2 = param_2 - *(int *)(*piVar1 + 4);
    param_1 = *(int *)(*piVar1 + 4) + param_1;
  }
  return;
}

