export async function fetchOliveForecastData() {
  try {
    const response = await fetch('http://localhost:5000/api/olive-forecasting');
    if (!response.ok) {
      throw new Error('Failed to fetch olive oil forecasting data');
    }

    const result = await response.json();

    // Return as-is for now. We'll structure it dynamically in the component.
    return result.products;  // Object: { ProductName: [ { county, suppliers[] }, ... ] }

  } catch (error) {
    console.error('Olive Forecast fetch error:', error);
    return null;
  }
}
