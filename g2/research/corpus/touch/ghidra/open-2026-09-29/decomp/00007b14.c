
uint touch_sub_4814(int *param_1)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  
  if (param_1 == (int *)0x0) {
    uVar3 = 0;
  }
  else {
    uVar3 = 0;
    for (uVar2 = 0; uVar2 < *(byte *)(*param_1 + 0x24); uVar2 = uVar2 + 1) {
      if (*(char *)(param_1[3] + uVar2 * 0x90 + 0x7b) != '\a') {
        uVar1 = touch_sub_4684(uVar2,param_1);
        uVar3 = uVar3 | uVar1;
      }
    }
  }
  *(undefined1 *)(param_1[2] + 0x73) = 0;
  *(uint *)(param_1[1] + 8) = *(uint *)(param_1[1] + 8) & 0xffffffcf;
  return uVar3;
}

