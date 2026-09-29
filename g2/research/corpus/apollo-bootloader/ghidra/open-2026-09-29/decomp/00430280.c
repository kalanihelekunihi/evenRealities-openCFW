
undefined4 descriptor_register_430280(int param_1,uint param_2)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  uint local_38;
  int aiStack_34 [7];
  
  if ((param_1 == 0) || (param_2 == 0)) {
    uVar2 = 0xffffffff;
  }
  else {
    for (uVar3 = 0; uVar3 < param_2; uVar3 = uVar3 + 1) {
      if (*(char *)(uVar3 * 0xc + param_1 + 4) == '\x01') {
        FUN_0041d92c(*(undefined4 *)(param_1 + uVar3 * 0xc),*DAT_0043046c);
        FUN_0041d9aa(*(undefined4 *)(param_1 + uVar3 * 0xc),
                     *(char *)(uVar3 * 0xc + param_1 + 5) == '\x01');
      }
      else if (*(char *)(uVar3 * 0xc + param_1 + 4) == '\x02') {
        FUN_0041d92c(*(undefined4 *)(param_1 + uVar3 * 0xc),
                     *DAT_00430464 & 0xffffff3f | (*(byte *)(uVar3 * 0xc + param_1 + 6) & 3) << 6);
        if ((*(char *)(uVar3 * 0xc + param_1 + 6) != '\0') &&
           (*(int *)(uVar3 * 0xc + param_1 + 8) != 0)) {
          local_38 = *(uint *)(param_1 + uVar3 * 0xc);
          FUN_00415ff4(aiStack_34,0x1c);
          aiStack_34[local_38 >> 5] = 1 << (local_38 & 0x1f);
          FUN_0041dcca(0,1,aiStack_34);
          FUN_0041de3c(0,aiStack_34);
          FUN_0041e000(0,local_38,*(undefined4 *)(uVar3 * 0xc + param_1 + 8),0);
          FUN_0041da84(0,1,&local_38);
          iVar1 = DAT_00430468;
          scb_priority_nibble_43025c
                    ((int)*(short *)(DAT_00430468 + (*(uint *)(param_1 + uVar3 * 0xc) >> 5) * 2),4);
          nvic_enable_bit_430240
                    ((int)*(short *)(iVar1 + (*(uint *)(param_1 + uVar3 * 0xc) >> 5) * 2));
        }
      }
      else if (*(char *)(uVar3 * 0xc + param_1 + 4) == '\x04') {
        FUN_0041d92c(*(undefined4 *)(param_1 + uVar3 * 0xc),*DAT_00430460);
      }
    }
    uVar2 = 0;
  }
  return uVar2;
}

