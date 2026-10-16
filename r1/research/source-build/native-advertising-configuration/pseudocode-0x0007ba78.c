/* ================================================================
 * entry: 0x0007ba78
 * end:   0x0007babd
 * size:  70 bytes
 * name:  FUN_0007ba78
 * ================================================================ */

void FUN_0007ba78(undefined4 param_1,undefined1 *param_2)

{
  undefined1 uVar1;
  undefined1 auStack_88 [31];
  undefined1 auStack_69 [30];
  char local_4b;

  FUN_00073930(*(undefined4 *)(DAT_0007bac0 + 4),auStack_88,0x7c);
  if (local_4b == -1) {
    FUN_0002779c(param_1,0xf,0xff);
    if (param_2 == (undefined1 *)0x0) {
      return;
    }
    uVar1 = 0;
  }
  else {
    FUN_0002775c(param_1,auStack_69,0xf);
    if (param_2 == (undefined1 *)0x0) {
      return;
    }
    uVar1 = 0xf;
  }
  *param_2 = uVar1;
  return;
}



