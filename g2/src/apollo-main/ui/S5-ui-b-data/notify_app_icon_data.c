/* Notification app-icon table (S5-ui-b storage-definition pass, 2.2.6.10).
 *
 * ROM 0x687b60: 89 {app identifier, icon, display name} rows plus the
 * terminating default row {NULL, default icon, "Unknown App"} read by
 * ui/a-61-navigation-data/notify_app_icon.c (NOTIFY_APP_ICON_COUNT = 89).
 * Strings are copied from ROM (the stock rows point into the shared string
 * pool, e.g. "Messages" ROM 0x78a16c is used three times). The icons are the
 * lv_image_dsc_t assets in notify_image_assets_data.c. */
#include <stddef.h>
#include <stdint.h>

/* Same layout as ui/a-61-navigation-data/notify_app_icon.c. */
typedef struct {
    const char *app_identifier; /* +0x0 */
    const void *icon;           /* +0x4 lv_image_dsc_t */
    const char *name;           /* +0x8 */
} g2_notify_app_icon_data_t;
_Static_assert(sizeof(g2_notify_app_icon_data_t) == 12u, "stock record is 12 bytes");

extern const uint8_t g2_notify_app_icon_default_769804[]; /* ROM 0x769804 lv_image_dsc_t */
extern const uint8_t g2_notify_app_icon_769174[]; /* ROM 0x769174 lv_image_dsc_t */
extern const uint8_t g2_notify_app_icon_769190[]; /* ROM 0x769190 lv_image_dsc_t */
extern const uint8_t g2_notify_app_icon_7691ac[]; /* ROM 0x7691ac lv_image_dsc_t */
extern const uint8_t g2_notify_app_icon_769564[]; /* ROM 0x769564 lv_image_dsc_t */
extern const uint8_t g2_notify_app_icon_769580[]; /* ROM 0x769580 lv_image_dsc_t */
extern const uint8_t g2_notify_app_icon_76959c[]; /* ROM 0x76959c lv_image_dsc_t */
extern const uint8_t g2_notify_app_icon_7695b8[]; /* ROM 0x7695b8 lv_image_dsc_t */
extern const uint8_t g2_notify_app_icon_7695d4[]; /* ROM 0x7695d4 lv_image_dsc_t */
extern const uint8_t g2_notify_app_icon_769724[]; /* ROM 0x769724 lv_image_dsc_t */
extern const uint8_t g2_notify_app_icon_769740[]; /* ROM 0x769740 lv_image_dsc_t */
extern const uint8_t g2_notify_app_icon_76975c[]; /* ROM 0x76975c lv_image_dsc_t */
extern const uint8_t g2_notify_app_icon_7697b0[]; /* ROM 0x7697b0 lv_image_dsc_t */
extern const uint8_t g2_notify_app_icon_7697cc[]; /* ROM 0x7697cc lv_image_dsc_t */
extern const uint8_t g2_notify_app_icon_7697e8[]; /* ROM 0x7697e8 lv_image_dsc_t */
extern const uint8_t g2_notify_app_icon_769820[]; /* ROM 0x769820 lv_image_dsc_t */
extern const uint8_t g2_notify_app_icon_76983c[]; /* ROM 0x76983c lv_image_dsc_t */
extern const uint8_t g2_notify_app_icon_769874[]; /* ROM 0x769874 lv_image_dsc_t */
extern const uint8_t g2_notify_app_icon_7698ac[]; /* ROM 0x7698ac lv_image_dsc_t */
extern const uint8_t g2_notify_app_icon_7698c8[]; /* ROM 0x7698c8 lv_image_dsc_t */
extern const uint8_t g2_notify_app_icon_7698e4[]; /* ROM 0x7698e4 lv_image_dsc_t */
extern const uint8_t g2_notify_app_icon_769900[]; /* ROM 0x769900 lv_image_dsc_t */
extern const uint8_t g2_notify_app_icon_76991c[]; /* ROM 0x76991c lv_image_dsc_t */
extern const uint8_t g2_notify_app_icon_769938[]; /* ROM 0x769938 lv_image_dsc_t */
extern const uint8_t g2_notify_app_icon_769954[]; /* ROM 0x769954 lv_image_dsc_t */
extern const uint8_t g2_notify_app_icon_769aa4[]; /* ROM 0x769aa4 lv_image_dsc_t */
extern const uint8_t g2_notify_app_icon_769ac0[]; /* ROM 0x769ac0 lv_image_dsc_t */
extern const uint8_t g2_notify_app_icon_769adc[]; /* ROM 0x769adc lv_image_dsc_t */
extern const uint8_t g2_notify_app_icon_769af8[]; /* ROM 0x769af8 lv_image_dsc_t */

