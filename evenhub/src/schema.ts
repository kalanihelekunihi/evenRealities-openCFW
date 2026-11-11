// EvenHub wire schema, recovered from the stock nanopb descriptors (not from the
// official SDK, which never touches protobuf):
//   fw 2.2.6.10 root pb_msgdesc_t @ 0x0077754C (23 fields)
//   fw 2.3.2.14 root pb_msgdesc_t @ 0x007D3AE4 (26 fields)
// Dumps: evenhub/docs/schema-dump-*.txt (tools/dump_nanopb_desc.py).
// cmd <-> oneof tag pairs are pinned by the firmware senders/dispatchers in
// g2/src/apollo-main/ui/a-25|a-26-evenhub-data-parser and a-14-evenhub-ui.
// Names follow the official SDK's "PB:" comments where a field was matched;
// entries marked `inferred` are field-order matches only.

export const EVENHUB_SERVICE_ID = 0xe0; // EVENHUB_APP_ID, sync app id / BLE notify id

/** Root message: field 1 = cmd (u8), field 2 = magicRandom (u8, echoed), fields 3.. = oneof Msg_Ctx. */
export const ROOT = { cmd: 1, magic: 2 } as const;

/** cmd byte and the oneof tag that must accompany it. */
export const Cmd = {
  CreateStartUpPage: { cmd: 0x00, tag: 3 },
  CreateStartUpPageResult: { cmd: 0x01, tag: 4 },
  DeviceEvent: { cmd: 0x02, tag: 13 },
  ImageRawData: { cmd: 0x03, tag: 5 },
  ImageRawDataResult: { cmd: 0x04, tag: 6 },
  TextContainerUpgrade: { cmd: 0x05, tag: 9 },
  TextContainerUpgradeResult: { cmd: 0x06, tag: 10 },
  RebuildPage: { cmd: 0x07, tag: 7 },
  RebuildPageResult: { cmd: 0x08, tag: 8 },
  ShutDownPage: { cmd: 0x09, tag: 11 },
  ShutDownPageResult: { cmd: 0x0a, tag: 12 },
  PrivateDeviceEvent: { cmd: 0x0b, tag: 16 }, // glasses-internal (master->slave relay)
  HeartBeat: { cmd: 0x0c, tag: 14 },
  HeartBeatResult: { cmd: 0x0c, tag: 15 },
  SystemEvent: { cmd: 0x0e, tag: 17 },        // glasses-internal (timeout page)
  AudioControl: { cmd: 0x0f, tag: 18 },
  AudioControlResult: { cmd: 0x10, tag: 19 },
  MenuStartup: { cmd: 0x11, tag: 20 },        // glasses -> phone: app launched from glasses menu
  MenuStartupFailed: { cmd: 0x12, tag: 21 },
  ImuControl: { cmd: 0x13, tag: 22 },
  ImuControlResult: { cmd: 0x14, tag: 23 },
} as const;

export const CreateF = { containerTotalNum: 1, list: 2, text: 3, image: 4, widgetId: 5, menu: 6 /* fw>=2.3 */, unknown7: 7 } as const;
export const RebuildF = { containerTotalNum: 1, list: 2, text: 3, image: 4, menu: 5 /* fw>=2.3 */ } as const;

/** Shared geometry prefix for list/text containers (tags 1..9). */
export const BoxF = { x: 1, y: 2, width: 3, height: 4, borderWidth: 5, borderColor: 6, borderRadius: 7, padding: 8, containerID: 9, containerName: 10 } as const;
export const ListF = { ...BoxF, itemContainer: 11, isEventCapture: 12, zOrderIndex: 13 /* inferred */ } as const;
export const ListItemsF = { itemCount: 1, itemWidth: 2, isItemSelectBorderEn: 3, itemName: 4 } as const;
export const TextF = { ...BoxF, isEventCapture: 11, content: 12, zOrderIndex: 13 /* SDK 0.0.12 */, textColor: 14 /* fw>=2.3 */ } as const;
export const ImageF = { x: 1, y: 2, width: 3, height: 4, containerID: 5, containerName: 6, zOrderIndex: 7 /* SDK 0.0.12 */ } as const;
export const MenuF = { item: 1 } as const;
export const MenuItemF = { itemName: 1, itemID: 2, unknown3: 3, subItem: 4, unknown5: 5 } as const;

