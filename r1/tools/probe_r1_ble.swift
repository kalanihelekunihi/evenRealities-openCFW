#!/usr/bin/env swift

import Foundation
@preconcurrency import CoreBluetooth

private struct Options {
    let match: String
    let timeout: TimeInterval
    let requestReads: Bool
    let statusCount: Int
    let statusInterval: TimeInterval
    let verboseScan: Bool
    let pairRolePhone: Bool
    let statusBurst: Bool
    let deviceInfo: Bool
    let cccdCycle: Bool
    let channel1ProbeCount: Int
    let disconnectAfter: TimeInterval?
    let advertisementSamples: Int
    let expectStatusSilence: TimeInterval?

    static func parse() -> Options {
        var match = "B56EE2"
        var timeout: TimeInterval = 30
        var requestReads = false
        var statusCount = 0
        var statusInterval: TimeInterval = 0.1
        var verboseScan = false
        var pairRolePhone = false
        var statusBurst = false
        var deviceInfo = false
        var cccdCycle = false
        var channel1ProbeCount = 0
        var disconnectAfter: TimeInterval?
        var advertisementSamples = 0
        var expectStatusSilence: TimeInterval?
        var index = 1

        while index < CommandLine.arguments.count {
            let argument = CommandLine.arguments[index]
            switch argument {
            case "--read":
                requestReads = true
            case "--verbose-scan":
                verboseScan = true
            case "--pair-role-phone":
                pairRolePhone = true
            case "--status-burst":
                statusBurst = true
            case "--device-info":
                deviceInfo = true
            case "--cccd-cycle":
                cccdCycle = true
            case "--channel1-probe-count":
                index += 1
                guard index < CommandLine.arguments.count,
                      let parsed = Int(CommandLine.arguments[index]),
                      parsed > 0, parsed <= 20 else {
                    fputs("--channel1-probe-count must be between 1 and 20\n", stderr)
                    exit(64)
                }
                channel1ProbeCount = parsed
            case "--disconnect-after-ms":
                index += 1
                guard index < CommandLine.arguments.count,
                      let parsed = TimeInterval(CommandLine.arguments[index]),
                      parsed >= 20, parsed <= 5_000 else {
                    fputs("--disconnect-after-ms must be between 20 and 5000\n", stderr)
                    exit(64)
                }
                disconnectAfter = parsed / 1_000
            case "--advertisement-samples":
                index += 1
                guard index < CommandLine.arguments.count,
                      let parsed = Int(CommandLine.arguments[index]),
                      parsed >= 2, parsed <= 100 else {
                    fputs("--advertisement-samples must be between 2 and 100\n", stderr)
                    exit(64)
                }
                advertisementSamples = parsed
            case "--expect-status-silence-ms":
                index += 1
                guard index < CommandLine.arguments.count,
                      let parsed = TimeInterval(CommandLine.arguments[index]),
                      parsed >= 500, parsed <= 10_000 else {
                    fputs("--expect-status-silence-ms must be between 500 and 10000\n", stderr)
                    exit(64)
                }
                expectStatusSilence = parsed / 1_000
            case "--status-count":
                index += 1
                guard index < CommandLine.arguments.count,
                      let parsed = Int(CommandLine.arguments[index]),
                      parsed > 0, parsed <= 100 else {
                    fputs("--status-count must be between 1 and 100\n", stderr)
                    exit(64)
                }
                statusCount = parsed
            case "--status-interval-ms":
                index += 1
                guard index < CommandLine.arguments.count,
                      let parsed = TimeInterval(CommandLine.arguments[index]),
                      parsed >= 20, parsed <= 10_000 else {
                    fputs("--status-interval-ms must be between 20 and 10000\n", stderr)
                    exit(64)
                }
                statusInterval = parsed / 1_000
            case "--timeout":
                index += 1
                guard index < CommandLine.arguments.count,
                      let parsed = TimeInterval(CommandLine.arguments[index]),
                      parsed > 0 else {
                    fputs("usage: probe_r1_ble.swift [--timeout seconds] [--read] [--verbose-scan] [--pair-role-phone] [--device-info] [--cccd-cycle] [--channel1-probe-count count] [--status-count count] [--status-interval-ms ms] [--status-burst] [--disconnect-after-ms ms] [--advertisement-samples count] [--expect-status-silence-ms ms] [name-fragment]\n", stderr)
                    exit(64)
                }
                timeout = parsed
            case "--help", "-h":
                print("usage: probe_r1_ble.swift [--timeout seconds] [--read] [--verbose-scan] [--pair-role-phone] [--device-info] [--cccd-cycle] [--channel1-probe-count count] [--status-count count] [--status-interval-ms ms] [--status-burst] [--disconnect-after-ms ms] [--advertisement-samples count] [--expect-status-silence-ms ms] [name-fragment]")
                print("  Discovery is read-only by default. --read requests values only from readable characteristics.")
                print("  --status-count sends only the non-mutating system deviceStatus query on channel 2.")
                print("  --pair-role-phone sends the recovered ephemeral pairAuth phone-role selector before status queries.")
                print("  --device-info reads only the fixed firmware and hardware version slots.")
                print("  --status-burst sends the bounded status set without waiting for each response.")
                print("  --cccd-cycle disables and re-enables only the channel-2 notification CCCD before queries.")
                print("  --channel1-probe-count interleaves bounded non-mutating opcode-0x89 frames with a channel-2 burst.")
                print("  --disconnect-after-ms intentionally disconnects during a status burst.")
                print("  --advertisement-samples measures target advertisements without connecting.")
                print("  --expect-status-silence-ms verifies that a status query receives no reply without pairAuth.")
                exit(0)
            default:
                match = argument
            }
            index += 1
        }

        if disconnectAfter != nil && (!statusBurst || statusCount == 0) {
            fputs("--disconnect-after-ms requires --status-burst and --status-count\n", stderr)
            exit(64)
        }
        if advertisementSamples > 0 &&
            (requestReads || pairRolePhone || deviceInfo || cccdCycle ||
             channel1ProbeCount > 0 || statusCount > 0) {
            fputs("--advertisement-samples cannot be combined with connection operations\n", stderr)
            exit(64)
        }
        if expectStatusSilence != nil &&
            (statusCount != 1 || pairRolePhone || statusBurst || disconnectAfter != nil) {
            fputs("--expect-status-silence-ms requires exactly --status-count 1 without pair role or burst\n", stderr)
            exit(64)
        }
        if channel1ProbeCount > 0 &&
            (!pairRolePhone || !statusBurst || statusCount == 0 ||
             disconnectAfter != nil || cccdCycle) {
            fputs("--channel1-probe-count requires --pair-role-phone, --status-burst, and --status-count; it cannot be combined with disconnect or CCCD cycling\n", stderr)
            exit(64)
        }

        return Options(
            match: match,
            timeout: timeout,
            requestReads: requestReads,
            statusCount: statusCount,
            statusInterval: statusInterval,
            verboseScan: verboseScan,
            pairRolePhone: pairRolePhone,
            statusBurst: statusBurst,
            deviceInfo: deviceInfo,
            cccdCycle: cccdCycle,
            channel1ProbeCount: channel1ProbeCount,
            disconnectAfter: disconnectAfter,
            advertisementSamples: advertisementSamples,
            expectStatusSilence: expectStatusSilence)
    }
}

