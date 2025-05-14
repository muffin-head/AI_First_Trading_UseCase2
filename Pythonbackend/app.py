from flask import Flask, jsonify
from flask_cors import CORS
import os
import pandas as pd

# === FLASK APP SETUP ===
app = Flask(__name__)
CORS(app)

@app.route('/api/olive-forecasting', methods=['GET'])
def olive_forecasting():
    try:
        # Load the dataset from /data
        data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
        file_path = os.path.join(data_dir, 'Usecase2_dataOlive_Oil.csv')
        df = pd.read_csv(file_path)

        # Ensure consistent column names (strip spaces, lowercase)
        df.columns = df.columns.str.strip()

        # Filter only relevant columns
        cols = ['Product ID', 'Quarter', 'County Retailer', 'Retailer Supplier Name',
                'Units Sold', 'Demand Forecast', 'Inventory Level', 'Units Ordered']
        df = df[cols].dropna(subset=['Product ID', 'Quarter'])

        # Grouped structure for drilldown UI (product → region → supplier)
        grouped = {}
        for (product, county), group in df.groupby(['Product ID', 'County Retailer']):
            suppliers = []
            for supplier, sub_group in group.groupby('Retailer Supplier Name'):
                chart_data = sub_group.sort_values('Quarter')
                suppliers.append({
                    'supplier': supplier,
                    'quarters': chart_data['Quarter'].tolist(),
                    'unitsSold': chart_data['Units Sold'].astype(int).tolist(),
                    'forecasted': chart_data['Demand Forecast'].astype(int).tolist(),
                    'inventory': chart_data['Inventory Level'].astype(int).tolist()
                })

            if product not in grouped:
                grouped[product] = []
            grouped[product].append({
                'county': county,
                'suppliers': suppliers
            })

        return jsonify({'products': grouped})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(port=5000, debug=True)
