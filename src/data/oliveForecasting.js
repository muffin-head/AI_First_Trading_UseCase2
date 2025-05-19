export async function fetchOliveForecastData() {
  try {
    const response = await fetch('http://localhost:5000/api/olive-forecasting');
    if (!response.ok) {
      throw new Error('Failed to fetch olive oil forecasting data');
    }

    const result = await response.json();

    // Return everything (products, scorecard, etc.)
    return result;

  } catch (error) {
    console.error('Olive Forecast fetch error:', error);
    return null;
  }
}
