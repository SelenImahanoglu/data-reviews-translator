import os
import pandas as pd

class Olist:
    def get_data(self):
        # 1. Adım: Mevcut projedeki data klasörüne bak
        base_dir = os.path.dirname(os.path.dirname(__file__))
        csv_path = os.path.join(base_dir, "data", "csv")

        # 2. Adım: Eğer bu projede veri yoksa, otomatik olarak
        # dünkü çalışan projeye (data-orders) gidip verileri oradan çeksin
        if not os.path.exists(csv_path):
            desktop = os.path.expanduser("~/Desktop")
            csv_path = os.path.join(desktop, "data-orders", "data", "csv")

        # 3. Adım: Klasördeki tüm csv dosyalarını bul, isimlendir ve oku
        file_names = [f for f in os.listdir(csv_path) if f.endswith('.csv')]
        key_names = [f.replace('olist_', '').replace('_dataset', '').replace('.csv', '') for f in file_names]

        data = {}
        for key, file in zip(key_names, file_names):
            data[key] = pd.read_csv(os.path.join(csv_path, file))
        return data
