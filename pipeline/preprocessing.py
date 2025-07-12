import pandas as pd
from sklearn.preprocessing import LabelEncoder

def preprocess_data(orders_df, products_df, order_products_df):
    # ✅ Merge product and order details
    df = order_products_df.merge(products_df, on="product_id", how="left")
    df = df.merge(orders_df, on="order_id", how="left")

    # ✅ Filter out unknown users/products (useful if reused for new input)
    known_users = orders_df["user_id"].unique()
    known_products = products_df["product_id"].unique()
    df = df[df["user_id"].isin(known_users) & df["product_id"].isin(known_products)]

    # ✅ Feature: Total user orders
    user_order_counts = orders_df.groupby("user_id")["order_number"].max().reset_index()
    user_order_counts.columns = ["user_id", "user_total_orders"]
    df = df.merge(user_order_counts, on="user_id", how="left")

    # ✅ Feature: Total product reorders
    product_reorders = order_products_df.groupby("product_id")["reordered"].sum().reset_index()
    product_reorders.columns = ["product_id", "product_reorder_count"]
    df = df.merge(product_reorders, on="product_id", how="left")

    # ✅ Feature: Total product orders
    product_total_orders = order_products_df.groupby("product_id")["order_id"].count().reset_index()
    product_total_orders.columns = ["product_id", "product_total_orders"]
    df = df.merge(product_total_orders, on="product_id", how="left")

    # ✅ Feature: Product reorder ratio
    df["product_reorder_rate"] = df["product_reorder_count"] / df["product_total_orders"]

    # ✅ Handle missing values
    df["days_since_prior_order"] = df["days_since_prior_order"].fillna(0)
    df["product_name"] = df["product_name"].fillna("Unknown")

    # ✅ Encode product_name (categorical)
    le_product = LabelEncoder()
    df["product_name_encoded"] = le_product.fit_transform(df["product_name"].astype(str))

    # ✅ Final feature set
    features = df[[
        "user_id",
        "product_id",
        "product_name_encoded",        # <--- new encoded categorical feature
        "order_dow",
        "order_hour_of_day",
        "add_to_cart_order",
        "user_total_orders",
        "product_reorder_rate",
        "days_since_prior_order"
    ]].copy()

    # ✅ Attach label
    features["reordered"] = df["reordered"].values

    return features.dropna()
