
undefined8 FUN_0055e388(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 *puVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  undefined4 local_20;
  
  uVar10 = 0;
  local_20 = param_3;
  for (uVar9 = 0; puVar1 = DAT_0055e98c, uVar9 < 4; uVar9 = uVar9 + 1) {
    if ((DAT_0055e98c[uVar9 * 7 + 2] != 0) && (DAT_0055e98c[uVar9 * 7 + 3] != 0)) {
      uVar7 = FUN_0058dae4(DAT_0055e98c[uVar9 * 7],DAT_0055e98c + uVar9 * 7 + 1);
      if (uVar9 == 2) {
        uVar8 = FUN_00480f0c(*(undefined4 *)puVar1[0x10],*DAT_0055e990);
      }
      else {
        uVar8 = FUN_00480f0c(*(undefined4 *)puVar1[uVar9 * 7 + 2],
                             *(undefined4 *)(puVar1[uVar9 * 7 + 2] + 8));
      }
      uVar2 = FUN_00480f0c(*(undefined4 *)(puVar1[uVar9 * 7 + 2] + 4),
                           *(undefined4 *)(puVar1[uVar9 * 7 + 2] + 0xc));
      uVar3 = FUN_0058dbb8(puVar1[uVar9 * 7 + 1],0,0);
      uVar4 = FUN_0058e09e(puVar1[uVar9 * 7 + 1],puVar1[uVar9 * 7 + 3]);
      local_20 = 0;
      uVar5 = FUN_0058ddd6(puVar1[uVar9 * 7 + 1],*(undefined4 *)(puVar1[uVar9 * 7 + 4] + 4),
                           *(undefined4 *)puVar1[uVar9 * 7 + 4],0);
      FUN_0055e288((int)(short)((short)puVar1[uVar9 * 7] + 0xf));
      if (uVar9 == 0) {
        FUN_0055e2a6((int)(short)((short)*puVar1 + 0xf),3);
      }
      else {
        FUN_0055e2a6((int)(short)((short)puVar1[uVar9 * 7] + 0xf),4);
      }
      FUN_0055e244((int)(short)((short)puVar1[uVar9 * 7] + 0xf));
      uVar6 = FUN_0058e782(puVar1[uVar9 * 7 + 1],0x471);
      uVar10 = uVar6 | uVar5 | uVar10 | uVar7 | uVar8 | uVar2 | uVar3 | uVar4;
      *(undefined1 *)(puVar1 + uVar9 * 7 + 6) = 1;
      FUN_0055e630(uVar9 & 0xff);
    }
  }
  return CONCAT44(local_20,(uint)(uVar10 != 0));
}

