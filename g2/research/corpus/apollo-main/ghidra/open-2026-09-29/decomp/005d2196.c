
uint FUN_005d2196(int param_1,uint param_2)

{
  short sVar1;
  uint uVar2;
  
  if ((*(int *)(param_1 + 0x4a4) != 0) && (param_2 < 0x100)) {
    sVar1 = (*(code *)**(undefined4 **)(param_1 + 0xc10))(param_2);
    for (uVar2 = 0; uVar2 < *(uint *)(param_1 + 0x14); uVar2 = uVar2 + 1) {
      if (*(short *)(*(int *)(param_1 + 0x4a4) + uVar2 * 2) == sVar1) {
        return uVar2;
      }
    }
  }
  return 0xffffffff;
}

