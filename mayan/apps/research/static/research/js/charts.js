/*
 * Research App Chart Integration
 * Task 2.6 - Chart.js integration for professional data visualizations
 * Optimized for demo presentation and live screen sharing
 */

(function($) {
    'use strict';

    // Research Charts namespace
    window.ResearchCharts = {
        // Color palette for consistent styling
        colors: {
            primary: '#007bff',
            secondary: '#6c757d', 
            success: '#28a745',
            info: '#17a2b8',
            warning: '#ffc107',
            danger: '#dc3545',
            light: '#f8f9fa',
            dark: '#343a40'
        },

        // Gradient definitions for professional charts
        gradients: {
            blue: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            green: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
            purple: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
            cyan: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
        },

        // Default chart configuration for professional appearance
        defaultConfig: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 20,
                        font: {
                            size: 12,
                            weight: '600'
                        }
                    }
                },
                tooltip: {
                    enabled: true,
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: '#007bff',
                    borderWidth: 1,
                    titleFont: {
                        size: 14,
                        weight: 'bold'
                    },
                    bodyFont: {
                        size: 12
                    },
                    padding: 12,
                    cornerRadius: 8
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            },
            scales: {
                x: {
                    grid: {
                        display: true,
                        color: 'rgba(0, 0, 0, 0.1)',
                        borderDash: [2, 2]
                    },
                    ticks: {
                        font: {
                            size: 11
                        },
                        color: '#6c757d'
                    }
                },
                y: {
                    grid: {
                        display: true,
                        color: 'rgba(0, 0, 0, 0.1)',
                        borderDash: [2, 2]
                    },
                    ticks: {
                        font: {
                            size: 11
                        },
                        color: '#6c757d'
                    }
                }
            }
        },

        /**
         * Create a professional histogram chart
         * @param {string} canvasId - ID of the canvas element
         * @param {Object} data - Chart data object
         * @param {Object} options - Chart configuration options
         */
        createHistogram: function(canvasId, data, options) {
            const ctx = document.getElementById(canvasId);
            if (!ctx) {
                console.warn('Canvas element not found:', canvasId);
                return null;
            }

            const config = {
                type: 'bar',
                data: {
                    labels: data.labels || [],
                    datasets: [{
                        label: data.label || 'Distribution',
                        data: data.values || [],
                        backgroundColor: 'rgba(54, 162, 235, 0.7)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1.5,
                        borderRadius: 4,
                        borderSkipped: false
                    }]
                },
                options: $.extend(true, {}, this.defaultConfig, {
                    plugins: {
                        title: {
                            display: true,
                            text: data.title || 'Data Distribution',
                            font: {
                                size: 16,
                                weight: 'bold'
                            },
                            color: '#343a40',
                            padding: 20
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Frequency'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: data.xlabel || 'Values'
                            }
                        }
                    }
                }, options)
            };

            return new Chart(ctx, config);
        },

        /**
         * Create a professional line chart for time series data
         * @param {string} canvasId - ID of the canvas element
         * @param {Object} data - Chart data object
         * @param {Object} options - Chart configuration options
         */
        createLineChart: function(canvasId, data, options) {
            const ctx = document.getElementById(canvasId);
            if (!ctx) {
                console.warn('Canvas element not found:', canvasId);
                return null;
            }

            const config = {
                type: 'line',
                data: {
                    labels: data.labels || [],
                    datasets: data.datasets || [{
                        label: data.label || 'Data Series',
                        data: data.values || [],
                        borderColor: '#007bff',
                        backgroundColor: 'rgba(0, 123, 255, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointBackgroundColor: '#007bff',
                        pointBorderColor: '#ffffff',
                        pointBorderWidth: 2,
                        pointRadius: 5,
                        pointHoverRadius: 8
                    }]
                },
                options: $.extend(true, {}, this.defaultConfig, {
                    plugins: {
                        title: {
                            display: true,
                            text: data.title || 'Time Series Analysis',
                            font: {
                                size: 16,
                                weight: 'bold'
                            },
                            color: '#343a40',
                            padding: 20
                        }
                    }
                }, options)
            };

            return new Chart(ctx, config);
        },

        /**
         * Create a professional pie chart
         * @param {string} canvasId - ID of the canvas element
         * @param {Object} data - Chart data object
         * @param {Object} options - Chart configuration options
         */
        createPieChart: function(canvasId, data, options) {
            const ctx = document.getElementById(canvasId);
            if (!ctx) {
                console.warn('Canvas element not found:', canvasId);
                return null;
            }

            const config = {
                type: 'pie',
                data: {
                    labels: data.labels || [],
                    datasets: [{
                        data: data.values || [],
                        backgroundColor: [
                            '#007bff', '#28a745', '#ffc107', '#dc3545', 
                            '#17a2b8', '#6f42c1', '#fd7e14', '#20c997'
                        ],
                        borderColor: '#ffffff',
                        borderWidth: 2
                    }]
                },
                options: $.extend(true, {}, this.defaultConfig, {
                    plugins: {
                        title: {
                            display: true,
                            text: data.title || 'Distribution Analysis',
                            font: {
                                size: 16,
                                weight: 'bold'
                            },
                            color: '#343a40',
                            padding: 20
                        }
                    },
                    scales: {}  // Remove scales for pie chart
                }, options)
            };

            return new Chart(ctx, config);
        },

        /**
         * Create a professional scatter plot
         * @param {string} canvasId - ID of the canvas element
         * @param {Object} data - Chart data object
         * @param {Object} options - Chart configuration options
         */
        createScatterPlot: function(canvasId, data, options) {
            const ctx = document.getElementById(canvasId);
            if (!ctx) {
                console.warn('Canvas element not found:', canvasId);
                return null;
            }

            const config = {
                type: 'scatter',
                data: {
                    datasets: data.datasets || [{
                        label: data.label || 'Data Points',
                        data: data.points || [],
                        backgroundColor: 'rgba(255, 99, 132, 0.6)',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 1,
                        pointRadius: 6,
                        pointHoverRadius: 8
                    }]
                },
                options: $.extend(true, {}, this.defaultConfig, {
                    plugins: {
                        title: {
                            display: true,
                            text: data.title || 'Correlation Analysis',
                            font: {
                                size: 16,
                                weight: 'bold'
                            },
                            color: '#343a40',
                            padding: 20
                        }
                    },
                    scales: {
                        x: {
                            type: 'linear',
                            position: 'bottom',
                            title: {
                                display: true,
                                text: data.xlabel || 'X Values'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: data.ylabel || 'Y Values'
                            }
                        }
                    }
                }, options)
            };

            return new Chart(ctx, config);
        },

        /**
         * Create charts from analysis results data
         * @param {Object} analysisResults - Analysis results from API
         * @param {string} containerId - Container element ID
         */
        renderAnalysisCharts: function(analysisResults, containerId) {
            const container = document.getElementById(containerId);
            if (!container) {
                console.warn('Container element not found:', containerId);
                return;
            }

            // Clear existing charts
            container.innerHTML = '';

            if (!analysisResults || !analysisResults.professional_charts) {
                this.showNoChartsMessage(container);
                return;
            }

            const charts = analysisResults.professional_charts;

            // Render distribution charts
            if (charts.distributions && charts.distributions.length > 0) {
                charts.distributions.forEach((chart, index) => {
                    this.createChartFromAnalysis(container, chart, `distribution-${index}`);
                });
            }

            // Render correlation heatmap
            if (charts.correlations) {
                this.createChartFromAnalysis(container, charts.correlations, 'correlation');
            }

            // Render summary dashboard
            if (charts.summary_dashboard) {
                this.createSummaryDashboard(container, charts.summary_dashboard);
            }
        },

        /**
         * Create a chart from analysis data
         * @private
         */
        createChartFromAnalysis: function(container, chartData, chartId) {
            const chartDiv = document.createElement('div');
            chartDiv.className = 'chart-container mb-4';
            chartDiv.innerHTML = `
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h5 class="mb-0">${chartData.title || 'Analysis Chart'}</h5>
                    <span class="badge badge-info">${chartData.quality || 'good'}</span>
                </div>
                <div class="chart-canvas-container" style="height: 400px;">
                    <canvas id="${chartId}" width="400" height="400"></canvas>
                </div>
                ${chartData.insights ? `
                    <div class="mt-3">
                        <h6>Key Insights:</h6>
                        <ul class="list-unstyled">
                            ${chartData.insights.map(insight => `<li><i class="fa fa-lightbulb text-warning"></i> ${insight}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            `;
            
            container.appendChild(chartDiv);

            // If chart has base64 image data, display it
            if (chartData.image_data) {
                this.displayBase64Chart(chartId, chartData.image_data);
            } else {
                // Create Chart.js chart from statistics
                this.createChartFromStatistics(chartId, chartData);
            }
        },

        /**
         * Display base64 encoded chart image
         * @private
         */
        displayBase64Chart: function(canvasId, imageData) {
            const canvas = document.getElementById(canvasId);
            if (!canvas) return;

            const img = new Image();
            img.onload = function() {
                const ctx = canvas.getContext('2d');
                canvas.width = img.width;
                canvas.height = img.height;
                ctx.drawImage(img, 0, 0);
            };
            img.src = imageData;
        },

        /**
         * Create Chart.js chart from statistics data
         * @private
         */
        createChartFromStatistics: function(canvasId, chartData) {
            if (!chartData.statistics) return;

            const stats = chartData.statistics;
            
            if (chartData.type === 'distribution') {
                // Create histogram from statistics
                this.createHistogram(canvasId, {
                    title: chartData.title,
                    label: 'Frequency',
                    labels: ['Min', 'Q1', 'Median', 'Q3', 'Max'],
                    values: [1, stats.count * 0.25, stats.count * 0.5, stats.count * 0.75, 1],
                    xlabel: 'Value Range'
                });
            }
        },

        /**
         * Show message when no charts are available
         * @private
         */
        showNoChartsMessage: function(container) {
            container.innerHTML = `
                <div class="text-center py-5">
                    <i class="fa fa-chart-line fa-3x text-muted mb-3"></i>
                    <h5 class="text-muted">No Charts Available</h5>
                    <p class="text-muted">Run dataset analysis to generate professional charts and visualizations.</p>
                </div>
            `;
        },

        /**
         * Create summary dashboard visualization
         * @private
         */
        createSummaryDashboard: function(container, dashboardData) {
            const dashboardDiv = document.createElement('div');
            dashboardDiv.className = 'research-dashboard mb-4';
            dashboardDiv.innerHTML = `
                <div class="row">
                    <div class="col-12">
                        <h4><i class="fa fa-tachometer-alt"></i> Summary Dashboard</h4>
                    </div>
                </div>
                <div class="row">
                    ${dashboardData.key_metrics ? Object.entries(dashboardData.key_metrics).map(([key, value]) => `
                        <div class="col-md-3 mb-3">
                            <div class="research-metric-item">
                                <div class="research-metric-label">${key.replace(/_/g, ' ')}</div>
                                <div class="research-metric-value">${value}</div>
                            </div>
                        </div>
                    `).join('') : ''}
                </div>
                ${dashboardData.insights ? `
                    <div class="row">
                        <div class="col-12">
                            <div class="research-analysis-section">
                                <h5>Dashboard Insights</h5>
                                <ul class="list-unstyled">
                                    ${dashboardData.insights.map(insight => `<li><i class="fa fa-check-circle text-success"></i> ${insight}</li>`).join('')}
                                </ul>
                            </div>
                        </div>
                    </div>
                ` : ''}
            `;

            container.appendChild(dashboardDiv);
        },

        /**
         * Initialize chart rendering for dataset detail page
         */
        initDatasetCharts: function() {
            // Check if we're on a dataset detail page
            const analysisContainer = document.getElementById('analysis-charts-container');
            if (!analysisContainer) return;

            // Get dataset ID from page
            const datasetId = analysisContainer.getAttribute('data-dataset-id');
            if (!datasetId) return;

            // Fetch analysis results and render charts
            this.fetchAndRenderCharts(datasetId, 'analysis-charts-container');
        },

        /**
         * Fetch analysis results from API and render charts
         * @param {string} datasetId - Dataset ID
         * @param {string} containerId - Container element ID
         */
        fetchAndRenderCharts: function(datasetId, containerId) {
            $.ajax({
                url: `/api/v4/research/datasets/${datasetId}/analysis/`,
                method: 'GET',
                success: (response) => {
                    this.renderAnalysisCharts(response, containerId);
                },
                error: (xhr, status, error) => {
                    console.warn('Failed to fetch analysis results:', error);
                    const container = document.getElementById(containerId);
                    if (container) {
                        this.showNoChartsMessage(container);
                    }
                }
            });
        }
    };

    // Initialize charts when document is ready
    $(document).ready(function() {
        // Initialize dataset charts if on dataset detail page
        ResearchCharts.initDatasetCharts();

        // Expose Chart.js globally for template usage
        if (typeof Chart !== 'undefined') {
            Chart.defaults.font.family = "'Inter', 'Segoe UI', 'Helvetica Neue', Arial, sans-serif";
            Chart.defaults.font.size = 12;
            Chart.defaults.color = '#6c757d';
        }
    });

})(jQuery); 