export const ImgRawF = { containerID: 1, containerName: 2, sessionId: 3, totalSize: 4, compressMode: 5, fragmentIndex: 6, fragmentPacketSize: 7, data: 8 } as const;
export const ImgRawResultF = { ...ImgRawF, status: 8 } as const; // tag 8 is a u8 status in the reply
export const TextUpgradeF = { containerID: 1, containerName: 2, contentOffset: 3, contentLength: 4, content: 5, textColor: 6 /* fw>=2.3 */ } as const;

export const DeviceEventF = { list: 1, text: 2, sys: 3 } as const;
export const ListEventF = { containerID: 1, containerName: 2, itemName: 3, itemIndex: 4, eventType: 5 } as const;
export const TextEventF = { containerID: 1, containerName: 2, eventType: 3 } as const;
export const SysEventF = { eventType: 1, eventSource: 2, imu: 3, exitReason: 4 } as const;

/** Firmware storage limits (nanopb static sizes, fw 2.2.6.10 / 2.3.2.14). */
export const Limits = {
  maxListContainers: 4, maxTextContainers: 8, maxImageContainers: 4,
  containerNameBytes: 15,      // char[16] incl. NUL
  listItems: 20, listItemNameBytes: 63,
  textCreateBytes: 999,        // char[1000]
  textUpgradeBytes: 1999,      // char[2000]
  imageFragmentBytes: 4096,    // pb bytes field capacity 4098 incl. 2-byte size
  /** Practical fragment size: TPL caps the whole pb message at 0x1000, envelope+header <= ~60 B. */
  imageFragmentDefault: 4000,
  menuItems: 10, menuNameBytes: 31, menuSubItems: 5,
  menuStartupFailedText: 199,
  maxEventCapture: 1,          // firmware rejects >= 2
  maxObjects: 12,              // checked as < 13
  /** Property ranges; one violation fails the whole create/rebuild with code 1. */
  borderWidth: 5, borderColor: 15, borderRadius: 10, padding: 32,
} as const;

export const Display = { width: 576, height: 288 } as const;

export const OsEvent = {
  CLICK: 0, SCROLL_TOP: 1, SCROLL_BOTTOM: 2, DOUBLE_CLICK: 3, FOREGROUND_ENTER: 4, FOREGROUND_EXIT: 5,
  ABNORMAL_EXIT: 6, SYSTEM_EXIT: 7, IMU_DATA_REPORT: 8, LONG_PRESS: 9, LONG_PRESS_RELEASE: 10,
} as const;
export const EventSource = { NONE: 0, GLASSES_R: 1, RING: 2, GLASSES_L: 3 } as const;
export const Compress = { NONE: 0, RLE: 1, LZ4: 2 } as const;
export const ImageStatus = { OK: 4, FAIL: 5 } as const; // evenhub_send_image_raw_data_response

/** EvenHub_ErrorCode_List ordinals; the firmware replies with these values
 * (create 0..3, image 4/5, rebuild 6/7, text 8/9, shutdown 10/11, heartbeat 12, audio 13/14). */
export const Result = {
  CREATE_SUCCESS: 0, CREATE_INVALID_CONTAINER: 1, CREATE_OVERSIZE_RESPONSE_CONTAINER: 2, CREATE_OUT_OF_MEMORY: 3,
  IMAGE_SUCCESS: 4, IMAGE_FAILED: 5, REBUILD_SUCCESS: 6, REBUILD_FAILED: 7,
  TEXT_SUCCESS: 8, TEXT_FAILED: 9, SHUTDOWN_SUCCESS: 10, SHUTDOWN_FAILED: 11,
  HEARTBEAT_SUCCESS: 12, AUDIO_SUCCESS: 13, AUDIO_FAILED: 14,
} as const;
