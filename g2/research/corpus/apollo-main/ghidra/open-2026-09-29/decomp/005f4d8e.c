
void Compute_Funcs(int param_1)

{
  int iVar1;
  
  if (*(short *)(param_1 + 0x12e) == 0x4000) {
    *(int *)(param_1 + 0x238) = (int)*(short *)(param_1 + 0x12a);
  }
  else if (*(short *)(param_1 + 0x130) == 0x4000) {
    *(int *)(param_1 + 0x238) = (int)*(short *)(param_1 + 300);
  }
  else {
    *(int *)(param_1 + 0x238) =
         (int)*(short *)(param_1 + 0x12a) * (int)*(short *)(param_1 + 0x12e) +
         (int)*(short *)(param_1 + 300) * (int)*(short *)(param_1 + 0x130) >> 0xe;
  }
  if (*(short *)(param_1 + 0x12a) == 0x4000) {
    *(undefined4 *)(param_1 + 0x240) = DAT_005f5320;
  }
  else if (*(short *)(param_1 + 300) == 0x4000) {
    *(undefined4 *)(param_1 + 0x240) = DAT_005f5324;
  }
  else {
    *(undefined4 *)(param_1 + 0x240) = DAT_005f5328;
  }
  if (*(short *)(param_1 + 0x126) == 0x4000) {
    *(undefined4 *)(param_1 + 0x244) = DAT_005f5320;
  }
  else if (*(short *)(param_1 + 0x128) == 0x4000) {
    *(undefined4 *)(param_1 + 0x244) = DAT_005f5324;
  }
  else {
    *(undefined4 *)(param_1 + 0x244) = DAT_005f532c;
  }
  *(undefined4 *)(param_1 + 0x24c) = DAT_005f5330;
  *(undefined4 *)(param_1 + 0x250) = DAT_005f5334;
  if (*(int *)(param_1 + 0x238) == 0x4000) {
    if (*(short *)(param_1 + 0x12e) == 0x4000) {
      *(undefined4 *)(param_1 + 0x24c) = DAT_005f5ae4;
      *(undefined4 *)(param_1 + 0x250) = DAT_005f5ae8;
    }
    else if (*(short *)(param_1 + 0x130) == 0x4000) {
      *(undefined4 *)(param_1 + 0x24c) = DAT_005f5afc;
      *(undefined4 *)(param_1 + 0x250) = DAT_005f5b10;
    }
  }
  if (*(int *)(param_1 + 0x238) < 0) {
    iVar1 = -*(int *)(param_1 + 0x238);
  }
  else {
    iVar1 = *(int *)(param_1 + 0x238);
  }
  if (iVar1 < 0x400) {
    *(undefined4 *)(param_1 + 0x238) = 0x4000;
  }
  *(undefined4 *)(param_1 + 0x104) = 0;
  return;
}