private func hex(_ data: Data) -> String {
    data.map { String(format: "%02X", $0) }.joined()
}

private func crc16CCITTUpdate(_ initial: UInt16, _ bytes: [UInt8]) -> UInt16 {
    var crc = initial
    for byte in bytes {
        crc = (crc >> 8) | (crc << 8)
        crc ^= UInt16(byte)
        crc ^= (crc & 0x00ff) >> 4
        crc ^= crc << 12
        crc ^= (crc & 0x00ff) << 5
    }
    return crc
}

private func crc16CCITT(_ bytes: [UInt8]) -> UInt16 {
    crc16CCITTUpdate(UInt16.max, bytes)
}

private func crc16MODBUSModel(_ bytes: [UInt8]) -> UInt16 {
    var crc = UInt16.max
    for (index, original) in bytes.enumerated() {
        let byte: UInt8 = (index == 10 || index == 11) ? 0 : original
        crc ^= UInt16(byte)
        for _ in 0..<8 {
            crc = (crc & 1) != 0 ? (crc >> 1) ^ 0xa001 : crc >> 1
        }
    }
    return crc
}

private func crc32Castagnoli(_ bytes: [UInt8]) -> UInt32 {
    var crc: UInt32 = 0
    for byte in bytes {
        crc ^= UInt32(byte) << 24
        for _ in 0..<8 {
            crc = (crc & 0x80000000) != 0
                ? (crc << 1) ^ 0x1edc6f41
                : crc << 1
        }
    }
    return crc
}

private func littleEndianUInt16(_ bytes: [UInt8], _ offset: Int) -> UInt16 {
    UInt16(bytes[offset]) | (UInt16(bytes[offset + 1]) << 8)
}

private func littleEndianUInt32(_ bytes: [UInt8], _ offset: Int) -> UInt32 {
    UInt32(bytes[offset]) |
        (UInt32(bytes[offset + 1]) << 8) |
        (UInt32(bytes[offset + 2]) << 16) |
        (UInt32(bytes[offset + 3]) << 24)
}

private func systemRequest(serial: UInt16, subcommand: UInt8, payload: [UInt8]) -> Data {
    let length = 12 + payload.count
    var model: [UInt8] = [
        100, 1, 100,
        UInt8(truncatingIfNeeded: serial), UInt8(truncatingIfNeeded: serial >> 8),
        0, 0, subcommand,
        UInt8(truncatingIfNeeded: length), UInt8(truncatingIfNeeded: length >> 8),
        0, 0,
    ] + payload
    let compact = [
        model[0], model[1], model[2], model[3], model[5],
        model[6], model[7], model[8], UInt8(0),
    ]
    let innerCRC = crc16CCITTUpdate(crc16CCITT(compact), payload)
    model[10] = UInt8(truncatingIfNeeded: innerCRC)
    model[11] = UInt8(truncatingIfNeeded: innerCRC >> 8)
    let outerCRC = crc32Castagnoli(model)
    return Data([
        0,
        UInt8(truncatingIfNeeded: outerCRC),
        UInt8(truncatingIfNeeded: outerCRC >> 8),
        UInt8(truncatingIfNeeded: outerCRC >> 16),
        UInt8(truncatingIfNeeded: outerCRC >> 24),
    ] + model)
}

