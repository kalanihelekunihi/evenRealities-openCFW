
void FUN_000060ea(undefined4 param_1,undefined4 param_2,undefined4 param_3,int *param_4)

{
  int *piVar1;
  uint uVar2;
  
  piVar1 = (int *)param_4[6];
  for (uVar2 = 0; uVar2 < *(byte *)(*param_4 + 0x2c); uVar2 = uVar2 + 1) {
    FUN_00005fc6(*piVar1,(char)piVar1[1],param_1,param_2,param_3);
    if (7 < *(byte *)(piVar1 + 1)) {
      software_bkpt(1);
    }
    *(int *)(*piVar1 + 0x44) = 1 << (uint)*(byte *)(piVar1 + 1);
    piVar1 = piVar1 + 2;
  }
  return;
}

