
undefined4 FT_Remove_Module(int param_1,int param_2)

{
  undefined4 uVar1;
  int *piVar2;
  int *piVar3;
  
  if (param_1 == 0) {
    uVar1 = 0x21;
  }
  else {
    if (param_2 != 0) {
      piVar2 = (int *)(param_1 + 0x14);
      piVar3 = piVar2 + *(int *)(param_1 + 0x10);
      for (; piVar2 < piVar3; piVar2 = piVar2 + 1) {
        if (*piVar2 == param_2) {
          *(int *)(param_1 + 0x10) = *(int *)(param_1 + 0x10) + -1;
          for (; piVar2 < piVar3 + -1; piVar2 = piVar2 + 1) {
            *piVar2 = piVar2[1];
          }
          piVar3[-1] = 0;
          Destroy_Module(param_2);
          return 0;
        }
      }
    }
    uVar1 = 0x22;
  }
  return uVar1;
}