private func deviceStatusRequest(serial: UInt16) -> Data {
    systemRequest(serial: serial, subcommand: 1, payload: [])
}

private func pairRolePhoneRequest() -> Data {
    systemRequest(serial: 0x3f00, subcommand: 8, payload: [1])
}

private func deviceInfoRequest() -> Data {
    systemRequest(serial: 0x3f01, subcommand: 2, payload: [])
}

private func channel1NonmutatingRequest() -> Data {
    /* Opcode 0x89 reads byte 3 as command-valid. Zero keeps every recovered
     * wear/secondary/touch/regulator/radio transition disabled. */
    Data([0, 0, 0x89, 0, 0, 0, 0])
}

private func channel1NonmutatingResponse() -> Data {
    /* The bounded handler acknowledges by setting workspace byte 4 to one. */
    Data([0, 0, 0x89, 0, 1, 0, 0])
}

private func propertyNames(_ properties: CBCharacteristicProperties) -> String {
    let known: [(CBCharacteristicProperties, String)] = [
        (.broadcast, "broadcast"),
        (.read, "read"),
        (.writeWithoutResponse, "write-without-response"),
        (.write, "write"),
        (.notify, "notify"),
        (.indicate, "indicate"),
        (.authenticatedSignedWrites, "authenticated-signed-writes"),
        (.extendedProperties, "extended-properties"),
        (.notifyEncryptionRequired, "notify-encryption-required"),
        (.indicateEncryptionRequired, "indicate-encryption-required"),
    ]
    let names = known.compactMap { properties.contains($0.0) ? $0.1 : nil }
    return names.isEmpty ? "none" : names.joined(separator: ",")
}

private final class Probe: NSObject, CBCentralManagerDelegate, CBPeripheralDelegate {
    private let options: Options
    private var central: CBCentralManager!
    private var target: CBPeripheral?
    private var pendingServices = Set<CBUUID>()
    private var pendingCharacteristics = Set<String>()
    private var pendingDescriptors = Set<String>()
    private var pendingReads = Set<String>()
    private var channel1RX: CBCharacteristic?
    private var channel1TX: CBCharacteristic?
    private var channel2RX: CBCharacteristic?
    private var channel2TX: CBCharacteristic?
    private var statusStarted = false
    private var statusSent = 0
    private var statusReceived = 0
    private var channel1Sent = 0
    private var channel1Received = 0
    private var channel1RequestTimes: [TimeInterval] = []
    private var channel1LatenciesMilliseconds: [Double] = []
    private var interleavedCompletionScheduled = false
    private var requestTimes: [UInt16: TimeInterval] = [:]
    private var latenciesMilliseconds: [Double] = []
    private var pairRequestTime: TimeInterval?
    private var deviceInfoRequestTime: TimeInterval?
    private var deviceInfoReceived = false
    private var cccdCycleStage = 0
    private var intentionalDisconnect = false
    private var advertisementTimes: [TimeInterval] = []
    private let startedAt = ProcessInfo.processInfo.systemUptime
    private var deadline: Timer?
    private var finished = false

    init(options: Options) {
        self.options = options
        super.init()
        central = CBCentralManager(delegate: self, queue: .main)
        deadline = Timer.scheduledTimer(withTimeInterval: options.timeout, repeats: false) { [weak self] _ in
            self?.finish(code: 2, reason: "timeout")
        }
    }

    func centralManagerDidUpdateState(_ central: CBCentralManager) {
        guard central.state == .poweredOn else {
            if central.state == .unsupported || central.state == .unauthorized || central.state == .poweredOff {
                finish(code: 3, reason: "Bluetooth unavailable: \(central.state.rawValue)")
            }
            return
        }

        let connectedServices = [
            CBUUID(string: "BAE80001-4F05-4503-8E65-3AF1F7329D1F"),
            CBUUID(string: "FE59"),
        ]
        let connected = central.retrieveConnectedPeripherals(withServices: connectedServices)
        for peripheral in connected {
            print(
                "CONNECTED-CANDIDATE id=\(peripheral.identifier.uuidString)" +
                " name=\(peripheral.name ?? "-") state=\(peripheral.state.rawValue)")
        }
        if let peripheral = connected.first(where: {
            $0.name?.localizedCaseInsensitiveContains(options.match) == true
        }) {
            target = peripheral
            peripheral.delegate = self
            print(
                "MATCH id=\(peripheral.identifier.uuidString)" +
                " name=\(peripheral.name ?? "-") alreadyConnected=true")
            peripheral.discoverServices(nil)
            return
        }

        print("SCAN match=\(options.match) timeout=\(Int(options.timeout))s")
        central.scanForPeripherals(withServices: nil, options: [CBCentralManagerScanOptionAllowDuplicatesKey: true])
    }

