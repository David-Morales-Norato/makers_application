import pandas as pd
import os

class Database:
    def __init__(self, data_file_path: str):
        self.data_file_path = data_file_path
        self.data = self.load_data()

    def load_data(self)-> pd.DataFrame:
        data = pd.DataFrame()
        if os.path.exists(self.data_file_path):
            data = pd.read_csv(self.data_file_path)
        return data
    
    def search_inventory(self, name: str, column: str = 'description', **kwargs)-> str:
        if column not in self.data.columns:
            return "Column not found. Please search for 'name', 'price' or 'quantity'."
        
        product = self.data[self.data['name'] == name][column]
        if product.empty:
            return "Product not found."
        else:
            return product.to_string(index=False)

    def search_type(self, product_type: str)-> str:
        product = self.data[self.data['product_type'] == product_type]
        if product.empty:
            return "Product type not found."
        else:
            return f"I have found {product.shape[0]} products of type: {product_type}, here are some of the found products: {product['name'].sample(3).to_string(index=False)}"

    def get_columns(self, col)-> str:
        return self.data[col].to_list()