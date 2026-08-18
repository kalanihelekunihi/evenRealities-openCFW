#!/usr/bin/env swift

import Foundation
@preconcurrency import CoreBluetooth

private let serviceUUID = CBUUID(string: "8FCE0001-4A7D-4F9F-A83D-62F359A104D1")
private let controlUUID = CBUUID(string: "8FCE0010-4A7D-4F9F-A83D-62F359A104D1")
private let dataUUID = CBUUID(string: "8FCE0011-4A7D-4F9F-A83D-62F359A104D1")
private let statusUUID = CBUUID(string: "8FCE0012-4A7D-4F9F-A83D-62F359A104D1")

private struct Options {
    let image: URL
    let match: String
    let timeout: TimeInterval

    static func parse() -> Options {
        var image: URL?
        var match = "OPENR1-RECOVERY"
        var timeout: TimeInterval = 900
        var index = 1
        while index < CommandLine.arguments.count {
            switch CommandLine.arguments[index] {
            case "--image":
                index += 1
                guard index < CommandLine.arguments.count else { usage() }
                image = URL(fileURLWithPath: CommandLine.arguments[index])
            case "--match":
                index += 1
                guard index < CommandLine.arguments.count else { usage() }
                match = CommandLine.arguments[index]
            case "--timeout":
                index += 1
                guard index < CommandLine.arguments.count,
                      let value = TimeInterval(CommandLine.arguments[index]),
                      value >= 30 else { usage() }
                timeout = value
            case "--help", "-h":
                usage(exitCode: 0)
            default:
                usage()
            }
            index += 1
        }
        guard let image else { usage() }
        return Options(image: image, match: match, timeout: timeout)
    }

    private static func usage(exitCode: Int32 = 64) -> Never {
        let stream = exitCode == 0 ? stdout : stderr
        fputs("usage: upload_openr1_recovery --image signed.bin [--match name-or-uuid] [--timeout seconds]\n", stream)
        fputs("Uploads only through the source-built OPENR1-RECOVERY service; the loader enforces the bundled MCUboot signature.\n", stream)
        exit(exitCode)
    }
}

private enum PendingWrite {
    case none
    case abort
    case start
    case data(Int)
    case finish
}

private func littleEndianUInt32(_ bytes: [UInt8], _ offset: Int) -> UInt32 {
    UInt32(bytes[offset]) |
        (UInt32(bytes[offset + 1]) << 8) |
        (UInt32(bytes[offset + 2]) << 16) |
        (UInt32(bytes[offset + 3]) << 24)
}

private func appendLittleEndian(_ value: UInt32, to data: inout Data) {
    data.append(UInt8(truncatingIfNeeded: value))
    data.append(UInt8(truncatingIfNeeded: value >> 8))
    data.append(UInt8(truncatingIfNeeded: value >> 16))
    data.append(UInt8(truncatingIfNeeded: value >> 24))
}

