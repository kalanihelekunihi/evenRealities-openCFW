
undefined8 af_property_get(int param_1,undefined4 param_2,uint *param_3,int param_4)

{
  undefined1 uVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  uint *local_28;
  int local_24;
  
  iVar3 = *(int *)(param_1 + 0xc);
  uVar4 = *(uint *)(param_1 + 0x10);
  uVar1 = *(undefined1 *)(param_1 + 0x14);
  local_28 = param_3;
  local_24 = param_4;
  iVar2 = FUN_0046cacc(param_2,DAT_005abc58);
  if (iVar2 == 0) {
    iVar2 = af_property_get_face_globals(*param_3,&local_24,param_1);
    if (iVar2 == 0) {
      param_3[1] = *(uint *)(local_24 + 8);
    }
  }
  else {
    iVar2 = FUN_0046cacc(param_2,DAT_005abc3c);
    if (iVar2 == 0) {
      *param_3 = (uint)*(byte *)(*(int *)(DAT_005abc40 + iVar3 * 4) + 2);
      iVar2 = 0;
    }
    else {
      iVar2 = FUN_0046cacc(param_2,DAT_005abc44);
      if (iVar2 == 0) {
        *param_3 = uVar4;
        iVar2 = 0;
      }
      else {
        iVar2 = FUN_0046cacc(param_2,DAT_005abc48);
        if (iVar2 == 0) {
          iVar2 = af_property_get_face_globals(*param_3,&local_28,param_1);
          if (iVar2 == 0) {
            param_3[1] = local_28[3];
          }
        }
        else {
          iVar2 = FUN_0046cacc(param_2,DAT_005abc4c);
          if (iVar2 == 0) {
            *(undefined1 *)param_3 = uVar1;
            iVar2 = 0;
          }
          else {
            iVar2 = FUN_0046cacc(param_2,DAT_005abc50);
            if (iVar2 == 0) {
              *param_3 = *(uint *)(param_1 + 0x18);
              param_3[1] = *(uint *)(param_1 + 0x1c);
              param_3[2] = *(uint *)(param_1 + 0x20);
              param_3[3] = *(uint *)(param_1 + 0x24);
              param_3[4] = *(uint *)(param_1 + 0x28);
              param_3[5] = *(uint *)(param_1 + 0x2c);
              param_3[6] = *(uint *)(param_1 + 0x30);
              param_3[7] = *(uint *)(param_1 + 0x34);
              iVar2 = 0;
            }
            else {
              iVar2 = FUN_0046cacc(param_2,DAT_005abc54);
              if (iVar2 == 0) {
                *(undefined1 *)param_3 = *(undefined1 *)(param_1 + 0x15);
                iVar2 = 0;
              }
              else {
                iVar2 = 0xc;
              }
            }
          }
        }
      }
    }
  }
  return CONCAT44(local_28,iVar2);
}

