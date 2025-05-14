export async function fetchWineDashboardData() {
  try {
    const response = await fetch('http://localhost:5000/api/wine-dashboard');
    if (!response.ok) {
      throw new Error('Failed to fetch wine dashboard data');
    }

    const result = await response.json();

    const kpis = {
      totalWines: result.kpis.totalWines,
      avgRating: result.kpis.avgRating,
      topCountry: result.kpis.topCountry,
      varietyCount: result.kpis.varietyCount,
    };

    const formatBarChart = (chartData, color = '#8b5cf6') => ({
      series: chartData.series,
      chartOptions: {
        chart: {
          type: 'bar',
          height: 300,
          toolbar: { show: false },
        },
        plotOptions: {
          bar: {
            horizontal: false,
            columnWidth: '55%',
            borderRadius: 6,
          },
        },
        xaxis: chartData.chartOptions.xaxis,
        fill: {
          opacity: 1,
        },
        dataLabels: {
          enabled: false,
        },
        tooltip: {
          y: {
            formatter: val => `${val}`,
          },
        },
        colors: [color],
      },
    });

    const formatPieChart = (chartData, colors = ['#f87171', '#34d399', '#fbbf24', '#60a5fa']) => ({
      series: chartData.series,
      chartOptions: {
        chart: {
          type: 'pie',
          height: 300,
        },
        labels: chartData.chartOptions.labels,
        legend: {
          position: 'bottom',
        },
        responsive: [
          {
            breakpoint: 480,
            options: {
              chart: { width: 200 },
              legend: { position: 'bottom' },
            },
          },
        ],
        colors,
      },
    });

    const formatLineChart = (chartData, colors = ['#8b5cf6', '#34d399']) => ({
      series: chartData.series,
      chartOptions: {
        chart: {
          type: 'line',
          height: 300,
          toolbar: { show: false },
        },
        xaxis: chartData.chartOptions.xaxis,
        stroke: {
          curve: 'smooth',
        },
        dataLabels: {
          enabled: false,
        },
        tooltip: {
          y: {
            formatter: val => `${val}`,
          },
        },
        colors,
      },
    });

    return {
      kpis,
      charts: {
        countryChart: formatBarChart(result.charts.countryChart),
        typeChart: formatPieChart(result.charts.typeChart),
        ratingOverYearChart: formatLineChart(result.charts.ratingOverYearChart),
        regionChart: formatBarChart(result.charts.regionChart, '#60a5fa'),
        wineryChart: formatBarChart(result.charts.wineryChart, '#f59e0b'),
        priceCountryChart: formatBarChart(result.charts.priceCountryChart, '#10b981'),
        priceTypeChart: formatPieChart(result.charts.priceTypeChart, ['#a78bfa', '#34d399', '#fbbf24', '#60a5fa']),
        priceBucketChart: formatBarChart(result.charts.priceBucketChart, '#f87171'),
        bestValueChart: formatPieChart(result.charts.bestValueChart, ['#4ade80', '#6366f1', '#facc15', '#ec4899']),
        vintageChart: formatBarChart(result.charts.vintageChart, '#c084fc'),
        wineryRatingChart: formatBarChart(result.charts.wineryRatingChart, '#ec4899'),
        typePriceChart: formatBarChart(result.charts.typePriceChart, '#fcd34d'),
      },
    };
  } catch (error) {
    console.error('Dashboard fetch error:', error);
    return null;
  }
}
