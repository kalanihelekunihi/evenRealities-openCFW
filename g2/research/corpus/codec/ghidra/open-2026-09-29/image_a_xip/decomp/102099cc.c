
void gx8002_memset(undefined4 *param_1,undefined1 param_2,int param_3)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 *puVar3;
  
  if (param_3 != 0) {
    iVar2 = param_3;
    puVar3 = param_1;
    if (((uint)param_1 & 3) != 0) {
      *(undefined1 *)param_1 = param_2;
      iVar2 = param_3 + -1;
      if (iVar2 == 0) {
        return;
      }
      puVar3 = (undefined4 *)((int)param_1 + 1);
      if (((uint)puVar3 & 3) != 0) {
        *(undefined1 *)puVar3 = param_2;
        iVar2 = param_3 + -2;
        if (iVar2 == 0) {
          return;
        }
        puVar3 = (undefined4 *)((int)param_1 + 2);
        if (((uint)puVar3 & 3) != 0) {
          *(undefined1 *)puVar3 = param_2;
          iVar2 = param_3 + -3;
          puVar3 = (undefined4 *)((int)param_1 + 3);
        }
      }
    }
    uVar1 = CONCAT22(CONCAT11(param_2,param_2),CONCAT11(param_2,param_2));
    for (; 0xf < iVar2; iVar2 = iVar2 + -0x10) {
      *puVar3 = uVar1;
      puVar3[1] = uVar1;
      puVar3[2] = uVar1;
      puVar3[3] = uVar1;
      puVar3 = puVar3 + 4;
    }
    for (; 3 < iVar2; iVar2 = iVar2 + -4) {
      *puVar3 = uVar1;
      puVar3 = puVar3 + 1;
    }
    if (((iVar2 != 0) && (*(undefined1 *)puVar3 = param_2, iVar2 != 1)) &&
       (*(undefined1 *)((int)puVar3 + 1) = param_2, iVar2 != 2)) {
      *(undefined1 *)((int)puVar3 + 2) = param_2;
      return;
    }
  }
  return;
}

