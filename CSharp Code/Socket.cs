// LocalUdpClient.cs - 完整项目输出（仅发送部分）
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices
using System.Linq;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;

namespace BMSLib
{
    /// <summary>
    /// 仅限本机的UDP客户端（支持大数据分包发送）
    /// 安全特性：硬编码127.0.0.1、运行时地址验证、延迟初始化
    /// </summary>
    public static class LocalUdpClient
    {
        /* ==================== 配置常量 ==================== */
        private static readonly IPAddress AllowedAddress = IPAddress.Parse("127.0.0.1");
        private const int AllowedPort = 58764;
        private const int MaxPacketSize = 1400;  // 安全UDP包大小（留余量）
        private const int HeaderSize = 24;     // 分包协议头长度

        /* ==================== 延迟初始化 ==================== */
        private static readonly Lazy<Socket> _socket = new Lazy<Socket>(
            CreateSocket, LazyThreadSafetyMode.ExecutionAndPublication);

        private static readonly object _lock = new object();
        private static readonly System.Random _random = new System.Random();
        private static bool _preloaded = false;

        /* ==================== 初始化与清理 ==================== */
        private static Socket CreateSocket()
        {
            try
            {
                var socket = new Socket(AddressFamily.InterNetwork, SocketType.Dgram, ProtocolType.Udp)
                {
                    EnableBroadcast = false,
                    ExclusiveAddressUse = true
                };
                Console.WriteLine($"[UDP] Socket初始化成功 => {AllowedAddress}:{AllowedPort}");
                return socket;
            }
            catch (SocketException ex)
            {
                Console.WriteLine($"[UDP FATAL] Socket创建失败: {ex.SocketErrorCode} - {ex.Message}");
                throw new InvalidOperationException("UDP客户端初始化失败", ex);
            }
        }

        /// <summary>
        /// 预加载（应用启动时调用，可选）
        /// </summary>
        public static void Preload()
        {
            if (!_preloaded)
            {
                var _ = _socket.Value;
                _preloaded = true;
                Console.WriteLine("[UDP] 预加载完成");
            }
        }

        /// <summary>
        /// 清理资源（程序退出时必须调用）
        /// </summary>
        public static void Cleanup()
        {
            lock (_lock)
            {
                if (_socket.IsValueCreated)
                {
                    try
                    {
                        _socket.Value.Close();
                        Console.WriteLine("[UDP] 资源已释放");
                    }
                    catch { /* 忽略关闭异常 */ }
                }
            }
        }

        /* ==================== 核心发送逻辑 ==================== */
        /// <summary>
        /// 发送数据（自动判断是否需要分包）
        /// </summary>
        /// <param name="data">完整数据字节数组</param>
        public static void Send(byte[] data)
        {
            //ValidateInitialization();

            if (data.Length > MaxPacketSize)
            {
                // 大数据：自动分包发送
                SendLargeData(data);
            }
            else
            {
                // 小数据：直接发送
                SendRaw(data);
            }
        }

        /// <summary>
        /// 发送字符串（便捷方法）
        /// </summary>
        public static void SendString(string message)
        {
            Send(Encoding.UTF8.GetBytes(message));
        }

        /* ==================== 分包发送实现 ==================== */
        private static void SendLargeData(byte[] data)
        {
            var packets = SplitData(data);
            Console.WriteLine($"[UDP] 大数据包自动拆分: {packets.Count} 个分包");

            foreach (var packet in packets)
            {
                SendRaw(packet);
            }
        }

        private static List<byte[]> SplitData(byte[] data)
        {
            var packets = new List<byte[]>();
            int payloadSize = MaxPacketSize - HeaderSize;
            int totalPackets = (data.Length + payloadSize - 1) / payloadSize;
            ulong packetId = GeneratePacketId();

            for (int i = 0; i < totalPackets; i++)
            {
                int offset = i * payloadSize;
                int length = Math.Min(payloadSize, data.Length - offset);

                byte[] packet = new byte[HeaderSize + length];
                var header = new PacketHeader
                {
                    PacketId = packetId,
                    TotalPackets = (ushort)totalPackets,
                    PacketIndex = (ushort)i,
                    DataLength = length
                };

                // 写入协议头
                MemoryMarshal.Write(packet.AsSpan(), ref header);
                // 写入数据片段
                Buffer.BlockCopy(data, offset, packet, HeaderSize, length);

                packets.Add(packet);
            }

            return packets;
        }

        private static ulong GeneratePacketId()
        {
            long timestamp = DateTime.UtcNow.Ticks;
            int random;
            lock (_random)
            {
                random = _random.Next();
            }
            return ((ulong)(uint)timestamp << 32) | (uint)random;
        }

        /* ==================== 底层发送 ==================== */
        private static void SendRaw(byte[] data)
        {
            lock (_lock)
            {
                try
                {
                    var endPoint = new IPEndPoint(AllowedAddress, AllowedPort);
                    _socket.Value.SendTo(data, endPoint);
                }
                catch (SocketException ex)
                {
                    Console.WriteLine($"[UDP ERROR] 发送失败: {ex.Message}");
                    throw;
                }
            }
        }

        /* ==================== 安全验证 ==================== */
        //private static void ValidateInitialization()
        //{
        //	if (!_socket.IsValueCreated && !_preloaded)
        //		throw new InvalidOperationException("UDP客户端未初始化，请先调用Initialize()或Send()");
        //}

        /// <summary>
        /// 序列化并发送复杂数据（Int, Int, Int, Int, List<Long>）
        /// </summary>
        public static void SendStructuredData(int songId, int syncNumber, int maxCombo, int totalCombo, List<long> hitMap)
        {
            byte[] serialized = SerializeData(songId, syncNumber, maxCombo, totalCombo, hitMap);
            Send(serialized);
        }

        private static byte[] SerializeData(int songId, int syncNumber, int maxCombo, int totalCombo, List<long> hitMap)
        {
            using (var ms = new System.IO.MemoryStream())
            using (var writer = new System.IO.BinaryWriter(ms))
            {
                writer.Write(songId);
                writer.Write(syncNumber);
                writer.Write(maxCombo);
                writer.Write(totalCombo);
                writer.Write(hitMap?.Count ?? 0);
                foreach (long kD in hitMap ?? Enumerable.Empty<long>())
                {
                    writer.Write(kD);
                }
                return ms.ToArray();
            }
        }

        /* ==================== 分包协议头 ==================== */
        [System.Runtime.InteropServices.StructLayout(System.Runtime.InteropServices.LayoutKind.Sequential, Pack = 1)]
        private struct PacketHeader
        {
            public ulong PacketId;
            public ushort TotalPackets;
            public ushort PacketIndex;
            public int DataLength;
        }
    }
}