    func centralManager(
        _ central: CBCentralManager,
        didDiscover peripheral: CBPeripheral,
        advertisementData: [String: Any],
        rssi RSSI: NSNumber
    ) {
        let localName = advertisementData[CBAdvertisementDataLocalNameKey] as? String
        let peripheralName = peripheral.name
        let serviceUUIDs = (advertisementData[CBAdvertisementDataServiceUUIDsKey] as? [CBUUID]) ?? []
        let manufacturerData = advertisementData[CBAdvertisementDataManufacturerDataKey] as? Data
        let connectable = advertisementData[CBAdvertisementDataIsConnectable] as? NSNumber
        let names = [localName, peripheralName].compactMap { $0 }
        let isMatch = names.contains {
            $0.localizedCaseInsensitiveContains(options.match)
        }

        guard options.verboseScan || isMatch else { return }

        let advertisedServices = serviceUUIDs.map { $0.uuidString }.joined(separator: ",")
        let manufacturerCompany = manufacturerData.flatMap { data -> String? in
            guard data.count >= 2 else { return nil }
            return String(format: "%02X%02X", data[1], data[0])
        } ?? "-"
        let advertisement = [
            "ADVERTISEMENT id=\(peripheral.identifier.uuidString)",
            "localName=\(localName ?? "-")",
            "peripheralName=\(peripheralName ?? "-")",
            "rssi=\(RSSI)",
            "connectable=\(connectable?.stringValue ?? "-")",
            "services=\(advertisedServices)",
            "manufacturerCompany=\(manufacturerCompany)",
            "manufacturerLength=\(manufacturerData?.count ?? 0)",
        ].joined(separator: " ")
        print(advertisement)

        if isMatch && options.advertisementSamples > 0 {
            let observedAt = ProcessInfo.processInfo.systemUptime
            if let previous = advertisementTimes.last,
               observedAt - previous < 0.1 {
                print("ADVERTISEMENT-COALESCED scanResponsePair=true")
                return
            }
            advertisementTimes.append(observedAt)
            if advertisementTimes.count == options.advertisementSamples {
                let intervals = zip(
                    advertisementTimes.dropFirst(), advertisementTimes
                ).map { ($0.0 - $0.1) * 1_000 }
                let minimum = intervals.min() ?? 0
                let maximum = intervals.max() ?? 0
                let mean = intervals.reduce(0, +) / Double(intervals.count)
                print(String(
                    format: "ADVERTISEMENT-SUMMARY samples=%d intervals=%d minMs=%.3f meanMs=%.3f maxMs=%.3f",
                    advertisementTimes.count, intervals.count,
                    minimum, mean, maximum))
                finish(code: 0, reason: "advertisement sampling complete")
            }
            return
        }

        guard target == nil, isMatch else {
            return
        }

        target = peripheral
        peripheral.delegate = self
        central.stopScan()
        print("MATCH id=\(peripheral.identifier.uuidString) name=\(names.first ?? "-")")
        central.connect(peripheral, options: nil)
    }

    func centralManager(_ central: CBCentralManager, didConnect peripheral: CBPeripheral) {
        print("CONNECTED id=\(peripheral.identifier.uuidString) elapsedMs=\(elapsedMilliseconds())")
        print(
            "WRITE-LIMITS withResponse=\(peripheral.maximumWriteValueLength(for: .withResponse))" +
            " withoutResponse=\(peripheral.maximumWriteValueLength(for: .withoutResponse))")
        peripheral.discoverServices(nil)
    }

    func centralManager(_ central: CBCentralManager, didFailToConnect peripheral: CBPeripheral, error: Error?) {
        finish(code: 4, reason: "connect failed: \(error?.localizedDescription ?? "unknown")")
    }

    func centralManager(_ central: CBCentralManager, didDisconnectPeripheral peripheral: CBPeripheral, error: Error?) {
        guard !finished else { return }
        if intentionalDisconnect {
            printStatusSummary()
            finish(code: 0, reason: "intentional disconnect-under-load complete")
            return
        }
        finish(code: 5, reason: "disconnected: \(error?.localizedDescription ?? "peer closed connection")")
    }

    func peripheral(_ peripheral: CBPeripheral, didDiscoverServices error: Error?) {
        if let error {
            finish(code: 6, reason: "service discovery failed: \(error.localizedDescription)")
            return
        }

        let services = peripheral.services ?? []
        pendingServices = Set(services.map { $0.uuid })
        print("SERVICES count=\(services.count)")
        if services.isEmpty {
            finish(code: 0, reason: "discovery complete")
            return
        }
        for service in services {
            print("SERVICE uuid=\(service.uuid.uuidString) primary=\(service.isPrimary)")
            peripheral.discoverCharacteristics(nil, for: service)
        }
    }

