
int FUN_00567230(int param_1,undefined4 param_2)

{
  int *piVar1;
  int iVar2;
  undefined4 *puVar3;
  undefined4 uVar4;
  int iVar5;
  bool bVar6;
  float fVar7;
  float fVar8;
  undefined1 auStack_9c [136];
  
  piVar1 = DAT_0056759c;
  iVar5 = *DAT_0056759c;
  *(undefined4 *)(iVar5 + 0x34) = DAT_005675a0;
  *(undefined4 *)(iVar5 + 0x30) = DAT_005675a4;
  bVar6 = *(int *)(iVar5 + 0x10) != 0;
  iVar2 = 0;
  if (bVar6) {
    iVar2 = *(int *)(iVar5 + 0x1c);
  }
  if (bVar6 && iVar2 != 0) {
    fVar7 = *(float *)(iVar5 + 0x2d8) * 0.5;
    fVar8 = fVar7 + DAT_00567594;
    fVar7 = DAT_00567598 - fVar7;
    *(undefined4 *)(iVar5 + 0x2c) = 0;
    *(float *)(iVar5 + 0x30) = fVar8;
    *(float *)(iVar5 + 0x34) = fVar7;
    *(byte *)(iVar5 + 0x21) =
         ((byte)*(undefined4 *)(param_1 + 0x84) | (byte)*(undefined4 *)(iVar5 + 0x90)) & 1;
    iVar2 = *piVar1;
    if (*(char *)(iVar2 + 0x21) != '\0') {
      if ((int)((uint)*(byte *)(iVar2 + 0x90) << 0x1f) < 0) {
        FUN_00561830(iVar2 + 0x38,iVar2 + 0xa4);
        if ((int)((uint)*(byte *)(param_1 + 0x84) << 0x1f) < 0) {
          FUN_005619f2(*piVar1 + 0x38,param_1 + 0x60);
        }
      }
      else if ((int)((uint)*(byte *)(param_1 + 0x84) << 0x1f) < 0) {
        FUN_00561830(iVar2 + 0x38,param_1 + 0x60);
      }
      else {
        FUN_00561810(iVar2 + 0x38);
      }
    }
    iVar2 = *piVar1;
    *(undefined4 *)(iVar2 + 8) = 0;
    *(undefined4 *)(iVar2 + 0xc) = 0;
    *(undefined4 *)(iVar2 + 0x14) = 0;
    *(undefined4 *)(iVar2 + 0x18) = 0;
    *(undefined1 *)(iVar2 + 0x20) = 0;
    *(undefined4 *)(*piVar1 + 0x24) = 0;
    iVar2 = FUN_005657d8(param_1);
    if (iVar2 == 0) {
      puVar3 = (undefined4 *)*piVar1;
      *puVar3 = puVar3[3];
      puVar3[1] = puVar3[2];
      if (puVar3[10] != 2) {
        FUN_00439c04(auStack_9c,param_1,0x88);
        FUN_00514f3c(auStack_9c,*puVar3,puVar3[7],puVar3[1],puVar3[4]);
        *(undefined1 *)(*piVar1 + 0x7e) = 1;
        iVar2 = FUN_005202ec(auStack_9c,param_2);
        *(undefined1 *)(*piVar1 + 0x7e) = 0;
        return iVar2;
      }
      goto LAB_00567316;
    }
  }
  else {
    fVar7 = *(float *)(iVar5 + 0x2d8) * 0.5;
    fVar8 = fVar7 + DAT_00567594;
    fVar7 = DAT_00567598 - fVar7;
    *(undefined4 *)(iVar5 + 0x2c) = 1;
    *(float *)(iVar5 + 0x30) = fVar8;
    *(float *)(iVar5 + 0x34) = fVar7;
    *(byte *)(iVar5 + 0x21) =
         ((byte)*(undefined4 *)(param_1 + 0x84) | (byte)*(undefined4 *)(iVar5 + 0x90)) & 1;
    iVar2 = *piVar1;
    if (*(char *)(iVar2 + 0x21) != '\0') {
      if ((int)((uint)*(byte *)(iVar2 + 0x90) << 0x1f) < 0) {
        FUN_00561830(iVar2 + 0x38,iVar2 + 0xa4);
        if ((int)((uint)*(byte *)(param_1 + 0x84) << 0x1f) < 0) {
          FUN_005619f2(*piVar1 + 0x38,param_1 + 0x60);
        }
      }
      else if ((int)((uint)*(byte *)(param_1 + 0x84) << 0x1f) < 0) {
        FUN_00561830(iVar2 + 0x38,param_1 + 0x60);
      }
      else {
        FUN_00561810(iVar2 + 0x38);
      }
    }
    puVar3 = (undefined4 *)*piVar1;
    *puVar3 = 0;
    puVar3[7] = 0;
    puVar3[1] = 0;
    puVar3[4] = 0;
    puVar3[2] = 0;
    puVar3[3] = 0;
    puVar3[5] = 0;
    puVar3[6] = 0;
    *(undefined1 *)(puVar3 + 8) = 0;
    *(undefined4 *)(*piVar1 + 0x24) = 0;
    iVar2 = FUN_005657d8(param_1);
    if (iVar2 == 0) {
      puVar3 = (undefined4 *)*piVar1;
      *puVar3 = puVar3[3];
      puVar3[1] = puVar3[2];
      goto LAB_00567316;
    }
  }
  FUN_0051778c(0);
  FUN_00517796(0);
  FUN_0051565c(iVar2);
LAB_00567316:
  if ((int)((uint)*(byte *)((undefined4 *)*piVar1 + 0x24) << 0x1b) < 0) {
    uVar4 = FUN_0051416c(*(undefined4 *)*piVar1);
    iVar2 = *piVar1;
    *(undefined4 *)(iVar2 + 0x1c) = uVar4;
    uVar4 = FUN_0051416c(*(int *)(iVar2 + 4) << 2);
    iVar2 = *piVar1;
    *(undefined4 *)(iVar2 + 0x10) = uVar4;
    if (*(int *)(iVar2 + 0x1c) != 0) {
      if (*(int *)(iVar2 + 0x10) != 0) {
        fVar7 = *(float *)(iVar2 + 0x2d8) * 0.5;
        fVar8 = fVar7 + DAT_00567594;
        fVar7 = DAT_00567598 - fVar7;
        *(undefined4 *)(iVar2 + 0x2c) = 0;
        *(float *)(iVar2 + 0x30) = fVar8;
        *(float *)(iVar2 + 0x34) = fVar7;
        *(byte *)(iVar2 + 0x21) =
             ((byte)*(undefined4 *)(param_1 + 0x84) | (byte)*(undefined4 *)(iVar2 + 0x90)) & 1;
        iVar2 = *piVar1;
        if (*(char *)(iVar2 + 0x21) != '\0') {
          if ((int)((uint)*(byte *)(iVar2 + 0x90) << 0x1f) < 0) {
            FUN_00561830(iVar2 + 0x38,iVar2 + 0xa4);
            if ((int)((uint)*(byte *)(param_1 + 0x84) << 0x1f) < 0) {
              FUN_005619f2(*piVar1 + 0x38,param_1 + 0x60);
            }
          }
          else if ((int)((uint)*(byte *)(param_1 + 0x84) << 0x1f) < 0) {
            FUN_00561830(iVar2 + 0x38,param_1 + 0x60);
          }
          else {
            FUN_00561810(iVar2 + 0x38);
          }
        }
        iVar2 = *piVar1;
        *(undefined4 *)(iVar2 + 8) = 0;
        *(undefined4 *)(iVar2 + 0xc) = 0;
        *(undefined4 *)(iVar2 + 0x14) = 0;
        *(undefined4 *)(iVar2 + 0x18) = 0;
        *(undefined1 *)(iVar2 + 0x20) = 0;
        *(undefined4 *)(*piVar1 + 0x24) = 0;
        iVar2 = FUN_005657d8(param_1);
        if (iVar2 == 0) {
          puVar3 = (undefined4 *)*piVar1;
          *puVar3 = puVar3[3];
          puVar3[1] = puVar3[2];
          FUN_00439c04(auStack_9c,param_1,0x88);
          FUN_00514f3c(auStack_9c,*puVar3,puVar3[7],puVar3[1],puVar3[4]);
          *(undefined1 *)(*piVar1 + 0x7e) = 1;
          iVar2 = FUN_005202ec(auStack_9c,param_2);
          *(undefined1 *)(*piVar1 + 0x7e) = 0;
        }
        else {
          FUN_0051778c(0);
          FUN_00517796(0);
          FUN_0051565c(iVar2);
        }
        if (*(int *)(*piVar1 + 0x1c) != 0) {
          FUN_00514178();
        }
        if (*(int *)(*piVar1 + 0x10) != 0) {
          FUN_00514178();
        }
        iVar5 = *piVar1;
        *(undefined4 *)(iVar5 + 0x1c) = 0;
        *(undefined4 *)(iVar5 + 0x10) = 0;
        return iVar2;
      }
      FUN_00514178();
    }
    if (*(int *)(*piVar1 + 0x10) != 0) {
      FUN_00514178();
    }
    iVar2 = *piVar1;
    *(undefined4 *)(iVar2 + 0x1c) = 0;
    *(undefined4 *)(iVar2 + 0x10) = 0;
  }
  return 2;
}

