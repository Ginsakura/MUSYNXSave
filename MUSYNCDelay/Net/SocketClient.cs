using System;
using System.Collections.Generic;
using System.IO;
using System.Net.Sockets;
using System.Text;
using MUSYNCDelay.Config;
using MUSYNCDelay.Data;
using MUSYNCDelay.Patches;

namespace MUSYNCDelay.Net
{
    /// <summary>
    /// 8.1-8.4 Socket 客户端 — 后台线程执行，短连接模型
    /// 帧格式: [4 字节大端长度][payload]
    /// </summary>
    public static class SocketClient
    {
        private static volatile bool _shutdownRequested;

        public static void Shutdown()
        {
            _shutdownRequested = true;
        }

        /// <summary>
        /// 后台线程调用：序列化 snapshot → Connect → Send → Recv → 反序列化
        /// 返回 null 表示连接失败或超时
        /// </summary>
        public static SettleResult SendSettle(SettleSnapshot snapshot)
        {
            if (_shutdownRequested) return null;

            var cfg = Plugin.Config.network;
            string json = BuildSettleJson(snapshot);
            byte[] payload = Encoding.UTF8.GetBytes(json);

            try
            {
                using (var client = new TcpClient())
                {
                    // 8.3 Connect refused = 瞬时失败
                    client.Connect(cfg.host, cfg.port);
                    client.ReceiveTimeout = cfg.read_timeout_ms;
                    client.SendTimeout = cfg.read_timeout_ms;

                    var stream = client.GetStream();

                    // 8.1 发送帧: [4 字节大端长度][payload]
                    WriteFrame(stream, payload);

                    // 接收响应帧
                    byte[] respPayload = ReadFrame(stream);
                    if (respPayload == null) return null;

                    // 反序列化响应
                    return ParseResult(respPayload);
                }
            }
            catch (SocketException)
            {
                // Connect refused 或超时 — Python 未启动
                return null;
            }
            catch (Exception ex)
            {
                Plugin.Logger?.LogWarning($"SocketClient error: {ex.Message}");
                return null;
            }
        }

        // ---- 帧协议 ----

        private static void WriteFrame(NetworkStream stream, byte[] payload)
        {
            var header = new byte[4];
            int len = payload.Length;
            header[0] = (byte)(len >> 24);
            header[1] = (byte)(len >> 16);
            header[2] = (byte)(len >> 8);
            header[3] = (byte)(len);
            stream.Write(header, 0, 4);
            stream.Write(payload, 0, payload.Length);
        }

        private static byte[] ReadFrame(NetworkStream stream)
        {
            var header = new byte[4];
            if (!ReadExact(stream, header, 4)) return null;
            int len = (header[0] << 24) | (header[1] << 16) | (header[2] << 8) | header[3];
            if (len <= 0 || len > 10 * 1024 * 1024) return null; // 安全上限 10MB
            var buf = new byte[len];
            if (!ReadExact(stream, buf, len)) return null;
            return buf;
        }

        private static bool ReadExact(NetworkStream stream, byte[] buf, int count)
        {
            int offset = 0;
            while (offset < count)
            {
                int n = stream.Read(buf, offset, count - offset);
                if (n <= 0) return false;
                offset += n;
            }
            return true;
        }

        // ---- JSON 构建/解析 ----

        private static string BuildSettleJson(SettleSnapshot s)
        {
            var sb = new StringBuilder(4096);
            sb.Append("{\"cmd\":\"SETTLE\",\"sid\":");
            sb.Append(s.songId);
            sb.Append(",\"maxcombo\":");
            sb.Append(s.maxComboThis);
            sb.Append(",\"sync\":");
            sb.Append(s.syncNumberThis);
            sb.Append(",\"newrec\":");
            sb.Append(s.newRecordThis ? "true" : "false");
            sb.Append(",\"ex\":"); sb.Append(s.totalEx);
            sb.Append(",\"exact\":"); sb.Append(s.totalExact);
            sb.Append(",\"great\":"); sb.Append(s.totalGreat);
            sb.Append(",\"right\":"); sb.Append(s.totalRight);
            sb.Append(",\"miss\":"); sb.Append(s.totalMiss);
            sb.Append(",\"combo\":"); sb.Append(s.totalCombo);
            sb.Append(",\"hits\":[");
            for (int i = 0; i < s.hits.Count; i++)
            {
                if (i > 0) sb.Append(',');
                sb.Append(s.hits[i]);
            }
            sb.Append("]}");
            return sb.ToString();
        }

