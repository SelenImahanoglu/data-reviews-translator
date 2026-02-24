import pandas as pd
import numpy as np
from olist.utils import haversine_distance
from olist.data import Olist

class Order:
    '''
    DataFrames containing all orders as index,
    and various properties of these orders as columns
    '''
    def __init__(self):
        self.data = Olist().get_data()

    def get_wait_time(self, is_delivered=True):
        orders = self.data['orders'].copy()

        if is_delivered:
            orders = orders.query("order_status=='delivered'").copy()

        orders.loc[:, 'order_delivered_customer_date'] = pd.to_datetime(orders['order_delivered_customer_date'])
        orders.loc[:, 'order_estimated_delivery_date'] = pd.to_datetime(orders['order_estimated_delivery_date'])
        orders.loc[:, 'order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])

        orders.loc[:, 'delay_vs_expected'] = (orders['order_delivered_customer_date'] - orders['order_estimated_delivery_date']) / np.timedelta64(24, 'h')

        def handle_delay(x):
            if x > 0:
                return x
            else:
                return 0

        orders.loc[:, 'delay_vs_expected'] = orders['delay_vs_expected'].apply(handle_delay)
        orders.loc[:, 'wait_time'] = (orders['order_delivered_customer_date'] - orders['order_purchase_timestamp']) / np.timedelta64(24, 'h')
        orders.loc[:, 'expected_wait_time'] = (orders['order_estimated_delivery_date'] - orders['order_purchase_timestamp']) / np.timedelta64(24, 'h')

        return orders[[
            'order_id', 'wait_time', 'expected_wait_time', 'delay_vs_expected', 'order_status'
        ]]

    def get_review_score(self):
        reviews = self.data['order_reviews'].copy()

        def dim_five_star(d):
            return 1 if d == 5 else 0

        def dim_one_star(d):
            return 1 if d == 1 else 0

        def calculate_review_cost(score):
            if score == 1:
                return 100
            elif score == 2:
                return 50
            elif score == 3:
                return 40
            else:
                return 0

        reviews.loc[:, 'dim_is_five_star'] = reviews['review_score'].apply(dim_five_star)
        reviews.loc[:, 'dim_is_one_star'] = reviews['review_score'].apply(dim_one_star)
        reviews.loc[:, 'cost_of_review'] = reviews['review_score'].apply(calculate_review_cost)

        return reviews[[
            'order_id', 'dim_is_five_star', 'dim_is_one_star', 'review_score', 'cost_of_review'
        ]]

    def get_number_items(self):
        data = self.data
        items = data['order_items'].groupby('order_id', as_index=False).agg({'order_item_id': 'count'})
        items.columns = ['order_id', 'number_of_items']
        return items

    def get_number_sellers(self):
        data = self.data
        sellers = data['order_items'].groupby('order_id')['seller_id'].nunique().reset_index()
        sellers.columns = ['order_id', 'number_of_sellers']
        return sellers

    def get_price_and_freight(self):
        data = self.data
        price_freight = data['order_items'].groupby('order_id', as_index=False).agg({'price': 'sum', 'freight_value': 'sum'})
        return price_freight

    def get_distance_seller_customer(self):
        data = self.data
        orders = data['orders']
        order_items = data['order_items']
        sellers = data['sellers']
        customers = data['customers']

        geo = data['geolocation']
        geo = geo.groupby('geolocation_zip_code_prefix', as_index=False).first()

        sellers_mask_columns = ['seller_id', 'seller_zip_code_prefix', 'geolocation_lat', 'geolocation_lng']
        sellers_geo = sellers.merge(geo, how='left', left_on='seller_zip_code_prefix', right_on='geolocation_zip_code_prefix')[sellers_mask_columns]

        customers_mask_columns = ['customer_id', 'customer_zip_code_prefix', 'geolocation_lat', 'geolocation_lng']
        customers_geo = customers.merge(geo, how='left', left_on='customer_zip_code_prefix', right_on='geolocation_zip_code_prefix')[customers_mask_columns]

        customers_sellers = customers.merge(orders, on='customer_id')\
            .merge(order_items, on='order_id')\
            .merge(sellers, on='seller_id')\
            [['order_id', 'customer_id','customer_zip_code_prefix', 'seller_id', 'seller_zip_code_prefix']]

        matching_geo = customers_sellers.merge(sellers_geo, on='seller_id')\
            .merge(customers_geo, on='customer_id', suffixes=('_seller', '_customer'))

        matching_geo = matching_geo.dropna()

        matching_geo.loc[:, 'distance_seller_customer'] = matching_geo.apply(lambda row:
                               haversine_distance(row['geolocation_lng_seller'],
                                                  row['geolocation_lat_seller'],
                                                  row['geolocation_lng_customer'],
                                                  row['geolocation_lat_customer']), axis=1)

        order_distance = matching_geo.groupby('order_id', as_index=False).agg({'distance_seller_customer': 'mean'})
        return order_distance

    def get_training_data(self, is_delivered=True, with_distance_seller_customer=False):
        training_set = self.get_wait_time(is_delivered)\
                .merge(self.get_review_score(), on='order_id')\
                .merge(self.get_number_items(), on='order_id')\
                .merge(self.get_number_sellers(), on='order_id')\
                .merge(self.get_price_and_freight(), on='order_id')

        if with_distance_seller_customer:
            training_set = training_set.merge(self.get_distance_seller_customer(), on='order_id')

        return training_set.dropna()
