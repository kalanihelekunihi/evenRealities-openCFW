
undefined8 FUN_005db3ec(int param_1,int param_2,undefined4 param_3,int param_4)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  int local_18;
  
  uVar3 = *(undefined4 *)(param_1 + 0x1c);
  *(undefined4 *)(param_2 + 0x84) = 0;
  *(undefined4 *)(param_2 + 0x88) = 0;
  *(undefined4 *)(param_2 + 0x8c) = 0;
  iVar5 = param_2;
  local_18 = param_4;
  do {
    uVar1 = *(undefined4 *)(param_1 + 8);
    iVar2 = FT_Stream_ReadULong(param_1,&local_18);
    iVar4 = DAT_005db940;
    if (local_18 != 0) {
LAB_005db532:
      return CONCAT44(iVar5,local_18);
    }
    if (iVar2 != DAT_005db93c) {
      if (((((iVar2 == 0x10000) || (iVar2 == DAT_005db940)) || (iVar2 == DAT_005db94c)) ||
          ((iVar2 == DAT_005db950 || (iVar2 == DAT_005db954)))) ||
         ((iVar2 == DAT_005db958 || ((iVar2 == DAT_005db95c || (iVar2 == 0x20000)))))) {
        *(int *)(param_2 + 0x84) = DAT_005db940;
        if (iVar2 == iVar4) {
          local_18 = FT_Stream_ReadFields(param_1,PTR_DAT_005dc11c,param_2 + 0x84);
          if (local_18 == 0) {
            if (*(int *)(param_2 + 0x8c) == 0) {
              local_18 = 8;
            }
            else if (*(uint *)(param_1 + 4) >> 5 < *(uint *)(param_2 + 0x8c)) {
              local_18 = 10;
            }
            else {
              iVar5 = 0;
              uVar3 = ft_mem_realloc(uVar3,4,0,*(undefined4 *)(param_2 + 0x8c),0,&local_18);
              *(undefined4 *)(param_2 + 0x90) = uVar3;
              if ((local_18 == 0) &&
                 (local_18 = FT_Stream_EnterFrame(param_1,*(int *)(param_2 + 0x8c) << 2),
                 local_18 == 0)) {
                for (iVar4 = 0; iVar4 < *(int *)(param_2 + 0x8c); iVar4 = iVar4 + 1) {
                  uVar3 = FT_Stream_GetULong(param_1);
                  *(undefined4 *)(*(int *)(param_2 + 0x90) + iVar4 * 4) = uVar3;
                }
                FT_Stream_ExitFrame(param_1);
              }
            }
          }
        }
        else {
          *(undefined4 *)(param_2 + 0x88) = 0x10000;
          *(undefined4 *)(param_2 + 0x8c) = 1;
          uVar3 = ft_mem_alloc(uVar3,4,&local_18);
          *(undefined4 *)(param_2 + 0x90) = uVar3;
          if (local_18 == 0) {
            **(undefined4 **)(param_2 + 0x90) = uVar1;
          }
        }
      }
      else {
        local_18 = 2;
      }
      goto LAB_005db532;
    }
    local_18 = FT_Stream_Seek(param_1,uVar1);
    if ((local_18 != 0) || (local_18 = FUN_005dae90(param_1,param_2), local_18 != 0))
    goto LAB_005db532;
    param_1 = *(int *)(param_2 + 0x68);
  } while( true );
}

