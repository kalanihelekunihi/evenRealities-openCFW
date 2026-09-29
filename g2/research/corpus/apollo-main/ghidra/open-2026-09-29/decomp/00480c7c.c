
void FUN_00480c7c(int param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  bool bVar1;
  int iVar2;
  uint local_10;
  undefined4 uStack_c;
  
  local_10 = param_3;
  uStack_c = param_4;
  iVar2 = FUN_004d3f3c(1,0x244,1,&local_10);
  *(undefined4 *)(param_1 + 0xc) = 0;
  if (iVar2 == 0) {
    if ((((*DAT_00480e7c & 0xff) >> 4 == 2) && (1 < (*DAT_00480e7c & 0xf))) && (local_10 < 0xff)) {
      bVar1 = true;
    }
    else {
      bVar1 = false;
    }
    if (bVar1) {
      if ((*DAT_00480e7c & 0xf) != 3) {
        local_10 = local_10 - 1;
      }
      *(uint *)(param_1 + 0xc) = *(uint *)(param_1 + 0xc) & 0xffff00ff | 0x200;
      *(uint *)(param_1 + 0xc) = *(uint *)(param_1 + 0xc) & 0xffffff00 | local_10 & 0xff;
      *(uint *)(param_1 + 0xc) = *(uint *)(param_1 + 0xc) | 0x20000;
      *(uint *)(param_1 + 0xc) = *(uint *)(param_1 + 0xc) | 0x10000;
    }
    else {
      *(uint *)(param_1 + 0xc) = *(uint *)(param_1 + 0xc) & 0xffff00ff;
      *(uint *)(param_1 + 0xc) = *(uint *)(param_1 + 0xc) & 0xffffff00 | local_10 & 0xff;
      *(uint *)(param_1 + 0xc) = *(uint *)(param_1 + 0xc) & 0xfffdffff;
      *(uint *)(param_1 + 0xc) = *(uint *)(param_1 + 0xc) | 0x10000;
    }
  }
  else {
    *(uint *)(param_1 + 0xc) = *(uint *)(param_1 + 0xc) & 0xffff00ff;
    *(uint *)(param_1 + 0xc) = *(uint *)(param_1 + 0xc) & 0xffffff00 | local_10 & 0xff;
    *(uint *)(param_1 + 0xc) = *(uint *)(param_1 + 0xc) & 0xfffdffff;
    *(uint *)(param_1 + 0xc) = *(uint *)(param_1 + 0xc) & 0xfffeffff;
  }
  return;
}