private final class RecoveryUploader: NSObject,
    CBCentralManagerDelegate, CBPeripheralDelegate {
    private let options: Options
    private let image: Data
    private var central: CBCentralManager!
    private var peripheral: CBPeripheral?
    private var control: CBCharacteristic?
    private var dataCharacteristic: CBCharacteristic?
    private var status: CBCharacteristic?
    private var pending = PendingWrite.none
    private var sentOffset = 0
    private var reconnectCount = 0
    private var deadline: DispatchWorkItem?

    init(options: Options) throws {
        let input = try Data(contentsOf: options.image, options: .mappedIfSafe)
        guard !input.isEmpty, input.count <= 0x000A_A000 else {
            throw NSError(domain: "openr1-recovery", code: 64,
                          userInfo: [NSLocalizedDescriptionKey:
                            "signed image must contain 1...696320 bytes"])
        }
        self.options = options
        image = input
        super.init()
        central = CBCentralManager(delegate: self, queue: .main)
        let timeout = DispatchWorkItem { [weak self] in
            self?.fail("timed out before the recovery loader accepted the image")
        }
        deadline = timeout
        DispatchQueue.main.asyncAfter(deadline: .now() + options.timeout,
                                      execute: timeout)
    }

    func centralManagerDidUpdateState(_ central: CBCentralManager) {
        guard central.state == .poweredOn else {
            if central.state != .unknown && central.state != .resetting {
                fail("Bluetooth is unavailable (state \(central.state.rawValue))")
            }
            return
        }
        scan()
    }

    private func scan() {
        central.scanForPeripherals(withServices: [serviceUUID],
            options: [CBCentralManagerScanOptionAllowDuplicatesKey: false])
    }

    func centralManager(_ central: CBCentralManager, didDiscover candidate: CBPeripheral,
        advertisementData: [String: Any], rssi RSSI: NSNumber) {
        let advertisedName = advertisementData[CBAdvertisementDataLocalNameKey] as? String
        let identity = candidate.identifier.uuidString
        let name = advertisedName ?? candidate.name ?? ""
        guard options.match.caseInsensitiveCompare("OPENR1-RECOVERY") == .orderedSame ||
              name.localizedCaseInsensitiveContains(options.match) ||
              identity.caseInsensitiveCompare(options.match) == .orderedSame else { return }
        central.stopScan()
        peripheral = candidate
        candidate.delegate = self
        print("openR1 recovery: connecting \(name.isEmpty ? identity : name)")
        central.connect(candidate)
    }

    func centralManager(_ central: CBCentralManager, didConnect peripheral: CBPeripheral) {
        peripheral.discoverServices([serviceUUID])
    }

    func centralManager(_ central: CBCentralManager, didFailToConnect peripheral: CBPeripheral,
        error: Error?) {
        reconnect("connection failed", error: error)
    }

    func centralManager(_ central: CBCentralManager, didDisconnectPeripheral peripheral: CBPeripheral,
        error: Error?) {
        reconnect("disconnected", error: error)
    }

    private func reconnect(_ message: String, error: Error?) {
        reconnectCount += 1
        self.peripheral = nil
        control = nil
        dataCharacteristic = nil
        status = nil
        pending = .none
        let suffix = error.map { ": \($0.localizedDescription)" } ?? ""
        print("openR1 recovery: \(message)\(suffix); resuming (attempt \(reconnectCount))")
        scan()
    }

    func peripheral(_ peripheral: CBPeripheral, didDiscoverServices error: Error?) {
        if let error { fail("service discovery failed: \(error.localizedDescription)") }
        guard let service = peripheral.services?.first(where: { $0.uuid == serviceUUID }) else {
            fail("source-built recovery service is absent")
        }
        peripheral.discoverCharacteristics([controlUUID, dataUUID, statusUUID], for: service)
    }

    func peripheral(_ peripheral: CBPeripheral,
        didDiscoverCharacteristicsFor service: CBService, error: Error?) {
        if let error { fail("characteristic discovery failed: \(error.localizedDescription)") }
        for characteristic in service.characteristics ?? [] {
            switch characteristic.uuid {
            case controlUUID: control = characteristic
            case dataUUID: dataCharacteristic = characteristic
            case statusUUID: status = characteristic
            default: break
            }
        }
        guard control != nil, dataCharacteristic != nil, let status else {
            fail("recovery service is incomplete")
        }
        peripheral.readValue(for: status)
    }

    func peripheral(_ peripheral: CBPeripheral, didUpdateValueFor characteristic: CBCharacteristic,
        error: Error?) {
        if let error { fail("status read failed: \(error.localizedDescription)") }
        guard characteristic.uuid == statusUUID,
              let value = characteristic.value, value.count == 12 else {
            fail("recovery status has invalid length")
        }
        let bytes = [UInt8](value)
        let state = bytes[0]
        let loaderError = bytes[1]
        let received = Int(littleEndianUInt32(bytes, 4))
        let expected = Int(littleEndianUInt32(bytes, 8))
        guard loaderError == 0 else {
            fail("recovery loader reports errno \(loaderError)")
        }
        switch state {
        case 0:
            startUpload()
        case 1 where expected == image.count && received <= expected:
            sentOffset = received
            print("openR1 recovery: resuming at \(received)/\(expected) bytes")
            sendNextBlock()
        case 1:
            print("openR1 recovery: replacing incomplete image of \(expected) bytes")
            writeControl(Data([3]), operation: .abort)
        case 2 where expected == image.count && received == expected:
            print("openR1 recovery: image was already received; requesting verified boot")
            writeControl(Data([2]), operation: .finish)
        case 3:
            fail("recovery loader is in failed state")
        default:
            fail("recovery status is inconsistent")
        }
    }

    private func startUpload() {
        guard image.count <= Int(UInt32.max) else { fail("image is too large") }
        var request = Data([1])
        appendLittleEndian(UInt32(image.count), to: &request)
        sentOffset = 0
        print("openR1 recovery: starting \(image.count)-byte signed image")
        writeControl(request, operation: .start)
    }

    private func writeControl(_ value: Data, operation: PendingWrite) {
        guard let peripheral, let control else { fail("control path disappeared") }
        pending = operation
        peripheral.writeValue(value, for: control, type: .withResponse)
    }

    private func sendNextBlock() {
        guard let peripheral, let dataCharacteristic else {
            fail("data path disappeared")
        }
        if sentOffset == image.count {
            writeControl(Data([2]), operation: .finish)
            return
        }
        let maximum = max(1, peripheral.maximumWriteValueLength(for: .withResponse) - 4)
        let count = min(maximum, image.count - sentOffset)
        var packet = Data()
        appendLittleEndian(UInt32(sentOffset), to: &packet)
        packet.append(image.subdata(in: sentOffset..<(sentOffset + count)))
        pending = .data(count)
        peripheral.writeValue(packet, for: dataCharacteristic, type: .withResponse)
    }

    func peripheral(_ peripheral: CBPeripheral, didWriteValueFor characteristic: CBCharacteristic,
        error: Error?) {
        if let error { fail("recovery write failed: \(error.localizedDescription)") }
        let completed = pending
        pending = .none
        switch completed {
        case .abort:
            startUpload()
        case .start:
            sendNextBlock()
        case let .data(count):
            sentOffset += count
            if sentOffset == image.count || sentOffset % 16384 < count {
                print("openR1 recovery: uploaded \(sentOffset)/\(image.count) bytes")
            }
            sendNextBlock()
        case .finish:
            succeed()
        case .none:
            fail("unexpected write completion")
        }
    }

    private func succeed() -> Never {
        deadline?.cancel()
        print("openR1 recovery: upload accepted; MCUboot will execute only if the owner signature validates")
        exit(0)
    }

    fileprivate func fail(_ message: String) -> Never {
        deadline?.cancel()
        fputs("openR1 recovery: \(message)\n", stderr)
        exit(1)
    }
}

private let options = Options.parse()
do {
    _ = try RecoveryUploader(options: options)
    dispatchMain()
} catch {
    fputs("openR1 recovery: \(error.localizedDescription)\n", stderr)
    exit(1)
}