    func peripheral(_ peripheral: CBPeripheral, didDiscoverCharacteristicsFor service: CBService, error: Error?) {
        pendingServices.remove(service.uuid)
        if let error {
            print("CHARACTERISTICS-ERROR service=\(service.uuid.uuidString) error=\(error.localizedDescription)")
            checkCompletion()
            return
        }

        for characteristic in service.characteristics ?? [] {
            let key = characteristicKey(service: service, characteristic: characteristic)
            pendingCharacteristics.insert(key)
            print(
                "CHARACTERISTIC service=\(service.uuid.uuidString)" +
                " uuid=\(characteristic.uuid.uuidString)" +
                " properties=\(propertyNames(characteristic.properties))"
            )
            if characteristic.uuid.uuidString.caseInsensitiveCompare(
                "BAE80010-4F05-4503-8E65-3AF1F7329D1F") == .orderedSame {
                channel1RX = characteristic
            }
            if characteristic.uuid.uuidString.caseInsensitiveCompare(
                "BAE80011-4F05-4503-8E65-3AF1F7329D1F") == .orderedSame {
                channel1TX = characteristic
            }
            if characteristic.uuid.uuidString.caseInsensitiveCompare(
                "BAE80012-4F05-4503-8E65-3AF1F7329D1F") == .orderedSame {
                channel2RX = characteristic
            }
            if characteristic.uuid.uuidString.caseInsensitiveCompare(
                "BAE80013-4F05-4503-8E65-3AF1F7329D1F") == .orderedSame {
                channel2TX = characteristic
            }
            peripheral.discoverDescriptors(for: characteristic)
            if options.requestReads && characteristic.properties.contains(.read) {
                pendingReads.insert(key)
                print("READ-REQUEST service=\(service.uuid.uuidString) uuid=\(characteristic.uuid.uuidString)")
                peripheral.readValue(for: characteristic)
            }
        }
        checkCompletion()
    }

    func peripheral(_ peripheral: CBPeripheral, didDiscoverDescriptorsFor characteristic: CBCharacteristic, error: Error?) {
        guard let service = characteristic.service else { return }
        let key = characteristicKey(service: service, characteristic: characteristic)
        pendingCharacteristics.remove(key)
        if let error {
            print("DESCRIPTORS-ERROR characteristic=\(characteristic.uuid.uuidString) error=\(error.localizedDescription)")
        } else {
            let descriptors = characteristic.descriptors ?? []
            print("DESCRIPTORS characteristic=\(characteristic.uuid.uuidString) count=\(descriptors.count)")
            for descriptor in descriptors {
                let descriptorKey = "\(key)/\(descriptor.uuid.uuidString)"
                pendingDescriptors.insert(descriptorKey)
                peripheral.readValue(for: descriptor)
            }
        }
        checkCompletion()
    }

    func peripheral(_ peripheral: CBPeripheral, didUpdateValueFor descriptor: CBDescriptor, error: Error?) {
        guard let characteristic = descriptor.characteristic,
              let service = characteristic.service else { return }
        let key = "\(characteristicKey(service: service, characteristic: characteristic))/\(descriptor.uuid.uuidString)"
        pendingDescriptors.remove(key)
        print(
            "DESCRIPTOR characteristic=\(characteristic.uuid.uuidString)" +
            " uuid=\(descriptor.uuid.uuidString)" +
            " status=\(error == nil ? "ok" : "error")"
        )
        checkCompletion()
    }

    func peripheral(_ peripheral: CBPeripheral, didUpdateValueFor characteristic: CBCharacteristic, error: Error?) {
        guard let service = characteristic.service else { return }
        if options.channel1ProbeCount > 0,
           characteristic === channel1TX,
           let value = characteristic.value {
            handleChannel1Response(value, error: error)
            return
        }
        if (options.statusCount > 0 || options.pairRolePhone || options.deviceInfo),
           characteristic === channel2TX,
           let value = characteristic.value {
            handleStatusResponse(Array(value), error: error)
            return
        }
        pendingReads.remove(characteristicKey(service: service, characteristic: characteristic))
        print(
            "READ-RESULT service=\(service.uuid.uuidString)" +
            " uuid=\(characteristic.uuid.uuidString)" +
            " status=\(error == nil ? "ok" : "error")" +
            " length=\(characteristic.value?.count ?? 0)" +
            (error.map { " error=\($0.localizedDescription)" } ?? "")
        )
        checkCompletion()
    }

