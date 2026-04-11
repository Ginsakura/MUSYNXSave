class SyncDataAnalyzer:
    def __init__(self):
        self.data: dict[str, list[int, float]] = {
            "4KeyEasy": [0, 0.0],
            "4KeyHard": [0, 0.0],
            "4KeyInferno": [0, 0.0],
            "6KeyEasy": [0, 0.0],
            "6KeyHard": [0, 0.0],
            "6KeyInferno": [0, 0.0],
        }

    @staticmethod
    def _safe_avg(counter: int, score_sum: float) -> float:
        """安全的平均值计算，防止被除数为 0 导致崩溃"""
        return (score_sum / counter) if counter > 0 else 0.0

    def clear(self):
        """重置所有统计数据"""
        for key in self.data:
            self.data[key] = [0, 0.0]

    def calculate_all_stats(self) -> dict[str, float]:
        """计算并返回所有维度的综合同步率"""
        stats = {
            # mode: counter, avg
            "": [0, 0.0],
            "separator0": [0, 0.0],
            "4K": [0, 0.0],
            "6K": [0, 0.0],
            "separator1": [0, 0.0],
            "EZ": [0, 0.0],
            "HD": [0, 0.0],
            "IN": [0, 0.0],
            "separator2": [0, 0.0],
            "4KEZ": [0, 0.0],
            "4KHD": [0, 0.0],
            "4KIN": [0, 0.0],
            "separator3": [0, 0.0],
            "6KEZ": [0, 0.0],
            "6KHD": [0, 0.0],
            "6KIN": [0, 0.0],
            }
        data = self.data

        # ==========================================
        # 4. 每条独立显示的同步率 (4KEZ, 6KHD 等)
        # ==========================================
        for mode, (counter, score_sum) in data.items():
            mode_str: str = mode.replace("Key", "K").replace("Easy", "EZ").replace("Hard", "HD").replace("Inferno", "IN")
            stats[mode_str] = [counter, self._safe_avg(counter, score_sum) * 100.0]

        # ==========================================
        # 1. 所有数据合并的`综合同步率`
        # ==========================================
        total_counter = sum(val[0] for val in data.values())
        total_score = sum(val[1] for val in data.values())
        stats[""] = [total_counter, self._safe_avg(total_counter, total_score) * 100.0]

        # ==========================================
        # 2. 按照键型合并的综合同步率 (4K, 6K)
        # ==========================================
        for key_type in ["4K", "6K"]:
            k_counter = sum(v[0] for k, v in data.items() if key_type in k)
            k_score = sum(v[1] for k, v in data.items() if key_type in k)
            stats[f"{key_type}"] = [k_counter, self._safe_avg(k_counter, k_score) * 100.0]

        # ==========================================
        # 3. 按照难度合并的综合同步率 (EZ, HD, IN)
        # ==========================================
        difficulty_map = {"Easy": "EZ", "Hard": "HD", "Inferno": "IN"}
        for diff_key, diff_alias in difficulty_map.items():
            d_counter = sum(v[0] for k, v in data.items() if diff_key in k)
            d_score = sum(v[1] for k, v in data.items() if diff_key in k)
            stats[f"{diff_alias}"] = [d_counter, self._safe_avg(d_counter, d_score) * 100.0]

        return stats
