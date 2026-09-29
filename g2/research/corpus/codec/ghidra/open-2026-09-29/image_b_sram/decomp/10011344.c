
void FUN_10011344(undefined4 *param_1,undefined4 *param_2,int param_3)

{
  undefined1 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  
  if ((((uint)param_2 | (uint)param_1) & 3) == 0) {
    for (; 0xf < param_3; param_3 = param_3 + -0x10) {
      uVar2 = param_2[1];
      uVar3 = param_2[2];
      *param_1 = *param_2;
      uVar4 = param_2[3];
      param_1[1] = uVar2;
      param_1[2] = uVar3;
      param_1[3] = uVar4;
      param_2 = param_2 + 4;
      param_1 = param_1 + 4;
    }
    for (; 3 < param_3; param_3 = param_3 + -4) {
      uVar2 = *param_2;
      param_2 = param_2 + 1;
      *param_1 = uVar2;
      param_1 = param_1 + 1;
    }
    for (; param_3 != 0; param_3 = param_3 + -1) {
      uVar1 = *(undefined1 *)param_2;
      param_2 = (undefined4 *)((int)param_2 + 1);
      *(undefined1 *)param_1 = uVar1;
      param_1 = (undefined4 *)((int)param_1 + 1);
    }
  }
  else {
    for (; param_3 != 0; param_3 = param_3 + -1) {
      uVar1 = *(undefined1 *)param_2;
      param_2 = (undefined4 *)((int)param_2 + 1);
      *(undefined1 *)param_1 = uVar1;
      param_1 = (undefined4 *)((int)param_1 + 1);
    }
  }
  return;
}

