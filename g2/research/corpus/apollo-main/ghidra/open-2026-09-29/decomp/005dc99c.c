
undefined4 FUN_005dc99c(int *param_1,uint param_2)

{
  int iVar1;
  undefined1 *puVar2;
  uint uVar3;
  uint uVar4;
  
  uVar4 = param_1[8];
  while( true ) {
    if (uVar4 <= param_2) {
      return 0xffffffff;
    }
    iVar1 = param_1[4] + param_2 * 2;
    puVar2 = (undefined1 *)(iVar1 + 0xe);
    param_1[0xb] = (uint)CONCAT11(*puVar2,*(undefined1 *)(iVar1 + 0xf));
    param_1[10] = (uint)CONCAT11(puVar2[uVar4 * 2 + 2],puVar2[uVar4 * 2 + 3]);
    puVar2 = puVar2 + uVar4 * 2 + 2 + uVar4 * 2;
    param_1[0xc] = (int)CONCAT11(*puVar2,puVar2[1]);
    puVar2 = puVar2 + uVar4 * 2;
    uVar3 = (uint)CONCAT11(*puVar2,puVar2[1]);
    if ((((uVar4 - 1 <= param_2) && (param_1[10] == 0xffff)) && (param_1[0xb] == 0xffff)) &&
       ((uVar3 != 0 &&
        ((undefined1 *)(*(int *)(*param_1 + 0x200) + *(int *)(*param_1 + 0x1fc)) <
         puVar2 + uVar3 + 2)))) {
      param_1[0xc] = 1;
      uVar3 = 0;
    }
    if (uVar3 != 0xffff) break;
    param_2 = param_2 + 1;
  }
  if (uVar3 == 0) {
    puVar2 = (undefined1 *)0x0;
  }
  else {
    puVar2 = puVar2 + uVar3;
  }
  param_1[0xd] = (int)puVar2;
  param_1[9] = param_2;
  return 0;
}

