
undefined4 dmPrivActSetPrivacyMode(int param_1)

{
  undefined4 unaff_r7;
  
  HciLeSetPrivacyModeCmd(*(undefined1 *)(param_1 + 4),param_1 + 5,*(undefined1 *)(param_1 + 0xb));
  return unaff_r7;
}

