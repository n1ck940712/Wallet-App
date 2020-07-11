var DEFAULT_DATASET_SIZE = 7;

var addedCount = 0;
var color = Chart.helpers.color;
var barChartData = {
    labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
    datasets: [{
        label: 'Expense',
        backgroundColor: color(window.chartColors.red).alpha(0.5).rgbString(),
        borderColor: window.chartColors.red,
        borderWidth: 1,
        data: [
            randomScalingFactor(),
            randomScalingFactor(),
            randomScalingFactor(),
            randomScalingFactor(),
            randomScalingFactor(),
            randomScalingFactor(),
            randomScalingFactor()
        ]
    }]

};

window.onload = function() {
    var ctx = document.getElementById('expenseChart').getContext('2d');
    window.myChart = new Chart(ctx, {
        type: 'bar',
        data: barChartData,
        options: {
            responsive: true,
            title: {
                display: true,
                text: 'Expense'
            },
            tooltips: {
                mode: 'point'
            }
        }
    });
};


var MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
var config = {
    type: 'line',
    data: {
        labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
        datasets: [{
            label: 'My First dataset',
            backgroundColor: window.chartColors.red,
            borderColor: window.chartColors.red,
            data: [
                randomScalingFactor(),
                randomScalingFactor(),
                randomScalingFactor(),
                randomScalingFactor(),
                randomScalingFactor(),
                randomScalingFactor(),
                randomScalingFactor()
            ],
            fill: false,
        }]
    },
    options: {
        responsive: true,
        title: {
            display: true,
            text: 'Balance'
        },
        tooltips: {
            mode: 'index',
            intersect: false,
        },
        hover: {
            mode: 'nearest',
            intersect: true
        },
        scales: {
            x: {
                display: true,
                scaleLabel: {
                    display: true,
                    labelString: 'Month'
                }
            },
            y: {
                display: true,
                scaleLabel: {
                    display: true,
                    labelString: 'Value'
                }
            }
        }
    }
};

window.onload = function() {
    var ctx = document.getElementById('balanceChart').getContext('2d');
    window.myLine = new Chart(ctx, config);
    var ctx = document.getElementById('expenseChart').getContext('2d');
    window.myChart = new Chart(ctx, {
        type: 'bar',
        data: barChartData,
        options: {
            responsive: true,
            title: {
                display: true,
                text: 'Expense'
            },
            tooltips: {
                mode: 'point'
            }
        }
    });
};
