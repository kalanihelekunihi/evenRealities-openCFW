
char FUN_005453fe(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 *param_4,
                 undefined4 param_5)

{
  char cVar1;
  uint uVar2;
  undefined4 uVar3;
  undefined1 local_34 [4];
  undefined4 local_30;
  undefined1 auStack_2c [24];
  undefined4 *puStack_14;
  
  puStack_14 = param_4;
  cVar1 = FUN_00585a74(param_1,param_2,param_3,0,param_5);
  if (cVar1 == '\0') {
    if (param_1[7] != 0) {
      (*(code *)param_1[7])(param_1);
    }
    *(undefined1 *)(param_1 + 0xc) = 0;
    *(undefined1 *)((int)param_1 + 0x31) = 0;
    if (param_4 == (undefined4 *)0x0) {
      param_1[0xb] = 0;
      param_1[10] = 0;
    }
    else {
      uVar3 = param_4[1];
      param_1[10] = *param_4;
      param_1[0xb] = uVar3;
    }
    local_30 = 0;
    local_34[0] = 0;
    param_1[5] = 0;
    FUN_00544736(param_1,auStack_2c,0,&local_30,local_34,DAT_0054557c,0);
    param_1[5] = local_30;
    if ((uint)param_1[4] / (uint)param_1[3] < 2) {
      FUN_004733ee(DAT_00545534);
      uVar3 = FUN_00585c94(param_1);
      FUN_004733ee(DAT_00545538,*param_1,uVar3);
      FUN_004733ee(DAT_00545570,DAT_00545584,DAT_00545580);
      do {
                    /* WARNING: Do nothing block with infinite loop */
      } while( true );
    }
    for (uVar2 = 0; uVar2 < 0x40; uVar2 = uVar2 + 1) {
      *(undefined1 *)(param_1 + uVar2 * 6 + 0xaa) = 0;
      param_1[uVar2 * 6 + 0xaf] = 0xffffffff;
      param_1[uVar2 * 6 + 0xab] = 0xffffffff;
    }
    for (uVar2 = 0; uVar2 < 0x40; uVar2 = uVar2 + 1) {
      param_1[uVar2 * 2 + 0x2b] = 0xffffffff;
    }
    if (param_1[8] != 0) {
      (*(code *)param_1[8])(param_1);
    }
    cVar1 = FUN_00545264(param_1);
    if (param_1[7] != 0) {
      (*(code *)param_1[7])(param_1);
    }
    if (param_1[8] != 0) {
      (*(code *)param_1[8])(param_1);
    }
  }
  FUN_00585bc8(param_1,cVar1);
  return cVar1;
}

