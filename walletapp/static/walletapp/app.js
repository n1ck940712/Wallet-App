$(document).ready(function (){

    getDailyChange() //calculate daily total

    $('#filterDate').daterangepicker({
         "opens": "left"
    });
    $('#filterDate').on('apply.daterangepicker', function(ev, picker) {
        $('#filterDateStart').val(picker.startDate.format('YYYY-MM-DD'))
        $('#filterDateEnd').val(picker.endDate.format('YYYY-MM-DD'))
    });
    $('#filterDate').on('show.daterangepicker', function(ev, picker) {
        $('#filterDateStart').val(picker.startDate.format('YYYY-MM-DD'))
        $('#filterDateEnd').val(picker.endDate.format('YYYY-MM-DD'))
    });

    $('#addEntryButton').on('click', function(){
        console.log(moment().date()+"/"+moment().month()+"/"+moment().year())
        var dd = moment().date();
        var mm = moment().month()+1;
        var yy = moment().year();
        if (mm<10) {
            mm = '0'+mm;
        }
        if (dd<10) {
            dd = '0'+dd;
        }
        var test = (yy + '-' + mm + '-' + dd)
        $(".new_entry_date").val(test)
    })

    $('#clearFilterButton').on('click', function(){
        $('#filterType').val('')
        $('#filterAccount').val('')
        $('#filterCategory').val('')
        $('#filterNote').val('')
        $('.transactionDivSubSub').each(function(){
            $(this).show()
        })
        getTransTotal()
    })

    // create initial chart (expense)
    var color = Chart.helpers.color;
    var ctx = document.getElementById('expenseChart').getContext('2d');
    var expenseChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                data: [],
                label: 'Total',
                backgroundColor: color(window.chartColors.red).alpha(0.5).rgbString(),
                borderColor: window.chartColors.red,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            title: {
                display: true,
                text: 'Expense'
            },
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: true
                    }
                }]
            }
        }
    });

    // create initial chart (balance history)
    var ctx = document.getElementById("balanceChart").getContext("2d");
    var balanceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
            label: 'Change of Account Balance',
            data: [],
            backgroundColor: [
                'rgba(255, 99, 132, 0.2)',
                'rgba(54, 162, 235, 0.2)',
                'rgba(255, 206, 86, 0.2)',
                'rgba(75, 192, 192, 0.2)',
                'rgba(153, 102, 255, 0.2)',
                'rgba(255, 159, 64, 0.2)'
            ],
            borderColor: [
                'rgba(255,99,132,1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(75, 192, 192, 1)',
                'rgba(153, 102, 255, 1)',
                'rgba(255, 159, 64, 1)'
            ],
            borderWidth: 1
            }]
        },
        options: {
            scales: {
                xAxes: [{
                    type: 'time'
                }]
            }
        }
    });

    $('.accountDiv').click(function(){
        $.ajax({
            type: 'GET',
            url: 'overviewAjax',
            data: {
                "selected_account": $(this).attr('id')
            },
            success: function(data) {
                console.log(data)
                var transaction = JSON.parse(data.transaction)
                var transaction_category = data.transaction_category

                $('#totalIncome').text("$ "+data.total_income)
                $('#totalExpense').text("$ "+data.total_expense)
                $('#totalChange').text("$ "+data.total_change)
                $('#totalTransfer').text("$ "+data.total_transfer)

                // update transaction div
                $('.transContrCont').html('')
                for (var item in transaction) {
                    if (transaction[item].fields.type =='Expense') {
                        var trans = $('<div class="transContrContSub divExpense"></div>').text(`${transaction[item].fields.type}: ${transaction[item].fields.category} (${transaction[item].fields.fromAccount}) ${transaction[item].fields.entryNote}   $${transaction[item].fields.amount}`)
                    }
                    if (transaction[item].fields.type =='Income') {
                        var trans = $('<div class="transContrContSub divIncome"></div>').text(`${transaction[item].fields.type}: ${transaction[item].fields.category} (${transaction[item].fields.toAccount}) ${transaction[item].fields.entryNote}   $${transaction[item].fields.amount}`)
                    }
                    if (transaction[item].fields.type =='Transfer') {
                        var trans = $('<div class="transContrContSub divTransfer"></div>').text(`${transaction[item].fields.type}: from (${transaction[item].fields.fromAccount}) to  (${transaction[item].fields.toAccount}) ${transaction[item].fields.entryNote}   $${transaction[item].fields.amount}`)
                    }
                    $('.transContrCont').append(trans)
                }

                // update account balance chart
                var latest_balance = parseInt(JSON.parse(data.selected_account_balance)[0].fields.accountBalance)
                var balance_history = (data.balance_history).reverse()
                var bal_history_date = []
                var bal_history_amount = []
                balanceChart.data.datasets[0].data.push(latest_balance)
                for (var item in balance_history) {
                    latest_balance -= balance_history[item].total
                    balanceChart.data.datasets[0].data.push(latest_balance)
                    balanceChart.data.labels.push(balance_history[item].entryDate)
                }
                // for (var item in bal_history_amount) {
                //     balanceChart.data.datasets[0].data.push(bal_history_amount[item])
                // }
                // for (var item in bal_history_date) {
                //     balanceChart.data.labels.push(bal_history_date[item])
                // }
                balanceChart.update()

                //update expense chart
                for (var item in transaction_category) {
                    expenseChart.data.labels.push(transaction_category[item].category);
                    expenseChart.data.datasets[0].data.push(Math.abs(transaction_category[item].total));
                }
                expenseChart.update();
            }
        })
    })
})


