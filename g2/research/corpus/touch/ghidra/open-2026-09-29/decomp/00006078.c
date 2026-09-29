
void FUN_00006078(undefined4 param_1,undefined4 param_2,int param_3,undefined4 param_4,int *param_5)

{
  int *piVar1;
  uint uVar2;
  
  piVar1 = (int *)param_5[5];
  for (uVar2 = 0; uVar2 < *(ushort *)(*param_5 + 0xc); uVar2 = uVar2 + 1) {
    FUN_00005fc6(*piVar1,(char)piVar1[1],param_1,param_2,param_4);
    if (param_3 == 0) {
      if (7 < *(byte *)(piVar1 + 1)) {
        software_bkpt(1);
      }
      *(int *)(*piVar1 + 0x44) = 1 << (uint)*(byte *)(piVar1 + 1);
    }
    else {
      if (7 < *(byte *)(piVar1 + 1)) {
        software_bkpt(1);
      }
      *(int *)(*piVar1 + 0x40) = 1 << (uint)*(byte *)(piVar1 + 1);
    }
    piVar1 = piVar1 + 2;
  }
  return;
}

