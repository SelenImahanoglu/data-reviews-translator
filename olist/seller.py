import pandas as pd
import numpy as np
from olist.data import Olist
from olist.order import Order

class Seller:
    def __init__(self):
        self.data = Olist().get_data()

    def get_seller_features(self):
        sellers = self.data['sellers'].copy()
        return sellers[['seller_id', 'seller_city', 'seller_state']]

    def get_seller_delay_wait_time(self):
        orders = Order().get_wait_time()
        order_items = self.data['order_items'].copy()

        seller_orders = order_items.merge(orders, on='order_id')

        delay_wait = seller_orders.groupby('seller_id', as_index=False).agg({
            'delay_vs_expected': 'mean',
            'wait_time': 'mean'
        })
        return delay_wait

    def get_active_dates(self):
        orders = self.data['orders'].copy()
        order_items = self.data['order_items'].copy()

        orders['order_approved_at'] = pd.to_datetime(orders['order_approved_at'])
        seller_orders = order_items.merge(orders, on='order_id')

        active_dates = seller_orders.groupby('seller_id', as_index=False).agg({
            'order_approved_at': ['min', 'max']
        })
        active_dates.columns = ['seller_id', 'date_first_sale', 'date_last_sale']

        # Olist'te geçirilen ay sayısını hesaplayalım (M hatasını çözmek için gün üzerinden bölme yapıyoruz)
        active_dates['months_on_olist'] = (active_dates['date_last_sale'] - active_dates['date_first_sale']) / np.timedelta64(1, 'D') / 30

        # Eğer ilk ve son satışı aynı ay içindeyse 0 çıkabilir, bunu önlemek için ayları kontrol edelim
        active_dates['months_on_olist'] = active_dates['months_on_olist'].apply(lambda x: x if x > 0 else 0)

        return active_dates

    def get_review_score(self):
        reviews = Order().get_review_score()
        order_items = self.data['order_items'].copy()

        # Bir siparişte birden fazla satıcı olabilir, review siparişe verilir.
        seller_reviews = order_items[['order_id', 'seller_id']].drop_duplicates().merge(reviews, on='order_id')

        reviews_agg = seller_reviews.groupby('seller_id', as_index=False).agg({
            'review_score': 'mean',
            'cost_of_review': 'sum', # Yeni eklediğimiz review maliyetlerini seller bazında topluyoruz
            'dim_is_five_star': 'mean',
            'dim_is_one_star': 'mean'
        })
        return reviews_agg

    def get_quantity(self):
        order_items = self.data['order_items'].copy()

        quantity = order_items.groupby('seller_id', as_index=False).agg({
            'order_id': 'nunique',
            'order_item_id': 'count'
        })
        quantity.columns = ['seller_id', 'n_orders', 'quantity']
        return quantity

    def get_sales(self):
        order_items = self.data['order_items'].copy()

        sales = order_items.groupby('seller_id', as_index=False).agg({'price': 'sum'})
        sales.rename(columns={'price': 'sales'}, inplace=True)
        return sales

    def get_training_data(self):
        # Tüm parçaları birleştiriyoruz
        training_set = self.get_seller_features()\
            .merge(self.get_seller_delay_wait_time(), on='seller_id')\
            .merge(self.get_active_dates(), on='seller_id')\
            .merge(self.get_review_score(), on='seller_id')\
            .merge(self.get_quantity(), on='seller_id')\
            .merge(self.get_sales(), on='seller_id')

        # Eksik verileri temizleyelim
        training_set = training_set.dropna()

        # CEO Talebi için Gelir (Revenues) ve Kâr (Profits) Hesaplamaları:
        # Gelir = (Aylık 80 BRL abonelik ücreti * Olist'te kalınan ay) + (Toplam satışların %10'u)
        training_set['revenues'] = (training_set['months_on_olist'] * 80) + (training_set['sales'] * 0.1)

        # Kâr = Gelir - Yorum Maliyeti (Cost of Reviews)
        training_set['profits'] = training_set['revenues'] - training_set['cost_of_review']

        return training_set
