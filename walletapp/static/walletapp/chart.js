
var color = Chart.helpers.color;


window.onload = function() {
    var ctx = document.getElementById('expenseChart').getContext('2d');
    window.myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Category1', 'Category2'],
            datasets: [{
                label: 'Expense',
                backgroundColor: color(window.chartColors.red).alpha(0.5).rgbString(),
                borderColor: window.chartColors.red,
                borderWidth: 1,
                data: [
                    randomScalingFactor(),
                    randomScalingFactor()
                ]
            }]

        },
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
