import os
import pandas as pd
from flask import Flask, jsonify
from flask_cors import CORS

# === Flask App Initialization ===
app = Flask(__name__)
CORS(app)

# === API Endpoint: Olive Forecasting Dashboard ===
@app.route('/api/olive-forecasting', methods=['GET'])
def olive_forecasting():
    try:
        # === Load CSV File ===
        data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
        file_path = os.path.join(data_dir, 'Usecase2_dataOlive_Oil.csv')
        df = pd.read_csv(file_path)

        # === Clean & Preprocess Columns ===
        df.columns = df.columns.str.strip()

        required_cols = [
            'Product ID', 'Quarter', 'County Retailer', 'Retailer Supplier Name',
            'Units Sold', 'Demand Forecast', 'Inventory Level', 'Units Ordered'
        ]
        df = df[required_cols].dropna(subset=['Product ID', 'Quarter'])

        # === Compute Inventory Metrics ===
        df['Restock Needed'] = df['Demand Forecast'] > df['Inventory Level']
        df['Reorder Qty'] = (df['Demand Forecast'] - df['Inventory Level']).clip(lower=0)
        df['Fulfillment Rate'] = (df['Units Sold'] / df['Demand Forecast']).round(2).clip(upper=1.0)
        df['Stockout'] = df['Inventory Level'] < df['Demand Forecast']
        df['Overstock'] = df['Inventory Level'] > (1.5 * df['Demand Forecast'])

        # === Transform Data for Drilldown View ===
        grouped = {}
        for (product, county), group in df.groupby(['Product ID', 'County Retailer']):
            suppliers = []
            for supplier, sub_group in group.groupby('Retailer Supplier Name'):
                chart_data = sub_group.sort_values('Quarter')
                suppliers.append({
                    'supplier': supplier,
                    'quarters': chart_data['Quarter'].tolist(),
                    'unitsSold': chart_data['Units Sold'].fillna(0).astype(int).tolist(),
                    'forecasted': chart_data['Demand Forecast'].fillna(0).astype(int).tolist(),
                    'inventory': chart_data['Inventory Level'].fillna(0).astype(int).tolist(),
                    'restockFlags': chart_data['Restock Needed'].tolist(),
                    'reorderQtys': chart_data['Reorder Qty'].astype(int).tolist(),
                    'fulfillmentRates': chart_data['Fulfillment Rate'].tolist(),
                    'stockouts': chart_data['Stockout'].tolist(),
                    'overstocks': chart_data['Overstock'].tolist()
                })

            if product not in grouped:
                grouped[product] = []
            grouped[product].append({
                'county': county,
                'suppliers': suppliers
            })

        # === Efficiency Summary (for Cards) ===
        quarterly_summary = (
            df.groupby('Quarter')
              .agg(
                  fulfillment_rate=('Fulfillment Rate', 'mean'),
                  stockout_rate=('Stockout', 'mean'),
                  overstock_rate=('Overstock', 'mean')
              )
              .round(2)
              .reset_index()
              .to_dict(orient='records')
        )

        # === Efficiency Table (Product × County × Quarter) ===
        efficiency_table = (
            df.groupby(['Product ID', 'County Retailer', 'Quarter'])
              .agg(
                  avg_fulfillment_rate=('Fulfillment Rate', 'mean'),
                  stockout_count=('Stockout', 'sum'),
                  overstock_count=('Overstock', 'sum')
              )
              .round(2)
              .reset_index()
              .to_dict(orient='records')
        )

        # === Final Response ===
        return jsonify({
            'products': grouped,
            'quarterly_efficiency': quarterly_summary,
            'efficiency_table': efficiency_table
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# === Run App ===
if __name__ == '__main__':
    app.run(port=5000, debug=True)
