
/* WARNING: Type propagation algorithm not settling */

undefined8 cff_get_advances(int param_1,undefined4 *param_2,uint param_3,uint param_4,int param_5)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  undefined4 *local_30;
  undefined1 local_2c [4];
  uint uStack_28;
  
  iVar2 = 0;
  iVar3 = *(int *)(param_1 + 0x54);
  local_30 = param_2;
  local_2c = (undefined1  [4])param_3;
  uStack_28 = param_4;
  if ((int)((uint)*(byte *)(param_1 + 8) << 0x1c) < 0) {
    if ((int)(param_4 << 0x1b) < 0) {
      if ((((*(uint *)(param_1 + 4) & DAT_005acd04) != 0) || (*(int *)(param_1 + 8) << 0x10 < 0)) &&
         (-1 < (int)((uint)*(byte *)(param_1 + 0x2c0) << 0x1b))) {
        iVar2 = 7;
        goto LAB_005ac13c;
      }
      if (*(char *)(param_1 + 0x124) != '\0') {
        for (uVar4 = 0; uVar4 < param_3; uVar4 = uVar4 + 1) {
          local_30 = (undefined4 *)((int)local_2c + 2);
          (**(code **)(*(int *)(param_1 + 0x21c) + 0x70))(param_1,1,(int)param_2 + uVar4,&uStack_28)
          ;
          *(uint *)(param_5 + uVar4 * 4) = (uint)local_2c >> 0x10;
        }
LAB_005ac104:
        iVar2 = 0;
        goto LAB_005ac13c;
      }
    }
    else {
      if ((((*(uint *)(param_1 + 4) & DAT_005acd04) != 0) || (*(int *)(param_1 + 8) << 0x10 < 0)) &&
         (-1 < (int)((uint)*(byte *)(param_1 + 0x2c0) << 0x1e))) {
        iVar2 = 7;
        goto LAB_005ac13c;
      }
      if (*(short *)(param_1 + 0xfa) != 0) {
        for (uVar4 = 0; uVar4 < param_3; uVar4 = uVar4 + 1) {
          local_30 = (undefined4 *)local_2c;
          (**(code **)(*(int *)(param_1 + 0x21c) + 0x70))(param_1,0,(int)param_2 + uVar4,&uStack_28)
          ;
          *(uint *)(param_5 + uVar4 * 4) = (uint)local_2c & 0xffff;
        }
        goto LAB_005ac104;
      }
    }
  }
  uVar4 = 0;
  while ((uVar4 < param_3 &&
         (iVar2 = cff_glyph_load(iVar3,*(undefined4 *)(param_1 + 0x58),(int)param_2 + uVar4,
                                 param_4 | 0x100), iVar2 == 0))) {
    if ((int)(param_4 << 0x1b) < 0) {
      uVar1 = *(undefined4 *)(iVar3 + 0x3c);
    }
    else {
      uVar1 = *(undefined4 *)(iVar3 + 0x38);
    }
    *(undefined4 *)(param_5 + uVar4 * 4) = uVar1;
    uVar4 = uVar4 + 1;
  }
LAB_005ac13c:
  return CONCAT44(local_30,iVar2);
}

