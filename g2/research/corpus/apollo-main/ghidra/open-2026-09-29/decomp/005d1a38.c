
undefined4 FUN_005d1a38(int param_1,int param_2,char param_3,undefined4 param_4)

{
  FUN_0043c0e4(param_1,0x28c,0);
  if (param_3 == '\0') {
    FUN_005d176a(param_1,param_2,0);
    *(undefined4 *)(param_1 + 0x214) = *(undefined4 *)(param_2 + 0x6c);
    *(int *)(param_1 + 0x21c) = *(int *)(param_2 + 0x6c) + 0xc20;
    *(undefined4 *)(param_1 + 0x218) = *(undefined4 *)(param_2 + 0x2fc);
    *(undefined4 *)(param_1 + 0x230) = *(undefined4 *)(param_2 + 0x2dc);
    *(undefined4 *)(param_1 + 0x240) = *(undefined4 *)(param_2 + 0x2ec);
    *(undefined4 *)(param_1 + 0x238) = *(undefined4 *)(param_2 + 0x2e4);
    *(undefined4 *)(param_1 + 0x22c) = *(undefined4 *)(param_2 + 0x2d8);
    *(undefined4 *)(param_1 + 0x23c) = *(undefined4 *)(param_2 + 0x2e8);
    *(undefined4 *)(param_1 + 0x234) = *(undefined4 *)(param_2 + 0x2e0);
    *(int *)(param_1 + 0x220) = param_2 + 0x248;
    *(undefined1 *)(param_1 + 0x224) = *(undefined1 *)(param_2 + 0x251);
    *(undefined1 *)(param_1 + 0x24c) = *(undefined1 *)(param_2 + 0x2f8);
    *(undefined4 *)(param_1 + 0x250) = *(undefined4 *)(param_2 + 0x300);
    *(undefined4 *)(param_1 + 0x254) = *(undefined4 *)(param_2 + 0x304);
  }
  else {
    FUN_005d176a(param_1,param_2,param_3);
    *(int *)(param_1 + 0x21c) = param_2 + 0x5e0;
    *(undefined4 *)(param_1 + 600) = *(undefined4 *)(param_2 + 0x540);
    *(undefined4 *)(param_1 + 0x248) = *(undefined4 *)(param_2 + 0x544);
    *(undefined4 *)(param_1 + 0x244) = *(undefined4 *)(param_2 + 0x548);
    *(undefined1 *)(param_1 + 0x24c) = *(undefined1 *)(param_2 + 0x5bc);
    *(undefined4 *)(param_1 + 0x280) = *(undefined4 *)(param_2 + 0x5b8);
    *(undefined4 *)(param_1 + 0x22c) = *(undefined4 *)(param_2 + 0x550);
    *(undefined4 *)(param_1 + 0x23c) = *(undefined4 *)(param_2 + 0x554);
    *(undefined4 *)(param_1 + 0x260) = *(undefined4 *)(param_2 + 0x558);
    *(undefined4 *)(param_1 + 0x264) = *(undefined4 *)(param_2 + 0x55c);
    *(undefined4 *)(param_1 + 0x284) = *(undefined4 *)(param_2 + 0x5d4);
    *(undefined4 *)(param_1 + 0x288) = *(undefined4 *)(param_2 + 0x5d8);
    *(undefined4 *)(param_1 + 0x25c) = *(undefined4 *)(param_2 + 0x54c);
  }
  return param_4;
}

