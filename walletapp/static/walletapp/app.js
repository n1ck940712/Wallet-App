$(document).ready(function (){


    if (window.location.pathname=='/') {loadTransaction()} // transaction page specific scripts
    if (window.location.pathname=='/overview') { //overview page scripts
        var color = Chart.helpers.color;
        var expenseChartCanvas = document.getElementById('expenseChart').getContext('2d'); // init expense chart
        var expenseChart = new Chart(expenseChartCanvas, {
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
        var balanceChartCanvas = document.getElementById("balanceChart").getContext("2d"); //init balance chart
        var balanceChart = new Chart(balanceChartCanvas, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Account Balance',
                    data: [],
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    xAxes: [{
                        type: 'time',
                        gridLines: {
                            show: false
                        }
                    }],
                    yAxes: [{
                        gridLines: {
                            show: false
                        }
                    }]
                }
            }
        });
        // click event listener accountdiv
        $('.accountDiv').click(function(){
            $(this).siblings().removeClass('selectedAccount').addClass('notSelectedAccount')
            $(this).addClass('selectedAccount').removeClass('notSelectedAccount')
            $.ajax({
                type: 'GET',
                url: 'overviewAjax',
                data: {
                    "selected_account": $('.selectedAccount').attr('id')
                },
                success: function(data) {
                    // console.log(data)
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
                    removeData(balanceChart)
                    removeData(expenseChart)

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
    }

    // filter button
    $('#filterButton').click(function(){
        loadTransaction()
    })
    // date picker
    $('#filterDate').daterangepicker({
        "opens": "left"
    });
    $('#filterDate').val('All Time')
    // clear date button
    $('#filterDate').on('cancel.daterangepicker', function(ev, picker) {
        $('#filterDate').val('All Time');
        $('#filterDateStart').val('')
        $('#filterDateEnd').val('')
    });
    $('#filterDate').on('apply.daterangepicker', function(ev, picker) {
        $('#filterDateStart').val(picker.startDate.format('YYYY-MM-DD'))
        $('#filterDateEnd').val(picker.endDate.format('YYYY-MM-DD'))
    });
    $('#filterDate').on('show.daterangepicker', function(ev, picker) {
        $('#filterDateStart').val(picker.startDate.format('YYYY-MM-DD'))
        $('#filterDateEnd').val(picker.endDate.format('YYYY-MM-DD'))
    });

    $('#addEntryButton').click(function(){ //set today date when add entry
        $(".new_entry_date").val(getTodayDate())
    })

    $('.submitNewEntry').click(function(){ // confirm new entry
        newTransaction()
    })

    $('#clearFilterButton').on('click', function(){ // clear filter
        $('#filterType').val('')
        $('#filterNote').val('')
        $('#filterAccount').val('')
        $('#filterCategory').val('')
        $('#filterDateStart').val('')
        $('#filterDateEnd').val('')
        loadTransaction()
    })

    $('.addNewCategory').click(function(){ //add new category
        addNewCategory()
    })

    $('.entryDeleteButton').click(function(){ //delete entry
        deleteEntry($('#entry_id').val())
    })
    $('.entryEditButton').click(function(){ //edit entry
        var entry_id = $('#entry_id').val()
        console.log(entry_id)
    })
})
// end of window.load



//////////////////////////////////////////////////////////////////////////////////////
// functions /////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////

function hideModal(){
    $('.modal').hide()
    $('.modal-backdrop').hide()
}

function deleteEntry(entry_id){
    $.ajax({
        type: 'GET',
        url: 'deleteEntry',
        data: {
            'entry_id': entry_id,
        },
        success: function(data){
            hideModal()
            loadTransaction()
            console.log(data)
        },
    })
}

function newTransaction(){
    var new_entry_from = $('.selectedTab').find('.new_entry_from').val()
    var new_entry_to = $('.selectedTab').find('.new_entry_to').val()
    var new_entry_amount = $('.selectedTab').find('.new_entry_amount').val()
    var new_entry_type = $('.selectedTab').find('.new_entry_type').val()
    var new_entry_date = $('.selectedTab').find('.new_entry_date').val()
    var new_entry_category = $('.selectedTab').find('.new_entry_category').val()
    var new_entry_note = $('.selectedTab').find('.new_entry_note').val()

    $.ajax({
        type: 'POST',
        url: 'addEntry',
        headers: {
            'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
        },
        data: {
            'new_entry_from': new_entry_from,
            'new_entry_to': new_entry_to,
            'new_entry_type': new_entry_type,
            'new_entry_amount': new_entry_amount,
            'new_entry_category': new_entry_category,
            'new_entry_note': new_entry_note,
            'new_entry_date': new_entry_date,
        },
        beforeSend: function () {
            $('#addingTransaction').show();
        },
        complete: function () {
            $('#addingTransaction').hide();
        },
        success: function(data) {
            hideModal()
            console.log(data)
            loadTransaction()
        }
    })
}

function getTodayDate(){
    var dd = moment().date();
    var mm = moment().month()+1;
    var yy = moment().year();
    if (mm<10) {
        mm = '0'+mm;
    }
    if (dd<10) {
        dd = '0'+dd;
    }
    var todayDate = (yy + '-' + mm + '-' + dd)
    return todayDate
}

function addNewCategory(){
    $.ajax({
        type: 'POST',
        url: 'addCategory',
        headers: {
            'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
        },
        data: {
            'new_category_name': $('.add_category_input').val()
        },
        success: function(data){
            console.log(data)
        },
        beforeSend: function () {
            $('#loadingAddNewCategory').show();
        },
        complete: function () {
            $('#loadingAddNewCategory').hide();
        },

    })
}

function loadTransaction(){
    filterNote = $('.filterContainer').find('input#filterNote')[0].value
    filterCategory = $('.filterContainer').find('select#filterCategory')[0].value
    filterAccount = $('.filterContainer').find('select#filterAccount')[0].value
    filterType = $('.filterContainer').find('select#filterType')[0].value
    filterDateStart = $('.filterContainer').find('input#filterDateStart')[0].value
    filterDateEnd = $('.filterContainer').find('input#filterDateEnd')[0].value

    $.ajax({
        type: 'GET',
        url: 'filterTransaction',
        data: {
            'filterNote': filterNote,
            'filterCategory': filterCategory,
            'filterAccount': filterAccount,
            'filterType': filterType,
            'filterDateStart': filterDateStart,
            'filterDateEnd': filterDateEnd
        },
        beforeSend: function () {
            $('.loadingTransaction').show();
        },
        complete: function () {
            $('.loadingTransaction').hide();
        },
        success: function(data){
            var accounts = JSON.parse(data.accounts)
            var category = JSON.parse(data.category)
            var transaction = JSON.parse(data.transaction)
            var transaction_date = JSON.parse(data.transaction_date)
            var message = data.message
            $('.transactionDiv').html('')
            if (transaction==null||transaction.length==0) {
                var transactionDivSub =
                `<div class="transactionDivSub text-center">
                    <h2>No entry matches filter criteria.</h2>
                </div>`;
                $('.transactionDiv').append(transactionDivSub)

            }
            for (var x in transaction_date) {
                var transactionDivSub = $(`<div class="transactionDivSub">
                    <div class="transactionDivSubTitle" style="display:flex;justify-content:space-between;">
                        <h4>${transaction_date[x].fields.entryDate}</h4>
                        <span class="dailyTotal">$Total</span>
                    </div>
                </div>`)

                for (var y in transaction) {
                    if (transaction[y].fields.entryDate == transaction_date[x].fields.entryDate) {
                        if (transaction[y].fields.type == 'Income') {
                            var transactionDivSubSub =
                            `<div class="transactionDivSubSub divIncome" style="display:flex; cursor:pointer;" transID="${transaction[y].pk}" data-toggle="modal" data-target="#indexModal" onclick="selectTransaction(${transaction[y].pk})">
                                <div class="transLeft">
                                    <span class="transType">Income</span>:
                                    <span class="transCategory">${transaction[y].fields.category}</span>
                                    (<span class="transAccount">${transaction[y].fields.toAccount}</span>)
                                    <span class="transNote">${transaction[y].fields.entryNote}</span>
                                </div>
                                <div class="transRight">
                                    <span class="dailyAdd">${transaction[y].fields.amount}</span>
                                </div>
                            </div>`;
                            transactionDivSub.append(transactionDivSubSub)
                        }
                        if (transaction[y].fields.type == 'Expense') {
                            var transactionDivSubSub =
                            `<div class="transactionDivSubSub divExpense" style="display:flex; cursor:pointer;" transID="${transaction[y].pk}" data-toggle="modal" data-target="#indexModal" onclick="selectTransaction(${transaction[y].pk})">
                                <div class="transLeft">
                                    <span class="transType">Expense</span>:
                                    <span class="transCategory">${transaction[y].fields.category}</span>
                                    (<span class="transAccount">${transaction[y].fields.fromAccount}</span>)
                                    <span class="transNote">${transaction[y].fields.entryNote}</span>
                                    <span class="transNote">${transaction[y].fields.entryDate}</span>
                                </div>
                                <div class="transRight">
                                    <span class="dailyAdd">${transaction[y].fields.amount}</span>
                                </div>
                            </div>`;
                            transactionDivSub.append(transactionDivSubSub)
                        }
                        if (transaction[y].fields.type == 'Transfer') {
                            var transactionDivSubSub =
                            `<div class="transactionDivSubSub divTransfer" style="display:flex; cursor:pointer;" transID="${transaction[y].pk}" data-toggle="modal" data-target="#indexModal" onclick="selectTransaction(${transaction[y].pk})">
                                <div class="transLeft">
                                    <span class="transType">Transfer</span>:
                                    <span class="transCategory">${transaction[y].fields.category}</span> from
                                    (<span class="transAccount">${transaction[y].fields.fromAccount}</span>) to
                                    (<span class="transAccount">${transaction[y].fields.toAccount}</span>)
                                    <span class="transNote">${transaction[y].fields.entryNote}</span>
                                </div>
                                <div class="transRight">
                                    <span class="dailyAdd">${transaction[y].fields.amount}</span>
                                </div>
                            </div>`;
                            transactionDivSub.append(transactionDivSubSub)
                        }
                    }
                }
                $('.transactionDiv').append(transactionDivSub)
            }
            getDailyChange()
        }
    })
}

function removeData(chart){ //clear data from chart
    chart.data.labels = []
    chart.data.datasets.forEach((dataset) => {
        dataset.data = []
    });
    chart.update();
}

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

function selectTransaction(trans_id){
    $('.editEntryHiddendiv').html(`
        <input type="hidden" id="entry_id" value="${trans_id}">
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
    $('.tabContent').removeClass('selectedTab')
    $('.tabContent').hide()
    $('#'+tab_name).addClass('selectedTab')
    $('#'+tab_name).show()
}

function closeTab(){
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