const g2_notify_app_icon_data_t g2_notify_app_icon_table_687b60[90] = {
    {"com.apple.MobileSMS", g2_notify_app_icon_default_769804, "Messages"}, /* 0: id ROM 0x77dec0, name ROM 0x78a16c */
    {"com.android.even_sms", g2_notify_app_icon_default_769804, "Messages"}, /* 1: id ROM 0x775224, name ROM 0x78a16c */
    {"com.android.mms", g2_notify_app_icon_default_769804, "Messages"}, /* 2: id ROM 0x784ff0, name ROM 0x78a16c */
    {"com.apple.mobilephone", g2_notify_app_icon_7691ac, "Phone"}, /* 3: id ROM 0x77523c, name ROM 0x78ca7c */
    {"com.android.even_phone", g2_notify_app_icon_7691ac, "Phone"}, /* 4: id ROM 0x775254, name ROM 0x78ca7c */
    {"com.android.dialer", g2_notify_app_icon_7691ac, "Phone"}, /* 5: id ROM 0x77ded4, name ROM 0x78ca7c */
    {"com.android.phone_incall", g2_notify_app_icon_7691ac, "Phone"}, /* 6: id ROM 0x7695f0, name ROM 0x78ca7c */
    {"com.android.phone_missed", g2_notify_app_icon_7697cc, "Missed Call"}, /* 7: id ROM 0x76960c, name ROM 0x78a178 */
    {"com.apple.mobilephone_missed", g2_notify_app_icon_7697cc, "Missed Call"}, /* 8: id ROM 0x75dfb0, name ROM 0x78a178 */
    {"com.apple.mobilecal", g2_notify_app_icon_769174, "Calendar"}, /* 9: id ROM 0x77dee8, name ROM 0x78a184 */
    {"com.android.even_calendar", g2_notify_app_icon_769174, "Calendar"}, /* 10: id ROM 0x769628, name ROM 0x78a184 */
    {"com.google.calendar", g2_notify_app_icon_769174, "Google Calendar"}, /* 11: id ROM 0x77defc, name ROM 0x785000 */
    {"com.google.android.calendar", g2_notify_app_icon_769174, "Calendar"}, /* 12: id ROM 0x769644, name ROM 0x78a184 */
    {"com.android.even_calendar", g2_notify_app_icon_769174, "Calendar"}, /* 13: id ROM 0x769628, name ROM 0x78a184 */
    {"com.samsung.android.calendar", g2_notify_app_icon_769174, "Calendar"}, /* 14: id ROM 0x75dfd0, name ROM 0x78a184 */
    {"com.cron.app", g2_notify_app_icon_769174, "Cron"}, /* 15: id ROM 0x785010, name ROM 0x78ca84 */
    {"com.cron.calendar", g2_notify_app_icon_769174, "Cron"}, /* 16: id ROM 0x77df10, name ROM 0x78ca84 */
    {"com.apple.mobilemail", g2_notify_app_icon_76975c, "Mail"}, /* 17: id ROM 0x77526c, name ROM 0x78ca8c */
    {"com.apple.mail", g2_notify_app_icon_76975c, "Mail"}, /* 18: id ROM 0x785020, name ROM 0x78ca8c */
    {"com.google.Gmail", g2_notify_app_icon_76975c, "Gmail"}, /* 19: id ROM 0x77df24, name ROM 0x78ca94 */
    {"com.google.android.gm", g2_notify_app_icon_76975c, "Gmail"}, /* 20: id ROM 0x775284, name ROM 0x78ca94 */
    {"com.microsoft.Office.Outlook", g2_notify_app_icon_76975c, "Outlook"}, /* 21: id ROM 0x75dff0, name ROM 0x78ca9c */
    {"com.microsoft.office.outlook", g2_notify_app_icon_76975c, "Outlook"}, /* 22: id ROM 0x75e010, name ROM 0x78ca9c */
    {"com.yahoo.Aerogram", g2_notify_app_icon_76975c, "Yahoo Mail"}, /* 23: id ROM 0x77df38, name ROM 0x78a190 */
    {"com.yahoo.mobile.client.mail", g2_notify_app_icon_76975c, "Yahoo Mail"}, /* 24: id ROM 0x75e030, name ROM 0x78a190 */
    {"com.yahoo.mobile.client.android.mail", g2_notify_app_icon_76975c, "Yahoo Mail"}, /* 25: id ROM 0x7479f4, name ROM 0x78a190 */
    {"ch.protonmail.protonmail", g2_notify_app_icon_76975c, "Proton Mail"}, /* 26: id ROM 0x769660, name ROM 0x78a19c */
    {"ch.protonmail.android", g2_notify_app_icon_76975c, "Proton Mail"}, /* 27: id ROM 0x77529c, name ROM 0x78a19c */
    {"com.tencent.foxmail", g2_notify_app_icon_76975c, "Foxmail"}, /* 28: id ROM 0x77df4c, name ROM 0x78caa4 */
    {"com.tencent.android.foxmail", g2_notify_app_icon_76975c, "Foxmail"}, /* 29: id ROM 0x76967c, name ROM 0x78caa4 */
    {"com.samsung.android.email", g2_notify_app_icon_76975c, "Samsung Email"}, /* 30: id ROM 0x769698, name ROM 0x785030 */
    {"com.samsung.android.email.provider", g2_notify_app_icon_76975c, "Samsung Email"}, /* 31: id ROM 0x7520a0, name ROM 0x785030 */
    {"com.easilydo.mail", g2_notify_app_icon_76975c, "Edison Mail"}, /* 32: id ROM 0x77df60, name ROM 0x78a1a8 */
    {"com.edisonmail.ios", g2_notify_app_icon_76975c, "Edison Mail"}, /* 33: id ROM 0x77df74, name ROM 0x78a1a8 */
    {"com.edisonmail.android", g2_notify_app_icon_76975c, "Edison Mail"}, /* 34: id ROM 0x7752b4, name ROM 0x78a1a8 */
    {"Mailroom.Canary-iOS", g2_notify_app_icon_76975c, "Canary Mail"}, /* 35: id ROM 0x77df88, name ROM 0x78a1b4 */
    {"io.canarymail.android", g2_notify_app_icon_76975c, "Canary Mail"}, /* 36: id ROM 0x7752cc, name ROM 0x78a1b4 */
    {"com.fastmail.FastMail", g2_notify_app_icon_76975c, "Fastmail"}, /* 37: id ROM 0x7752e4, name ROM 0x78a1c0 */
    {"com.fastmail.app", g2_notify_app_icon_76975c, "Fastmail"}, /* 38: id ROM 0x77df9c, name ROM 0x78a1c0 */
    {"com.openai.chatgpt", g2_notify_app_icon_769190, "ChatGPT"}, /* 39: id ROM 0x77dfb0, name ROM 0x78caac */
    {"com.hammerandchisel.discord", g2_notify_app_icon_769564, "Discord"}, /* 40: id ROM 0x7696b4, name ROM 0x78cab4 */
    {"com.discord", g2_notify_app_icon_769564, "Discord"}, /* 41: id ROM 0x78a1cc, name ROM 0x78cab4 */
    {"com.even.g1", g2_notify_app_icon_769580, "Even"}, /* 42: id ROM 0x78a1d8, name ROM 0x78cabc */
    {"com.even.sg", g2_notify_app_icon_769580, "Even"}, /* 43: id ROM 0x78a1e4, name ROM 0x78cabc */
    {"com.facebook.Facebook", g2_notify_app_icon_76959c, "Facebook"}, /* 44: id ROM 0x7752fc, name ROM 0x78a1f0 */
    {"com.facebook.katana", g2_notify_app_icon_76959c, "Facebook"}, /* 45: id ROM 0x77dfc4, name ROM 0x78a1f0 */
    {"com.larksuite.lark", g2_notify_app_icon_7695b8, "Feishu"}, /* 46: id ROM 0x77dfd8, name ROM 0x78cac4 */
    {"com.bytedance.ee.lark", g2_notify_app_icon_7695b8, "Feishu"}, /* 47: id ROM 0x775314, name ROM 0x78cac4 */
    {"com.larksuite.suite", g2_notify_app_icon_7695b8, "Feishu"}, /* 48: id ROM 0x77dfec, name ROM 0x78cac4 */
    {"com.ss.android.lark", g2_notify_app_icon_7695b8, "Feishu"}, /* 49: id ROM 0x77e000, name ROM 0x78cac4 */
    {"com.glovoapp.Glovo", g2_notify_app_icon_7695d4, "Glovo"}, /* 50: id ROM 0x77e014, name ROM 0x78cacc */
    {"com.glovo", g2_notify_app_icon_7695d4, "Glovo"}, /* 51: id ROM 0x78a1fc, name ROM 0x78cacc */
    {"com.burbn.instagram", g2_notify_app_icon_769724, "Instagram"}, /* 52: id ROM 0x77e028, name ROM 0x78a208 */
    {"com.instagram.android", g2_notify_app_icon_769724, "Instagram"}, /* 53: id ROM 0x77532c, name ROM 0x78a208 */
    {"com.linkedin.LinkedIn", g2_notify_app_icon_769740, "LinkedIn"}, /* 54: id ROM 0x775344, name ROM 0x78a214 */
    {"com.linkedin.android", g2_notify_app_icon_769740, "LinkedIn"}, /* 55: id ROM 0x77535c, name ROM 0x78a214 */
    {"com.facebook.Messenger", g2_notify_app_icon_7697b0, "Messenger"}, /* 56: id ROM 0x775374, name ROM 0x78a220 */
    {"com.facebook.orca", g2_notify_app_icon_7697b0, "Messenger"}, /* 57: id ROM 0x77e03c, name ROM 0x78a220 */
    {"co.uk.getmondo", g2_notify_app_icon_7697e8, "Monzo"}, /* 58: id ROM 0x785040, name ROM 0x78cad4 */
    {"com.monzo.app", g2_notify_app_icon_7697e8, "Monzo"}, /* 59: id ROM 0x785050, name ROM 0x78cad4 */
    {"com.monzo", g2_notify_app_icon_7697e8, "Monzo"}, /* 60: id ROM 0x78a22c, name ROM 0x78cad4 */
    {"pinterest", g2_notify_app_icon_769820, "Pinterest"}, /* 61: id ROM 0x78a238, name ROM 0x78a244 */
    {"com.pinterest", g2_notify_app_icon_769820, "Pinterest"}, /* 62: id ROM 0x785060, name ROM 0x78a244 */
    {"com.reddit.Reddit", g2_notify_app_icon_76983c, "Reddit"}, /* 63: id ROM 0x77e050, name ROM 0x78cadc */
    {"com.reddit.frontpage", g2_notify_app_icon_76983c, "Reddit"}, /* 64: id ROM 0x77538c, name ROM 0x78cadc */
    {"com.tinyspeck.chatlyio", g2_notify_app_icon_769874, "Slack"}, /* 65: id ROM 0x7753a4, name ROM 0x78cae4 */
    {"com.Slack", g2_notify_app_icon_769874, "Slack"}, /* 66: id ROM 0x78a250, name ROM 0x78cae4 */
    {"com.toyopagroup.picaboo", g2_notify_app_icon_7698ac, "Snapchat"}, /* 67: id ROM 0x7753bc, name ROM 0x78a25c */
    {"com.snapchat.android", g2_notify_app_icon_7698ac, "Snapchat"}, /* 68: id ROM 0x7753d4, name ROM 0x78a25c */
    {"com.stripe.Stripe", g2_notify_app_icon_7698c8, "Stripe"}, /* 69: id ROM 0x77e064, name ROM 0x78caec */
    {"com.stripe.android", g2_notify_app_icon_7698c8, "Stripe"}, /* 70: id ROM 0x77e078, name ROM 0x78caec */
    {"ph.telegra.Telegraph", g2_notify_app_icon_7698e4, "Telegram"}, /* 71: id ROM 0x7753ec, name ROM 0x78a268 */
    {"org.telegram.messenger", g2_notify_app_icon_7698e4, "Telegram"}, /* 72: id ROM 0x775404, name ROM 0x78a268 */
    {"com.burbn.barcelona", g2_notify_app_icon_769900, "Threads"}, /* 73: id ROM 0x77e08c, name ROM 0x78caf4 */
    {"com.instagram.barcelona", g2_notify_app_icon_769900, "Threads"}, /* 74: id ROM 0x77541c, name ROM 0x78caf4 */
    {"com.zhiliaoapp.musically", g2_notify_app_icon_76991c, "TikTok"}, /* 75: id ROM 0x7696d0, name ROM 0x78cafc */
    {"com.ss.android.ugc.aweme", g2_notify_app_icon_76991c, "TikTok"}, /* 76: id ROM 0x7696ec, name ROM 0x78cafc */
    {"tv.twitch", g2_notify_app_icon_769938, "Twitch"}, /* 77: id ROM 0x78a274, name ROM 0x78cb04 */
    {"tv.twitch.android.app", g2_notify_app_icon_769938, "Twitch"}, /* 78: id ROM 0x775434, name ROM 0x78cb04 */
    {"com.ubercab.UberClient", g2_notify_app_icon_769954, "Uber"}, /* 79: id ROM 0x77544c, name ROM 0x78cb0c */
    {"com.ubercab", g2_notify_app_icon_769954, "Uber"}, /* 80: id ROM 0x78a280, name ROM 0x78cb0c */
    {"com.tencent.xin", g2_notify_app_icon_769aa4, "WeChat"}, /* 81: id ROM 0x785070, name ROM 0x78cb14 */
    {"com.tencent.mm", g2_notify_app_icon_769aa4, "WeChat"}, /* 82: id ROM 0x785080, name ROM 0x78cb14 */
    {"net.whatsapp.WhatsApp", g2_notify_app_icon_769ac0, "WhatsApp"}, /* 83: id ROM 0x775464, name ROM 0x78a28c */
    {"com.whatsapp", g2_notify_app_icon_769ac0, "WhatsApp"}, /* 84: id ROM 0x785090, name ROM 0x78a28c */
    {"com.atebits.Tweetie2", g2_notify_app_icon_769adc, "X"}, /* 85: id ROM 0x77547c, name ROM 0x78f536 */
    {"com.twitter.android", g2_notify_app_icon_769adc, "X"}, /* 86: id ROM 0x77e0a0, name ROM 0x78f536 */
    {"com.google.ios.youtube", g2_notify_app_icon_769af8, "YouTube"}, /* 87: id ROM 0x775494, name ROM 0x78cb1c */
    {"com.google.android.youtube", g2_notify_app_icon_769af8, "YouTube"}, /* 88: id ROM 0x769708, name ROM 0x78cb1c */
    {NULL, g2_notify_app_icon_default_769804, "Unknown App"}, /* 89: id ROM 0x000000, name ROM 0x78a298 */
};