//////////////////////////////////////////////////////////////////////////////////////
// functions /////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////

function getDailyChange(){ //sum up total for the day
    $('.transactionDivSub').each(function(){
        var total=0;
        $(this).find(".transactionDivSubSub").each(function(){
            if ($(this).is(':visible')&&$(this).find('.transType').text()!="Transfer") {
                total+=parseInt($(this)[0].children[1].children[0].innerHTML)
            }
            else {
            }
        })
        $(this).find('.dailyTotal').html("$"+total)
    })
}

function functionA(trans_id){
    $('.inviForm').html(`
        <input type="hidden" name="entry_id" value="${trans_id}">
    `)
}

function categoryDetail(category_id, category_name){
    $('#edit_category_input').val(category_name)
    $('.inviForm').html(`
        <input type="hidden" name="category_id" value="${category_id}">
    `)
}

function addCategory(){
    $('#edit_category_input').val()
    $('#categoryModalbutton2').html("Add")
}

function accountDetail(account_id, account_name, account_balance, account_type){
    $('#edit_account_name').val(account_name)
    $('#edit_account_balance').val(account_balance)
    $('#edit_account_type').val(account_type)
    $('.inviForm').html(`
        <input type="hidden" name="account_id" value="${account_id}">
    `)
}

function openTab(env, tab_name){
    $('.tabContent').hide()
    $('#'+tab_name).show()
}

function closeModal(){
    $('.tabContent').hide()
}

// $('#filterNote').on('keyup', function(){ //event listener for filter note
//     filter = $(this).val().toLowerCase()
//     $('.transactionDivSubSub').find(".transNote").each(function(){ //filter for transaction note
//         text = $(this).text().toLowerCase()
//         if (text.indexOf(filter)!=-1) {
//             $(this).parent('div').parent('div').show()
//         }
//         else {
//             $(this).parent('div').parent('div').hide()
//         }
//     })
//     getTransTotal()
//
// })
//
// $('#filterCategory').change(function(){ //event listener for filter category
//     filter = $(this).val()
//     $('.transactionDivSubSub').find(".transCategory").each(function(){ //filter for transaction category
//         // var elementNum = $(this).parent().parent().parent()[0].childElementCount
//         if ($(this).text().indexOf(filter)!=-1) {
//             $(this).parent('div').parent('div').show()
//         }
//         else {
//             $(this).parent('div').parent('div').hide()
//         }
//     })
//     getTransTotal()
// })
//
// $('#filterAccount').change(function(){ //event listener for filter account
//     filter = $(this).val()
//     $('.transactionDivSubSub').find(".transAccount").each(function(){ //filter for account
//         if ($(this).text().indexOf(filter)!=-1) {
//             $(this).parent('div').parent('div').show()
//         }
//         else {
//             $(this).parent('div').parent('div').hide()
//         }
//     })
//     getTransTotal()
// })
//
// $('#filterType').change(function(){ //event listener for filter Type
//     filter_type = $(this).val()
//     filter_note = $('#filterNote').val()
//     filter_account = $('#filterAccount').val()
//     filter_category = $('#filterCategory').val()
//     $('.transactionDivSubSub').find(".transType").each(function(){ //filter for transaction type
//         if ($(this).text().indexOf(filter_type)!=-1) {
//             $(this).parent('div').parent('div').show()
//         }
//         else {
//             $(this).parent('div').parent('div').hide()
//         }
//     })
//     $('.transactionDivSubSub').find(".transNote").each(function(){ //filter for transaction note
//         text = $(this).text().toLowerCase()
//         if (text.indexOf(filter_note)!=-1) {
//             $(this).parent('div').parent('div').show()
//         }
//         else {
//             $(this).parent('div').parent('div').hide()
//         }
//     })
//     getTransTotal()
// })