        /// <summary>
        /// 解析 Python 响应：JSON 头 + 二进制 PNG
        /// 格式: JSON 部分包含 stats + charts[{name,len}]，后跟各 PNG bytes
        /// </summary>
        private static SettleResult ParseResult(byte[] data)
        {
            // 简化解析：找 JSON 结束位置（第一个 '}' 后面跟的是 PNG 二进制）
            // 实际上 Python 端会发一个完整的 JSON 帧，charts 的 PNG 在 JSON 之后
            string json = Encoding.UTF8.GetString(data);

            // 用 SimpleJson 解析 JSON 部分
            // 先找 JSON 边界：从开头到匹配的 '}'
            int jsonEnd = FindJsonEnd(json);
            if (jsonEnd < 0) return null;

            string jsonPart = json.Substring(0, jsonEnd + 1);
            int pngOffset = Encoding.UTF8.GetByteCount(jsonPart);

            var result = new SettleResult();

            // 解析 stats
            var parsed = new Dictionary<string, object>();
            SimpleJson.Populate(jsonPart, parsed);
            // 由于 SimpleJson.Populate 需要目标对象，这里手动解析
            // 简化：用反射 populate 到一个临时对象
            result.stats = new SettleStats();
            result.charts = new List<ChartEntry>();

            // 手动从 parsed dict 提取字段
            if (parsed.ContainsKey("stats"))
            {
                var sd = parsed["stats"] as Dictionary<string, object>;
                if (sd != null)
                {
                    result.stats.avg = GetFloat(sd, "avg");
                    result.stats.std = GetFloat(sd, "std");
                    result.stats.totalEx = GetInt(sd, "totalEx");
                    result.stats.totalExact = GetInt(sd, "totalExact");
                    result.stats.totalGreat = GetInt(sd, "totalGreat");
                    result.stats.totalRight = GetInt(sd, "totalRight");
                    result.stats.totalMiss = GetInt(sd, "totalMiss");
                    result.stats.totalCombo = GetInt(sd, "totalCombo");
                    result.stats.calibrated = GetBool(sd, "calibrated");
                    result.stats.calDir = GetFloat(sd, "calDir");
                    result.stats.calLo = GetFloat(sd, "calLo");
                    result.stats.calHi = GetFloat(sd, "calHi");
                }
            }

            if (parsed.ContainsKey("charts"))
            {
                var cl = parsed["charts"] as System.Collections.IList;
                if (cl != null)
                {
                    int byteOff = pngOffset;
                    foreach (var item in cl)
                    {
                        var cd = item as Dictionary<string, object>;
                        if (cd == null) continue;
                        var entry = new ChartEntry();
                        entry.name = cd.ContainsKey("name") ? cd["name"].ToString() : "";
                        entry.len = cd.ContainsKey("len") ? Convert.ToInt32(cd["len"]) : 0;
                        if (entry.len > 0 && byteOff + entry.len <= data.Length)
                        {
                            entry.pngBytes = new byte[entry.len];
                            Array.Copy(data, byteOff, entry.pngBytes, 0, entry.len);
                            byteOff += entry.len;
                        }
                        result.charts.Add(entry);
                    }
                }
            }

            return result;
        }

        private static int FindJsonEnd(string s)
        {
            int depth = 0;
            bool inStr = false;
            for (int i = 0; i < s.Length; i++)
            {
                char c = s[i];
                if (inStr) { if (c == '\\') { i++; continue; } if (c == '"') inStr = false; continue; }
                if (c == '"') { inStr = true; continue; }
                if (c == '{') depth++;
                else if (c == '}') { depth--; if (depth == 0) return i; }
            }
            return -1;
        }

        private static float GetFloat(Dictionary<string, object> d, string k)
        {
            object v; return d.TryGetValue(k, out v) ? Convert.ToSingle(v) : 0f;
        }
        private static int GetInt(Dictionary<string, object> d, string k)
        {
            object v; return d.TryGetValue(k, out v) ? Convert.ToInt32(v) : 0;
        }
        private static bool GetBool(Dictionary<string, object> d, string k)
        {
            object v; return d.TryGetValue(k, out v) && Convert.ToBoolean(v);
        }
    }
}
