using System;
using System.Collections.Generic;
using System.Globalization;
using System.Reflection;
using System.Text;

namespace MUSYNCDelay.Config
{
    /// <summary>
    /// 极简 JSON 序列化/反序列化，仅支持 POCO 嵌套 + 基本类型。
    /// 配置结构简单且固定，无需引入第三方 JSON 库。
    /// </summary>
    internal static class SimpleJson
    {
        // ---- 序列化 ----

        public static string Serialize(object obj)
        {
            var sb = new StringBuilder();
            WriteValue(sb, obj, 0);
            return sb.ToString();
        }

        private static void WriteValue(StringBuilder sb, object val, int indent)
        {
            if (val == null) { sb.Append("null"); return; }
            var t = val.GetType();
            if (t == typeof(string)) { WriteString(sb, (string)val); return; }
            if (t == typeof(bool)) { sb.Append((bool)val ? "true" : "false"); return; }
            if (t == typeof(int)) { sb.Append(((int)val).ToString(CultureInfo.InvariantCulture)); return; }
            if (t == typeof(float)) { sb.Append(((float)val).ToString("R", CultureInfo.InvariantCulture)); return; }
            if (t == typeof(double)) { sb.Append(((double)val).ToString("R", CultureInfo.InvariantCulture)); return; }
            if (t.IsClass && t != typeof(string)) { WriteObject(sb, val, indent); return; }
            sb.Append(val.ToString());
        }

        private static void WriteString(StringBuilder sb, string s)
        {
            sb.Append('"');
            foreach (char c in s)
            {
                switch (c)
                {
                    case '"': sb.Append("\\\""); break;
                    case '\\': sb.Append("\\\\"); break;
                    case '\n': sb.Append("\\n"); break;
                    case '\r': sb.Append("\\r"); break;
                    case '\t': sb.Append("\\t"); break;
                    default: sb.Append(c); break;
                }
            }
            sb.Append('"');
        }

        private static void WriteObject(StringBuilder sb, object obj, int indent)
        {
            var fields = obj.GetType().GetFields(BindingFlags.Public | BindingFlags.Instance);
            sb.Append("{\n");
            for (int i = 0; i < fields.Length; i++)
            {
                AppendIndent(sb, indent + 1);
                WriteString(sb, fields[i].Name);
                sb.Append(": ");
                WriteValue(sb, fields[i].GetValue(obj), indent + 1);
                if (i < fields.Length - 1) sb.Append(',');
                sb.Append('\n');
            }
            AppendIndent(sb, indent);
            sb.Append('}');
        }

        private static void AppendIndent(StringBuilder sb, int level)
        {
            for (int i = 0; i < level; i++) sb.Append("  ");
        }

        // ---- 反序列化（populate 已有对象） ----

        public static void Populate(string json, object target)
        {
            int pos = 0;
            var parsed = ParseValue(json, ref pos);
            if (parsed is Dictionary<string, object> dict)
                ApplyDict(dict, target);
        }

        private static void ApplyDict(Dictionary<string, object> dict, object target)
        {
            var t = target.GetType();
            foreach (var kv in dict)
            {
                var f = t.GetField(kv.Key, BindingFlags.Public | BindingFlags.Instance);
                if (f == null) continue;
                object val = kv.Value;
                if (val is Dictionary<string, object> sub && f.FieldType.IsClass && f.FieldType != typeof(string))
                {
                    object child = f.GetValue(target);
                    if (child == null) { child = Activator.CreateInstance(f.FieldType); f.SetValue(target, child); }
                    ApplyDict(sub, child);
                }
                else
                {
                    f.SetValue(target, ConvertValue(val, f.FieldType));
                }
            }
        }

