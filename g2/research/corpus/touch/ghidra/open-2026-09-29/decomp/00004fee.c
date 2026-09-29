
int touch_pipeline_1cee_update(int param_1,ushort *param_2,undefined4 param_3,int *param_4)

{
  int iVar1;
  uint uVar2;
  undefined4 uVar3;
  uint uVar4;
  int *piVar5;
  
  piVar5 = param_4;
  iVar1 = touch_leaf_1ab4_constant_0();
  if (iVar1 == 0) {
    uVar2 = (uint)*param_2;
    uVar4 = (uint)param_2[1];
    if (uVar4 <= uVar2) {
      *(undefined1 *)((int)param_2 + 7) = 0;
    }
    if (*(ushort *)(param_1 + 0x1c) + uVar2 < uVar4) {
      if ((ushort)*(byte *)((int)param_2 + 7) < *(ushort *)(param_1 + 0xc)) {
        *(byte *)((int)param_2 + 7) = *(byte *)((int)param_2 + 7) + 1;
      }
      else {
        touch_record_1ab8_reset(param_2);
      }
    }
    else if ((*(char *)(*param_4 + 0x28) != '\0') || (uVar2 <= uVar4 + *(ushort *)(param_1 + 0x1a)))
    {
      uVar3 = touch_leaf_1cde_blend_u8
                        (uVar2 << 8,(uint)CONCAT21(param_2[1],(char)param_2[4]),
                         *(undefined1 *)(param_1 + 0x22),0x22,piVar5);
      param_2[1] = (ushort)((uint)uVar3 >> 8);
      *(char *)(param_2 + 4) = (char)uVar3;
    }
  }
  return iVar1;
}