    func peripheral(
        _ peripheral: CBPeripheral,
        didUpdateNotificationStateFor characteristic: CBCharacteristic,
        error: Error?
    ) {
        if characteristic === channel1TX {
            if let error {
                finish(code: 7, reason: "channel-1 notification setup failed: \(error.localizedDescription)")
                return
            }
            print("CHANNEL1-NOTIFY enabled=\(characteristic.isNotifying) elapsedMs=\(elapsedMilliseconds())")
            guard characteristic.isNotifying, let channel2TX else {
                finish(code: 7, reason: "channel-1 notifications are disabled")
                return
            }
            peripheral.setNotifyValue(true, for: channel2TX)
            return
        }
        guard characteristic === channel2TX else { return }
        if let error {
            finish(code: 7, reason: "channel-2 notification setup failed: \(error.localizedDescription)")
            return
        }
        print("CHANNEL2-NOTIFY enabled=\(characteristic.isNotifying) elapsedMs=\(elapsedMilliseconds())")
        if options.cccdCycle && cccdCycleStage == 0 && characteristic.isNotifying {
            cccdCycleStage = 1
            print("CHANNEL2-CCCD-CYCLE action=disable")
            peripheral.setNotifyValue(false, for: characteristic)
            return
        }
        if options.cccdCycle && cccdCycleStage == 1 && !characteristic.isNotifying {
            cccdCycleStage = 2
            print("CHANNEL2-CCCD-CYCLE disabled=true")
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.25) { [weak self] in
                guard let self, let target = self.target,
                      let channel2TX = self.channel2TX else { return }
                print("CHANNEL2-CCCD-CYCLE action=enable")
                target.setNotifyValue(true, for: channel2TX)
            }
            return
        }
        if options.cccdCycle && cccdCycleStage == 2 && characteristic.isNotifying {
            cccdCycleStage = 3
            print("CHANNEL2-CCCD-CYCLE reenabled=true")
        }
        guard characteristic.isNotifying else {
            finish(code: 7, reason: "channel-2 notifications are disabled")
            return
        }
        if options.pairRolePhone {
            sendPairRolePhoneRequest()
        } else {
            startPostPairOperations()
        }
    }

    private func characteristicKey(service: CBService, characteristic: CBCharacteristic) -> String {
        "\(service.uuid.uuidString)/\(characteristic.uuid.uuidString)"
    }

    private func checkCompletion() {
        guard pendingServices.isEmpty,
              pendingCharacteristics.isEmpty,
              pendingDescriptors.isEmpty,
              pendingReads.isEmpty,
              target?.services != nil else { return }
        if options.statusCount > 0 || options.pairRolePhone || options.deviceInfo ||
           options.channel1ProbeCount > 0 {
            beginStatusQueries()
        } else {
            finish(code: 0, reason: "discovery complete")
        }
    }

    private func beginStatusQueries() {
        guard !statusStarted else { return }
        statusStarted = true
        guard let channel2RX, let channel2TX else {
            finish(code: 7, reason: "channel-2 characteristics unavailable")
            return
        }
        guard channel2RX.properties.contains(.writeWithoutResponse),
              channel2TX.properties.contains(.notify) else {
            finish(code: 7, reason: "channel-2 properties do not match the analyzed contract")
            return
        }
        if options.channel1ProbeCount > 0 {
            guard let channel1RX, let channel1TX,
                  channel1RX.properties.contains(.writeWithoutResponse),
                  channel1TX.properties.contains(.notify) else {
                finish(code: 7, reason: "channel-1 properties do not match the analyzed contract")
                return
            }
        }
        print(
            "CHANNEL2-PLAN pairRolePhone=\(options.pairRolePhone)" +
            " deviceInfo=\(options.deviceInfo)" +
            " statusCount=\(options.statusCount)" +
            " channel1ProbeCount=\(options.channel1ProbeCount)" +
            " intervalMs=\(Int(options.statusInterval * 1000))" +
            " burst=\(options.statusBurst)" +
            " cccdCycle=\(options.cccdCycle)" +
            " disconnectAfterMs=\(options.disconnectAfter.map { Int($0 * 1000) } ?? 0)")
        if options.channel1ProbeCount > 0, let channel1TX {
            target?.setNotifyValue(true, for: channel1TX)
        } else {
            target?.setNotifyValue(true, for: channel2TX)
        }
    }

    private func sendPairRolePhoneRequest() {
        guard let target, let channel2RX else { return }
        let value = pairRolePhoneRequest()
        pairRequestTime = ProcessInfo.processInfo.systemUptime
        print("PAIR-ROLE-REQUEST serial=16128 bytes=\(value.count)")
        target.writeValue(value, for: channel2RX, type: .withoutResponse)
    }

    private func sendDeviceInfoRequest() {
        guard let target, let channel2RX else { return }
        let value = deviceInfoRequest()
        deviceInfoRequestTime = ProcessInfo.processInfo.systemUptime
        print("DEVICE-INFO-REQUEST serial=16129 bytes=\(value.count)")
        target.writeValue(value, for: channel2RX, type: .withoutResponse)
    }

    private func startPostPairOperations() {
        if options.deviceInfo && !deviceInfoReceived {
            sendDeviceInfoRequest()
        } else if options.statusCount > 0 {
            startStatusQueries()
        } else {
            finish(code: 0, reason: "requested channel-2 operations complete")
        }
    }

    private func sendNextStatusRequest() {
        guard let target, let channel2RX, statusSent < options.statusCount else { return }
        let serial = UInt16(0x4000 + statusSent)
        let value = deviceStatusRequest(serial: serial)
        requestTimes[serial] = ProcessInfo.processInfo.systemUptime
        statusSent += 1
        print("STATUS-REQUEST serial=\(serial) bytes=\(value.count)")
        target.writeValue(value, for: channel2RX, type: .withoutResponse)
        if let silence = options.expectStatusSilence {
            DispatchQueue.main.asyncAfter(deadline: .now() + silence) { [weak self] in
                guard let self, !self.finished,
                      self.requestTimes.removeValue(forKey: serial) != nil else { return }
                print("STATUS-SILENCE verifiedMs=\(Int(silence * 1000)) serial=\(serial)")
                self.finish(code: 0, reason: "status remained silent without pair-role selection")
            }
        }
    }

    private func sendNextChannel1Probe() {
        guard let target, let channel1RX,
              channel1Sent < options.channel1ProbeCount else { return }
        let value = channel1NonmutatingRequest()
        channel1RequestTimes.append(ProcessInfo.processInfo.systemUptime)
        channel1Sent += 1
        print("CHANNEL1-PROBE-REQUEST index=\(channel1Sent) bytes=\(value.count) commandValid=false")
        target.writeValue(value, for: channel1RX, type: .withoutResponse)
    }

    private func startStatusQueries() {
        if options.statusBurst {
            while statusSent < options.statusCount ||
                  channel1Sent < options.channel1ProbeCount {
                if statusSent < options.statusCount {
                    sendNextStatusRequest()
                }
                if channel1Sent < options.channel1ProbeCount {
                    sendNextChannel1Probe()
                }
            }
            if let disconnectAfter = options.disconnectAfter {
                DispatchQueue.main.asyncAfter(deadline: .now() + disconnectAfter) { [weak self] in
                    guard let self, !self.finished, let target = self.target else { return }
                    self.intentionalDisconnect = true
                    print("DISCONNECT-UNDER-LOAD requested=true sent=\(self.statusSent) received=\(self.statusReceived)")
                    self.central.cancelPeripheralConnection(target)
                }
            }
            DispatchQueue.main.asyncAfter(deadline: .now() + 10.0) { [weak self] in
                guard let self, !self.finished,
                      self.statusReceived < self.options.statusCount else { return }
                self.printStatusSummary()
                self.printChannel1Summary()
                self.finish(code: 9, reason: "interleaved channel-2 responses incomplete")
            }
        } else {
            sendNextStatusRequest()
        }
    }

    private func handleChannel1Response(_ value: Data, error: Error?) {
        if let error {
            finish(code: 8, reason: "channel-1 response failed: \(error.localizedDescription)")
            return
        }
        guard value == channel1NonmutatingResponse(),
              !channel1RequestTimes.isEmpty else {
            print("UNMATCHED-CHANNEL1-FRAME bytes=\(value.count) hex=\(hex(value))")
            return
        }
        let requestTime = channel1RequestTimes.removeFirst()
        let latency = (ProcessInfo.processInfo.systemUptime - requestTime) * 1_000
        channel1LatenciesMilliseconds.append(latency)
        channel1Received += 1
        print(String(
            format: "CHANNEL1-PROBE-RESPONSE index=%d bytes=%d latencyMs=%.3f",
            channel1Received, value.count, latency))
    }

    private func checkInterleavedCompletion() {
        guard statusReceived == options.statusCount else { return }
        if options.channel1ProbeCount == 0 {
            printStatusSummary()
            finish(code: 0, reason: "channel-2 status queries complete")
            return
        }
        guard !interleavedCompletionScheduled else { return }
        interleavedCompletionScheduled = true
        /* Phone-role sessions may not receive channel-1 replies, which stock
         * routes toward the glasses role. Keep a bounded observation window
         * without selecting the documented fatal-risk glasses-role path. */
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) { [weak self] in
            guard let self, !self.finished else { return }
            self.printStatusSummary()
            self.printChannel1Summary()
            self.finish(code: 0, reason: "interleaved BAE8 channel writes and status queries complete")
        }
    }

    private func handleStatusResponse(_ fragment: [UInt8], error: Error?) {
        if let error {
            finish(code: 8, reason: "channel-2 response failed: \(error.localizedDescription)")
            return
        }
        guard fragment.count >= 17, fragment[0] == 0 else {
            finish(code: 8, reason: "unexpected or multipart status fragment")
            return
        }
        let outerObserved = littleEndianUInt32(fragment, 1)
        let model = Array(fragment.dropFirst(5))
        guard crc32Castagnoli(model) == outerObserved,
              model.count >= 12,
              Int(littleEndianUInt16(model, 8)) == model.count,
              crc16MODBUSModel(model) == littleEndianUInt16(model, 10) else {
            finish(code: 8, reason: "status response checksum or length mismatch")
            return
        }
        let serial = littleEndianUInt16(model, 3)
        guard model[0] == 100, model[1] == 1, model[6] == 0 else {
            finish(code: 8, reason: "system response header mismatch")
            return
        }
        let resultCode = model[5] >> 2
        if serial == 0x3f00 && model[7] == 8,
           let requestTime = pairRequestTime {
            let latency = (ProcessInfo.processInfo.systemUptime - requestTime) * 1_000
            let payload = Array(model.dropFirst(12))
            guard resultCode == 0, payload == [0] else {
                finish(code: 8, reason: "pair-role response refused or malformed")
                return
            }
            pairRequestTime = nil
            print(String(format: "PAIR-ROLE-RESPONSE result=%u latencyMs=%.3f", resultCode, latency))
            if options.statusCount == 0 && !options.deviceInfo {
                startPostPairOperations()
            } else {
                DispatchQueue.main.asyncAfter(deadline: .now() + 2.0) { [weak self] in
                    self?.startPostPairOperations()
                }
            }
            return
        }
        if serial == 0x3f01 && model[7] == 2,
           let requestTime = deviceInfoRequestTime {
            let latency = (ProcessInfo.processInfo.systemUptime - requestTime) * 1_000
            let payload = Array(model.dropFirst(12))
            guard resultCode == 0, payload.count == 32 else {
                finish(code: 8, reason: "device-info response refused or malformed")
                return
            }
            let application = printableVersion(Array(payload[0..<16]))
            let hardware = printableVersion(Array(payload[16..<32]))
            deviceInfoRequestTime = nil
            deviceInfoReceived = true
            print(String(
                format: "DEVICE-INFO-RESPONSE result=%u application=%@ hardware=%@ latencyMs=%.3f",
                resultCode, application, hardware, latency))
            startPostPairOperations()
            return
        }
        guard model[7] == 1,
              let requestTime = requestTimes.removeValue(forKey: serial) else {
            print(
                "UNMATCHED-SYSTEM-MODEL serial=\(serial)" +
                " status=\(model[5]) command=\(model[6])" +
                " subcommand=\(model[7]) payloadBytes=\(model.count - 12)")
            return
        }
        let latency = (ProcessInfo.processInfo.systemUptime - requestTime) * 1_000
        if options.expectStatusSilence != nil {
            print(String(
                format: "STATUS-SILENCE-FAILED serial=%u latencyMs=%.3f",
                serial, latency))
            finish(code: 10, reason: "status replied without pair-role selection")
            return
        }
        latenciesMilliseconds.append(latency)
        statusReceived += 1
        let payloadLength = model.count - 12
        print(String(
            format: "STATUS-RESPONSE serial=%u result=%u payloadBytes=%d latencyMs=%.3f",
            serial, resultCode, payloadLength, latency))

        if statusReceived == options.statusCount {
            checkInterleavedCompletion()
            return
        }
        if !options.statusBurst {
            DispatchQueue.main.asyncAfter(deadline: .now() + options.statusInterval) { [weak self] in
                self?.sendNextStatusRequest()
            }
        }
    }

    private func printStatusSummary() {
        let minimum = latenciesMilliseconds.min() ?? 0
        let maximum = latenciesMilliseconds.max() ?? 0
        let mean = latenciesMilliseconds.isEmpty
            ? 0
            : latenciesMilliseconds.reduce(0, +) / Double(latenciesMilliseconds.count)
        print(String(
            format: "STATUS-SUMMARY sent=%d received=%d dropped=%d minMs=%.3f meanMs=%.3f maxMs=%.3f",
            statusSent, statusReceived, statusSent - statusReceived,
            minimum, mean, maximum))
    }

    private func printChannel1Summary() {
        guard options.channel1ProbeCount > 0 else { return }
        let minimum = channel1LatenciesMilliseconds.min() ?? 0
        let maximum = channel1LatenciesMilliseconds.max() ?? 0
        let mean = channel1LatenciesMilliseconds.isEmpty
            ? 0
            : channel1LatenciesMilliseconds.reduce(0, +) /
              Double(channel1LatenciesMilliseconds.count)
        print(String(
            format: "CHANNEL1-SUMMARY sent=%d observedResponses=%d noObservedResponse=%d minMs=%.3f meanMs=%.3f maxMs=%.3f",
            channel1Sent, channel1Received, channel1Sent - channel1Received,
            minimum, mean, maximum))
    }

    private func printableVersion(_ bytes: [UInt8]) -> String {
        let significant = bytes.prefix { $0 != 0 && $0 != 0xff }
        return significant.map { byte in
            byte >= 0x20 && byte <= 0x7e
                ? Character(UnicodeScalar(byte))
                : "?"
        }.reduce(into: "") { $0.append($1) }
    }

    private func elapsedMilliseconds() -> String {
        String(format: "%.3f", (ProcessInfo.processInfo.systemUptime - startedAt) * 1_000)
    }

    private func finish(code: Int32, reason: String) {
        guard !finished else { return }
        finished = true
        deadline?.invalidate()
        central?.stopScan()
        if let target, target.state == .connected {
            central?.cancelPeripheralConnection(target)
        }
        print("RESULT code=\(code) reason=\(reason)")
        fflush(stdout)
        exit(code)
    }
}

private let options = Options.parse()
private let expectedPairRoleFrame = "001D47CA7B640164003F0000080D005EB901"
private let expectedDeviceInfoFrame = "0073A36B7B640164013F0000020C001A27"
private let expectedStatusFrame = "005C2C5C6364016400400000010C00EA3B"
private let expectedChannel1NonmutatingFrame = "00008900000000"
guard hex(pairRolePhoneRequest()) == expectedPairRoleFrame,
      hex(deviceInfoRequest()) == expectedDeviceInfoFrame,
      hex(deviceStatusRequest(serial: 0x4000)) == expectedStatusFrame,
      hex(channel1NonmutatingRequest()) == expectedChannel1NonmutatingFrame else {
    fputs("internal frame self-test disagrees with the C encoder\n", stderr)
    exit(70)
}
print("FRAME-SELFTEST cEncoderVectors=ok")
private let probe = Probe(options: options)
withExtendedLifetime(probe) {
    RunLoop.main.run()
}