        private static object ConvertValue(object val, Type target)
        {
            if (val == null) return target.IsValueType ? Activator.CreateInstance(target) : null;
            if (target == typeof(string)) return val.ToString();
            if (target == typeof(int)) return Convert.ToInt32(val, CultureInfo.InvariantCulture);
            if (target == typeof(float)) return Convert.ToSingle(val, CultureInfo.InvariantCulture);
            if (target == typeof(double)) return Convert.ToDouble(val, CultureInfo.InvariantCulture);
            if (target == typeof(bool)) return Convert.ToBoolean(val, CultureInfo.InvariantCulture);
            return val;
        }

        // ---- 极简 JSON 解析器 ----

        private static object ParseValue(string s, ref int pos)
        {
            SkipWs(s, ref pos);
            if (pos >= s.Length) return null;
            char c = s[pos];
            if (c == '{') return ParseObject(s, ref pos);
            if (c == '[') return ParseArray(s, ref pos);
            if (c == '"') return ParseString(s, ref pos);
            if (c == 't' || c == 'f') return ParseBool(s, ref pos);
            if (c == 'n') { pos += 4; return null; }
            return ParseNumber(s, ref pos);
        }

        private static Dictionary<string, object> ParseObject(string s, ref int pos)
        {
            var dict = new Dictionary<string, object>();
            pos++; // skip {
            SkipWs(s, ref pos);
            if (pos < s.Length && s[pos] == '}') { pos++; return dict; }
            while (pos < s.Length)
            {
                SkipWs(s, ref pos);
                string key = ParseString(s, ref pos);
                SkipWs(s, ref pos);
                pos++; // skip :
                object val = ParseValue(s, ref pos);
                dict[key] = val;
                SkipWs(s, ref pos);
                if (pos < s.Length && s[pos] == ',') { pos++; continue; }
                if (pos < s.Length && s[pos] == '}') { pos++; break; }
            }
            return dict;
        }

        private static List<object> ParseArray(string s, ref int pos)
        {
            var list = new List<object>();
            pos++; // skip [
            SkipWs(s, ref pos);
            if (pos < s.Length && s[pos] == ']') { pos++; return list; }
            while (pos < s.Length)
            {
                list.Add(ParseValue(s, ref pos));
                SkipWs(s, ref pos);
                if (pos < s.Length && s[pos] == ',') { pos++; continue; }
                if (pos < s.Length && s[pos] == ']') { pos++; break; }
            }
            return list;
        }

        private static string ParseString(string s, ref int pos)
        {
            pos++; // skip opening "
            var sb = new StringBuilder();
            while (pos < s.Length)
            {
                char c = s[pos++];
                if (c == '"') break;
                if (c == '\\' && pos < s.Length)
                {
                    char esc = s[pos++];
                    switch (esc)
                    {
                        case '"': sb.Append('"'); break;
                        case '\\': sb.Append('\\'); break;
                        case 'n': sb.Append('\n'); break;
                        case 'r': sb.Append('\r'); break;
                        case 't': sb.Append('\t'); break;
                        default: sb.Append(esc); break;
                    }
                }
                else sb.Append(c);
            }
            return sb.ToString();
        }

        private static bool ParseBool(string s, ref int pos)
        {
            if (s[pos] == 't') { pos += 4; return true; }
            pos += 5; return false;
        }

        private static object ParseNumber(string s, ref int pos)
        {
            int start = pos;
            bool isFloat = false;
            if (s[pos] == '-') pos++;
            while (pos < s.Length && (char.IsDigit(s[pos]) || s[pos] == '.' || s[pos] == 'e' || s[pos] == 'E' || s[pos] == '+' || s[pos] == '-'))
            {
                if (s[pos] == '.' || s[pos] == 'e' || s[pos] == 'E') isFloat = true;
                pos++;
            }
            string num = s.Substring(start, pos - start);
            if (isFloat) return double.Parse(num, CultureInfo.InvariantCulture);
            return int.Parse(num, CultureInfo.InvariantCulture);
        }

        private static void SkipWs(string s, ref int pos)
        {
            while (pos < s.Length && char.IsWhiteSpace(s[pos])) pos++;
        }
    }
}
