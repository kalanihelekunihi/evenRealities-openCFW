
void FUN_00582a48(undefined4 *param_1,undefined4 param_2,int param_3,uint param_4)

{
  undefined1 uVar1;
  int iVar2;
  uint uVar3;
  undefined1 local_38 [32];
  
  if (param_1 != (undefined4 *)0x0) {
    if (10 < param_4) {
      param_4 = 10;
    }
    *param_1 = param_2;
    param_1[1] = param_3;
    *(short *)(param_1 + 2) = (short)param_4;
    for (uVar3 = 0; uVar3 < param_4; uVar3 = uVar3 + 1) {
      param_1[uVar3 * 0x22 + 3] = uVar3 + 1;
      if (uVar3 + 1 == param_3) {
        uVar1 = 1;
      }
      else {
        uVar1 = 3;
      }
      *(undefined1 *)((int)param_1 + uVar3 * 0x88 + 0x92) = uVar1;
      iVar2 = FUN_0044b728(local_38,0x20,DAT_005836b4);
      if (iVar2 < 0) {
        local_38[0] = 0;
      }
      FUN_00582a1a(param_1 + uVar3 * 0x22 + 4,0x80,local_38);
    }
  }
  return;
}

