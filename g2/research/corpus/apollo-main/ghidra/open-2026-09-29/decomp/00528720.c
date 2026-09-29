
undefined8
raccess_guess_apple_generic
          (undefined4 param_1,undefined4 param_2,int param_3,int param_4,undefined4 *param_5)

{
  bool bVar1;
  ushort uVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  int iVar6;
  int local_20;
  int iStack_1c;
  
  local_20 = param_3;
  iStack_1c = param_4;
  iVar3 = FT_Stream_ReadULong(param_2,&local_20);
  iVar6 = local_20;
  if (local_20 == 0) {
    if (iVar3 == param_4) {
      FT_Stream_ReadULong(param_2,&local_20);
      iVar6 = local_20;
      if (((local_20 == 0) &&
          (local_20 = FT_Stream_Skip(param_2,0x10), iVar6 = local_20, local_20 == 0)) &&
         (uVar2 = FT_Stream_ReadUShort(param_2,&local_20), iVar6 = local_20, local_20 == 0)) {
        if (uVar2 == 0) {
          iVar6 = 2;
        }
        else {
          for (iVar3 = 0; iVar3 < (int)(uint)uVar2; iVar3 = iVar3 + 1) {
            iVar4 = FT_Stream_ReadULong(param_2,&local_20);
            iVar6 = local_20;
            if (local_20 != 0) goto LAB_005287fe;
            if (iVar4 == 2) {
              uVar5 = FT_Stream_ReadULong(param_2,&local_20);
              if ((local_20 == 0) && (FT_Stream_ReadULong(param_2,&local_20), local_20 == 0)) {
                bVar1 = false;
              }
              else {
                bVar1 = true;
              }
              if (!bVar1) {
                *param_5 = uVar5;
                iVar6 = 0;
                goto LAB_005287fe;
              }
            }
            else {
              iVar6 = FT_Stream_Skip(param_2,8);
              local_20 = iVar6;
              if (iVar6 != 0) goto LAB_005287fe;
            }
          }
          iVar6 = 2;
        }
      }
    }
    else {
      iVar6 = 2;
    }
  }
LAB_005287fe:
  return CONCAT44(local_20,iVar6);
}

