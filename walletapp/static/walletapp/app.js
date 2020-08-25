$(document).ready(function (){

    $('.alert').alert()
    setTimeout(function(){
        $('.alert').alert('close')},3000
    )

// transaction page
    if (window.location.pathname=='/') {loadEntry()}

    $('.filterButton').click(function(){
        loadEntry()
    })

    $('.filterDate').daterangepicker({
        "opens": "left"
    });

    $('.filterDate').val('All Time')

    $('.filterDate').on('cancel.daterangepicker', function(ev, picker) {
        $('.filterDate').val('All Time');
        $('.filterDateStart').val('')
        $('.filterDateEnd').val('')
        if (window.location.pathname=='/overview'){
            console.log('clear')
            loadOverview()
        }
    });
    $('.filterDate').on('apply.daterangepicker', function(ev, picker) {
        $('.filterDateStart').val(picker.startDate.format('YYYY-MM-DD'))
        $('.filterDateEnd').val(picker.endDate.format('YYYY-MM-DD'))
        if (window.location.pathname=='/overview'){
            console.log('apply')
            loadOverview()
        }
    });
    $('.filterdate').on('show.daterangepicker', function(ev, picker) {
        $('.filterdateStart').val(picker.startDate.format('YYYY-MM-DD'))
        $('.filterdateEnd').val(picker.endDate.format('YYYY-MM-DD'))
    });

    $('.clearFilterButton').click(function(){ // clear filter
        $('.filterType').val('')
        $('.filterNote').val('')
        $('.filterAccount').val('')
        $('.filterCategory').val('')
        $('.filterDateStart').val('')
        $('.filterDateEnd').val('')
        $('.filterDate').val('All Time')
        loadEntry()
    })

    $('.entryDeleteButton').click(function(){ //delete entry
        deleteEntry($('.entry_id').val())
    })

    $('.entryEditButton').click(function(){ //edit entry
        editEntry($('.entry_id').val())
    })

// setting page

    if (window.location.pathname=='/settings') {
        loadSettings()
        $('.exportDate').daterangepicker({
            "opens": "left"
        });
        $('.exportDate').on('apply.daterangepicker', function(ev, picker) {
            $('.exportDateStart').val(picker.startDate.format('YYYY-MM-DD'))
            $('.exportDateEnd').val(picker.endDate.format('YYYY-MM-DD'))
            if (window.location.pathname=='/overview'){
                loadOverview()
            }
        });
    }
    $('.deleteCategoryConfirm').click(function(){
        deleteCategory()
    })

    $('.deleteAccountConfirm').click(function(){
        deleteAccount()
    })

// overview page
    if (window.location.pathname=='/overview') {
        $('.overviewContainer').children(':first').addClass('selectedAccount').removeClass('notSelectedAccount')//select first account
        loadOverview()
        var color = Chart.helpers.color;
        var expenseChartCanvas = document.getElementById('expenseChart').getContext('2d'); // init expense chart
        expenseChart = new Chart(expenseChartCanvas, {
            type: 'pie',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    label: 'expense',
                    backgroundColor: [
						window.chartColors.red,
						window.chartColors.orange,
						window.chartColors.yellow,
						window.chartColors.green,
						window.chartColors.blue,
					],
                }],
            },
            options: {
                responsive: true,
                title: {
                    display: true,
                    text: 'Expense'
                },
            }
        });
        var incomeChartCanvas = document.getElementById('incomeChart').getContext('2d'); // init income chart
        incomeChart = new Chart(incomeChartCanvas, {
            type: 'pie',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    label: 'Income',
                    backgroundColor: [
                        window.chartColors.green,
                        window.chartColors.blue,
                        window.chartColors.yellow,
                        window.chartColors.orange,
						window.chartColors.red,
					],
                }],
            },
            options: {
                responsive: true,
                title: {
                    display: true,
                    text: 'Income'
                },
            }
        });

        var balanceChartCanvas = document.getElementById("balanceChart").getContext("2d"); //init balance chart
        balanceChart = new Chart(balanceChartCanvas, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Account Balance',
                    data: [],
                    borderWidth: 1,
                    backgroundColor: [
						window.chartColors.blue,
					],
                    lineTension: 0
                }]
            },
            options: {
                scales: {
                    xAxes: [{
                        type: 'time',
                        time: {
                            unit: 'day'
                        },
                        gridLines: {
                            // display:false
                        }
                    }],
                    yAxes: [{
                        gridLines: {
                            // display: false,
                        },
                        ticks: {
                            beginAtZero: true
                        }
                    }]
                },
                title: {
                    display: true,
                    text: 'Balance'
                },
                legend: {
                    display: false
                },
                // elements: {
                //     point:{
                //         radius: 0
                //     }
                // }
            }
        });
    }
    $('.accountSelect').change(function(){
        getAccountOverview()
    })

})
// end of window.load



//////////////////////////////////////////////////////////////////////////////////////
// functions /////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////

function startExport(){
    var exportDateStart = $('.exportDateStart').val()
    var exportDateEnd = $('.exportDateEnd').val()
    $.ajax({
        type: 'GET',
        url: 'export',
        data: {
            'exportDateStart': exportDateStart,
            'exportDateEnd': exportDateEnd,
        },
        beforeSend: function(){
            $('.loadingAnim').show()
        },
        complete: function(){
            $('.loadingAnim').hide()
        },
        success: function(data) {
            var transaction = JSON.parse(data.transaction)
            var account = JSON.parse(data.account)
            var category = JSON.parse(data.category)
            var csvString = converToCsv(transaction,account,category)
            var blob = new Blob([csvString]);
            if (window.navigator.msSaveOrOpenBlob) 
                window.navigator.msSaveBlob(blob, `${exportDateStart} to ${exportDateEnd}.csv`);
            else
            {
                var a = window.document.createElement("a");
                a.href = window.URL.createObjectURL(blob, {type: "text/plain"});
                a.download = `${exportDateStart} to ${exportDateEnd}.csv`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
            }            
        }
    })
}

function converToCsv(transaction,account,category){
    var str = '';
    var line = '';
    for (var index in transaction[0].fields) {
        if (line != '') line += ','
        line += index;
    }
    str += line + '\r\n';

    for (var i = 0; i < transaction.length; i++) {
        var line = '';
        for (var index in transaction[i].fields) {
            if (line != '') line += ','
            if  (index == 'category'){
                for (var x in category) {
                    if (category[x].pk == transaction[i].fields[index]) {
                        line += category[x].fields.categoryName
                    }
                }
            }
            else if (index == 'fromAccount' || index == 'toAccount'){
                for (var x in account) {
                    if (account[x].pk == transaction[i].fields[index]) {
                        line += account[x].fields.accountName
                    }
                }
            }
            else {
                line += transaction[i].fields[index];
            }
            if (!transaction[i].fields[index] && transaction[i].fields[index] != '0' ){
                line += 'N/A'
            }
        }
        str += line + '\r\n';
    }
    return str;
}

function test(){
    console.log('formsubmit')
}

function regSubmit(){
    var reg_email = $('.reg_email').val()
    var reg_first_name = $('.reg_first_name').val()
    var reg_last_name = $('.reg_last_name').val()
    var reg_password = $('.reg_password').val()
    var reg_password2 = $('.reg_password2').val()
    var reg_dob = $('.reg_dob').val()
    $.ajax({
        type: 'GET',
        url: 'register',
        data: {
            "reg_email": reg_email,
            // "reg_first_name": reg_first_name,
            // "reg_last_name": reg_last_name,
            'reg_password': reg_password,
            'reg_password2': reg_password2,
            'reg_dob': reg_dob,
        },
        beforeSend: function(){
            $('.loadingAnim').show()
        },
        complete: function(){
            $('.loadingAnim').hide()
        },
        success: function(data) {
            if (data.message_type == 'success') {
                hideModal()
            }
            else {
                $('.reg_password').val('')
                $('.reg_password2').val('')
            }
            $('.alertCont').append(`
                <div class="alert alert-${data.message_type} fade show text-center">
                ${data.message}
                </div>
            `)
            $('.alert').alert()
            setTimeout(function(){
                $('.alert').alert('close')},3000
            )
        }
    })
        
}

function loadOverview(){
    getAccountOverview()
}

function getAccountOverview(){
    var filter_start_date = $('.filterDateStart').val()
    var filter_end_date = $('.filterDateEnd').val()
    var filter_end_date_plus1 = new Date(filter_end_date)
    filter_end_date_plus1.setDate(filter_end_date_plus1.getDate()+1)
    $.ajax({
        type: 'GET',
        url: 'getAccountOverview',
        data: {
            "selected_account": $('.accountSelect').val(),
            'filter_date_start': filter_start_date,
            'filter_date_end': filter_end_date,
            'filter_date_end+1': convertDate(filter_end_date_plus1),
        },
        beforeSend: function(){
            $('.loadingAnim').show()
        },
        complete: function(){
            $('.loadingAnim').hide()
        },
        success: function(data) {
            console.log(data)
            var category = JSON.parse(data.category)
            var expense_category = data.expense_category
            var income_category = data.income_category
            var daily_change = data.daily_change
            var latest_balance = data.selected_account_balance

            $('.totalIncome').text("$ "+data.total_income.toFixed(2))
            $('.totalExpense').text("$ "+data.total_expense.toFixed(2))
            $('.totalChange').text("$ "+data.total_change.toFixed(2))
            $('.totalTransfer').text("$ "+data.total_transfer.toFixed(2))

            removeData(balanceChart)
            removeData(expenseChart)
            removeData(incomeChart)

            // update account balance chart
            var keys = Object.keys(daily_change)
            var array_last_item = keys.length-1

            balanceChart.data.datasets[0].data.push(latest_balance) //plot first data point
            var today_date = convertDate(new Date())
            if (filter_end_date !='') {
                if (filter_end_date > today_date) {
                    filter_end_date = today_date
                    if (keys[0] != filter_end_date) {
                        balanceChart.data.labels.push(filter_end_date)
                        balanceChart.data.datasets[0].data.push(latest_balance)
                    }
                }
            } else {
                if (keys[0] != today_date) {
                    balanceChart.data.labels.push(today_date)
                    balanceChart.data.datasets[0].data.push(latest_balance)
                }
            }
            for(var keys = Object.keys(daily_change), i = 0, end = keys.length; i < end; i++) {
                var key = keys[i], value = daily_change[key];
                latest_balance -= daily_change[keys[i]]
                balanceChart.data.datasets[0].data.push(latest_balance)
                balanceChart.data.labels.push(keys[i])
                if (i < array_last_item) {
                    var date1 = new Date(keys[i])
                    var date2 = new Date(keys[i+1])
                    var day_interval =  date1.getDate() - date2.getDate()
                    if (day_interval > 1) {
                        date1.setDate(date1.getDate()-1)
                        balanceChart.data.labels.push(convertDate(date1))
                        balanceChart.data.datasets[0].data.push(latest_balance)
                    }
                }
            };
            var dateVar = new Date(keys[array_last_item])
            dateVar.setDate(dateVar.getDate()-1)
            balanceChart.data.labels.push(convertDate(dateVar))
            balanceChart.update()
            // console.log(balanceChart.data)

            //update expense chart
            for (var item in expense_category) {
                expenseChart.data.labels.push(lookUpCategory(expense_category[item].category, category));
                expenseChart.data.datasets[0].data.push(Math.abs(expense_category[item].total));
            }
            expenseChart.update();

            //update income chart
            for (var item in income_category) {
                incomeChart.data.labels.push(lookUpCategory(income_category[item].category, category));
                incomeChart.data.datasets[0].data.push(Math.abs(income_category[item].total));
            }
            incomeChart.update();
        }
    })
}

// account
function addAccount(){
    $.ajax({
        type: 'POST',
        url: 'addAccount',
        headers: {
            'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
        },
        data: {
            'add_account_name': $('.add_account_name').val(),
            'add_account_type': $('.add_account_type').val(),
            'add_account_balance': $('.add_account_balance').val(),
        },
        beforeSend: function(){
            $('.loadingAnim').show()
        },
        success: function(data){
            hideModal()
            loadSettings()
            console.log(data)
        }
    })
}

function editAccount(){
    $.ajax({
        type: 'POST',
        url: 'editAccount',
        headers: {
            'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
        },
        data: {
            'account_id': $('.account_id').val(),
            'edit_account_name': $('.edit_account_name').val(),
            'edit_account_balance': $('.edit_account_balance').val(),
            'edit_account_type': $('.edit_account_type').val(),
        },
        beforeSend: function(){
            $('.loadingAnim').show()
        },
        success: function(data){
            hideModal()
            loadSettings()
            console.log(data)
        }
    })
}

function deleteAccount(){
    $.ajax({
        type: 'POST',
        url: 'deleteAccount',
        headers: {
            'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
        },
        data: {
            'account_id': $('.account_id').val()
        },
        beforeSend: function(){
            $('.loadingAnim').show()
        },
        success: function(data){
            hideModal()
            loadSettings()
            console.log(data)
        }
    })
}

function accountDetail(account_id, account_name, account_balance, account_type){
    $('.edit_account_name').val(account_name)
    $('.edit_account_balance').val(account_balance)
    $('.edit_account_type').val(account_type)
    $('.inviForm').html(`
        <input type="hidden" class="account_id" value="${account_id}">
    `)
}

// category
function addCategory(){
    console.log('addcategory')
    var add_category_name = $('.add_category_name').val()
    var add_category_type = $('.add_category_type').val()
    if (!/\S/.test(add_category_name) || add_category_name.charAt(0)==' ') {
        console.log('Invalid category name. Try again.')
        $('.add_category_name').val('')
        $('.add_category_type').val('')
    }
    else {
        $.ajax({
            type: 'POST',
            url: 'addCategory',
            headers: {
                'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
            },
            data: {
                'new_category_name': $('.add_category_name').val(),
                'new_category_type': $('.add_category_type').val()
            },
            beforeSend: function(){
                $('.loadingAnim').show()
            },
            success: function(data){
                hideModal()
                loadSettings()
                console.log(data)
            },

        })
    }

}

function editCategoryConfirm(){
    $.ajax({
        type: 'POST',
        url: 'editCategory',
        headers: {
            'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
        },
        data: {
            'category_id': $('.category_id').val(),
            'edit_category_input':$('.edit_category_input').val(),
        },
        beforeSend: function(){
            $('.loadingAnim').show()
        },
        success: function(data){
            hideModal()
            loadSettings()
            console.log(data)
        }
    })
}

function deleteCategory(){
    $.ajax({
        type: 'GET',
        url: 'deleteCategory',
        data: {
            'category_id': $('.category_id').val(),
        },
        beforeSend: function(){
            $('.loadingAnim').show()
        },
        success: function(data){
            hideModal()
            loadSettings()
            console.log(data)
        }
    })
}

function categoryDetail(category_id, category_name){
    $('.edit_category_input').val(category_name)
    $('.inviForm').html(`
        <input type="hidden" class="category_id" value="${category_id}">
    `)
}

// function toggleEditCategory(){
//     if  ($('.editCateToggBut').html() === 'Edit') {
//         $('.editCateToggBut').html('Cancel')
//         $('.editCateToggBut').addClass('btn-danger')
//         $('.editCateToggBut').removeClass('btn-primary')
//     } else {
//         $('.editCateToggBut').html('Edit')
//         $('.editCateToggBut').removeClass('btn-danger')
//         $('.editCateToggBut ').addClass('btn-primary')
//     }
//     $('.showAddCateBut').toggle()
// }

//loadsettings
function loadSettings(){
    $.ajax({
        type: 'GET',
        url: 'loadSettings',
        data: 'data',
        beforeSend: function(){
            $('.loadingAnim').show()
        },
        complete: function(){
            $('.loadingAnim').hide()
        },
        success: function(data){
            var category = JSON.parse(data.category)
            var account = JSON.parse(data.account)
            $('.accountContainerBody').html('')
            $('.categoryContainerBody').html('')
            for (var i in category) {
                var categorySub = $(`
                    <div class="categorySub">
                        <div>${category[i].fields.categoryName}</div>
                        <button class="btn btn-primary btn-sm" data-toggle="modal" data-target=".categoryModal" onclick="categoryDetail('${category[i].pk}', '${category[i].fields.categoryName}')">Edit</button>
                    </div>
                `)
                if (category[i].fields.categoryType=='expense') {
                    $('.categoryExpense').append(categorySub)
                }
                if (category[i].fields.categoryType=='income') {
                    $('.categoryIncome').append(categorySub)
                }
            }
            if ($('.categoryIncome > div').length < 1) {
                var noCategory = $(`
                    <div class="categorySub">
                        <div>No category</div>
                    </div>
                `)
                $('.categoryIncome').append(noCategory)
            }
            if ($('.categoryExpense > div').length < 1) {
                var noCategory = $(`
                    <div class="categorySub">
                        <div>No category</div>
                    </div>
                `)
                $('.categoryExpense').append(noCategory)
            }
            for (var i in account) {
                var accountSub = $(`
                    <div class="accountSub">
                        <div>${account[i].fields.accountName} (${account[i].fields.accountType}) - Balance: ${account[i].fields.accountBalance}</div>
                        <button type="button" class="btn btn-primary btn-sm" data-toggle="modal" data-target=".accountModal" onclick="accountDetail('${account[i].pk}', '${account[i].fields.accountName}', '${account[i].fields.accountBalance}', '${account[i].fields.accountType}')">Edit</button>
                    </div>
                `)
                $('.accountContainerBody').append(accountSub)
            }
        }
    })
}

// entry
function addEntry(){
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
            $('.loadingAnim').show();
        },
        success: function(data) {
            hideModal()
            console.log(data)
            loadEntry()
        }
    })
}

function editEntry(entry_id){
    $.ajax({
        type: 'GET',
        url: 'editEntry',
        data: {
            'entry_id': entry_id,
        },
        beforeSend: function () {
            $('.loadingAnim').show();
        },
        complete: function () {
            $('.loadingAnim').hide();
        },
        success: function(data){
            $('.editEntryForm').show()
            var accounts = JSON.parse(data.accounts)
            var category = JSON.parse(data.category)
            var chosen_entry = JSON.parse(data.chosen_entry)
            var pk = chosen_entry[0].pk
            var amount = chosen_entry[0].fields.amount
            var entry_category = chosen_entry[0].fields.category
            var entry_date = chosen_entry[0].fields.entryDate
            var entry_note = chosen_entry[0].fields.entryNote
            var from_account = chosen_entry[0].fields.fromAccount
            var to_account = chosen_entry[0].fields.toAccount
            var type = chosen_entry[0].fields.type
            if (type == "expense") {
                $('.editEntryForm').html(`
                    <input type="hidden" class="edit_entry_pk" value="${pk}">
                    <input type="hidden" class="edit_entry_to" value="0">
                    <div class='form-group row'>
                        <label for="edit_entry_amount" class="col-4 col-form-label">Amount</label>
                        <div class="col-8">
                            <input class="form-control edit_entry_amount" value="${amount}" required>
                        </div>
                    </div>
                    <div class='form-group row'>
                        <label for="edit_entry_from" class="col-4 col-form-label">Account</label>
                        <div class="col-8">
                            <select class="form-control edit_entry_from" required></select>
                        </div>
                    </div>
                    <div class='form-group row'>
                        <label for="edit_entry_category" class="col-4 col-form-label">Category</label>
                        <div class="col-8">
                            <select class="form-control edit_entry_category" required></select>
                        </div>
                    </div>
                    <div class='form-group row'>
                        <label for="edit_entry_note" class="col-4 col-form-label">Note</label>
                        <div class="col-8">
                            <input class="form-control edit_entry_note" value="${entry_note}" required>
                        </div>
                    </div>
                    <button type="submit" class="btn btn-primary">Confirm</button>
                `)
                for (var i in accounts) {
                    var x = accounts[i].pk
                    if (x == from_account) {
                        x = lookUpAccount(x, accounts)
                        var option = $(`<option value="${accounts[i].pk}" selected>${x}</option>`)
                        $('.edit_entry_from').append(option)
                    }
                    else {
                        x = lookUpAccount(x, accounts)
                        var option = $(`<option value="${accounts[i].pk}">${x}</option>`)
                        $('.edit_entry_from').append(option)
                    }
                }
                for (var i in category) {
                    var x = category[i].pk
                    if (x == entry_category) {
                        x = lookUpCategory(x, category)
                        var option = $(`<option value="${category[i].pk}" selected>${x}</option>`)
                        $('.edit_entry_category').append(option)
                    }
                    else {
                        x = lookUpCategory(x, category)
                        var option = $(`<option value="${category[i].pk}">${x}</option>`)
                        $('.edit_entry_category').append(option)
                    }
                }
            }
            if (type == "income") {
                $('.editEntryForm').html(`
                    <input type="hidden" class="edit_entry_pk" value="${pk}">
                    <input type="hidden" class="edit_entry_from">
                    <div class='form-group row'>
                        <label for="edit_entry_amount" class="col-sm-4 col-form-label">Amount</label>
                        <div class="col-sm-8">
                            <input class="form-control edit_entry_amount" value="${amount}" required>
                        </div>
                    </div>
                    <div class='form-group row'>
                        <label for="edit_entry_to" class="col-sm-4 col-form-label">Account</label>
                        <div class="col-sm-8">
                            <select class="form-control edit_entry_to" required></select>
                        </div>
                    </div>
                    <div class='form-group row'>
                        <label for="edit_entry_category" class="col-sm-4 col-form-label">Category</label>
                        <div class="col-sm-8">
                            <select class="form-control edit_entry_category" required></select>
                        </div>
                    </div>
                    <div class='form-group row'>
                        <label for="edit_entry_note" class="col-sm-4 col-form-label">Note</label>
                        <div class="col-sm-8">
                            <input class="form-control edit_entry_note" type="text" value="${entry_note}" required>
                        </div>
                    </div>
                    <button type="submit" class="btn btn-primary">Confirm</button>
                `)
                for (var i in accounts) {
                    var x = accounts[i].pk
                    if (x == to_account) {
                        x = lookUpAccount(x, accounts)
                        var option = $(`<option value="${accounts[i].pk}" selected>${x}</option>`)
                        $('.edit_entry_to').append(option)
                    }
                    else {
                        x = lookUpAccount(x, accounts)
                        var option = $(`<option value="${accounts[i].pk}">${x}</option>`)
                        $('.edit_entry_to').append(option)
                    }
                }
                for (var i in category) {
                    var x = category[i].pk
                    if (x == entry_category) {
                        x = lookUpCategory(x, category)
                        var option = $(`<option value="${category[i].pk}" selected>${x}</option>`)
                        $('.edit_entry_category').append(option)
                    }
                    else {
                        x = lookUpCategory(x, category)
                        var option = $(`<option value="${category[i].pk}">${x}</option>`)
                        $('.edit_entry_category').append(option)
                    }
                }
            }
            if (type == "transfer") {
                $('.editEntryForm').html(`
                    <input type="hidden" class="edit_entry_pk" value="${pk}">
                    <div class='form-group row'>
                        <label for="edit_entry_amount" class="col-sm-4 col-form-label">Amount</label>
                        <div class="col-sm-8">
                            <input class="form-control edit_entry_amount" type="text" value="${amount}" required>
                        </div>
                    </div>
                    <div class='form-group row'>
                        <label for="edit_entry_from" class="col-sm-4 col-form-label">From</label>
                        <div class="col-sm-8">
                            <select class="form-control edit_entry_from" required></select>
                        </div>
                    </div>
                    <div class='form-group row'>
                        <label for="edit_entry_to" class="col-sm-4 col-form-label">To</label>
                        <div class="col-sm-8">
                            <select class="form-control edit_entry_to" required></select>
                        </div>
                    </div>
                    <div class='form-group row'>
                        <label for="edit_entry_category" class="col-sm-4 col-form-label">Category</label>
                        <div class="col-sm-8">
                            <select class="form-control edit_entry_category" required></select>
                        </div>
                    </div>
                    <div class='form-group row'>
                        <label for="edit_entry_note" class="col-sm-4 col-form-label">Note</label>
                        <div class="col-sm-8">
                            <input class="form-control edit_entry_note" value="${entry_note}" required>
                        </div>
                    </div>
                    <button type="submit" class="btn btn-primary">Confirm</button>
                `)
                for (var i in accounts) {
                    var x = accounts[i].pk
                    if (x == to_account) {
                        x = lookUpAccount(x, accounts)
                        var option = $(`<option value="${accounts[i].pk}" selected>${x}</option>`)
                        $('.edit_entry_to').append(option)
                        var option = $(`<option value="${accounts[i].pk}">${x}</option>`)
                        $('.edit_entry_from').append(option)
                    }
                    if (x == from_account) {
                        x = lookUpAccount(x, accounts)
                        var option = $(`<option value="${accounts[i].pk}" selected>${x}</option>`)
                        $('.edit_entry_from').append(option)
                        var option = $(`<option value="${accounts[i].pk}">${x}</option>`)
                        $('.edit_entry_to').append(option)
                    }
                    else {
                        x = lookUpAccount(x, accounts)
                        var option = $(`<option value="${accounts[i].pk}">${x}</option>`)
                        $('.edit_entry_to').append(option)
                        var option = $(`<option value="${accounts[i].pk}">${x}</option>`)
                        $('.edit_entry_from').append(option)
                    }
                }
                for (var i in category) {
                    var x = category[i].pk
                    if (x == entry_category) {
                        x = lookUpCategory(x, category)
                        var option = $(`<option value="${category[i].pk}" selected>${x}</option>`)
                        $('.edit_entry_category').append(option)
                    }
                    else {
                        x = lookUpCategory(x, category)
                        var option = $(`<option value="${category[i].pk}">${x}</option>`)
                        $('.edit_entry_category').append(option)
                    }
                }
            }
            if (type == "system") {
                x = lookUpAccount(to_account, accounts)
                $('.editEntryForm').html(`
                    <input type="hidden" class="edit_entry_pk" value="${pk}">
                    <input type="hidden" class="edit_entry_from" value="${from_account}">
                    <div class='form-group row'>
                        <label for="edit_entry_amount" class="col-sm-4 col-form-label">Amount</label>
                        <div class="col-sm-8">
                            <input class="form-control edit_entry_amount" type="text" value="${amount}" required>
                        </div>
                    </div>
                    <div class='form-group row'>
                        <label for="edit_entry_category" class="col-sm-4 col-form-label">Account</label>
                        <div class="col-sm-8">
                            <select class="form-control edit_entry_to" required>
                                <option selected value='${to_account}'>${x}</option>
                            </select>
                        </div>
                    </div>
                    <div class='form-group row'>
                        <label for="edit_entry_note" class="col-sm-4 col-form-label">Note</label>
                        <div class="col-sm-8">
                            <input class="form-control edit_entry_note" value="${entry_note}" required>
                        </div>
                    </div>
                    <button type="submit" class="btn btn-primary">Confirm</button>
                `)
            }
        }
    })
}

function editEntryConfirm(){
    $.ajax({
        type: 'POST',
        url: 'editEntryConfirm',
        headers: {
            'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
        },
        data: {
            'edit_entry_pk': $('.edit_entry_pk').val(),
            'edit_entry_to': $('.edit_entry_to').val(),
            'edit_entry_from': $('.edit_entry_from').val(),
            'edit_entry_note': $('.edit_entry_note').val(),
            'edit_entry_amount': $('.edit_entry_amount').val(),
            'edit_entry_category': $('.edit_entry_category').val(),
        },
        beforeSend: function () {
            $('.loadingAnim').show();
        },
        success: function(data){
            hideModal()
            var entry_change_flag = JSON.parse(data.entry_change_flag)
            if (entry_change_flag == true) {
                loadEntry()
                console.log('changes')
            } else {
                $('.loadingAnim').hide();
            }
        }
    })
}

function deleteEntry(entry_id){
    $.ajax({
        type: 'GET',
        url: 'deleteEntry',
        data: {
            'entry_id': entry_id,
        },
        beforeSend: function () {
            $('.loadingAnim').show();
        },
        success: function(data){
            hideModal()
            loadEntry()
            console.log(data)
        },
    })
}

function selectEntry(trans_id){
    $('.editEntryHiddendiv').html(`
        <input type="hidden" class="entry_id" value="${trans_id}">
    `)
}

function loadEntry(){
    filterNote = $('.filterContainer').find('.filterNote')[0].value
    filterCategory = $('.filterContainer').find('.filterCategory')[0].value
    filterAccount = $('.filterContainer').find('.filterAccount')[0].value
    filterType = $('.filterContainer').find('.filterType')[0].value
    filterDateStart = $('.filterContainer').find('.filterDateStart')[0].value
    filterDateEnd = $('.filterContainer').find('.filterDateEnd')[0].value

    $.ajax({
        type: 'GET',
        url: 'loadEntry',
        data: {
            'filterNote': filterNote,
            'filterCategory': filterCategory,
            'filterAccount': filterAccount,
            'filterType': filterType,
            'filterDateStart': filterDateStart,
            'filterDateEnd': filterDateEnd
        },
        beforeSend: function () {
            $('.loadingAnim').show();
        },
        complete: function () {
            $('.loadingAnim').hide();
        },
        success: function(data){
            var accounts = JSON.parse(data.accounts)
            var category = JSON.parse(data.category)
            var transaction = JSON.parse(data.transaction)
            var transaction_date = JSON.parse(data.transaction_date)
            var message = data.message
            console.log(accounts)
            console.log(category)
            console.log(transaction)

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
                        if (transaction[y].fields.type == 'income') {
                            var to_account_name = lookUpAccount(transaction[y].fields.toAccount, accounts)
                            var category_name = lookUpCategory(transaction[y].fields.category, category)
                            var transactionDivSubSub =
                            `<div class="transactionDivSubSub divIncome" style="display:flex; cursor:pointer;" transID="${transaction[y].pk}" data-toggle="modal" data-target=".indexModal" onclick="selectEntry(${transaction[y].pk})">
                                <div class="transLeft">
                                    <span class="transType">Income</span>:
                                    <span class="transCategory">${category_name}</span>
                                    (<span class="transAccount">${to_account_name}</span>)
                                    <span class="transNote">${transaction[y].fields.entryNote}</span>
                                </div>
                                <div class="transRight">
                                    <span class="dailyAdd">${transaction[y].fields.amount.toFixed(2)}</span>
                                </div>
                            </div>`;
                            transactionDivSub.append(transactionDivSubSub)
                        }
                        if (transaction[y].fields.type == 'expense') {
                            var from_account_name = lookUpAccount(transaction[y].fields.fromAccount, accounts)
                            var category_name = lookUpCategory(transaction[y].fields.category, category)
                            var transactionDivSubSub =
                            `<div class="transactionDivSubSub divExpense" style="display:flex; cursor:pointer;" transID="${transaction[y].pk}" data-toggle="modal" data-target=".indexModal" onclick="selectEntry(${transaction[y].pk})">
                                <div class="transLeft">
                                    <span class="transType">Expense</span>:
                                    <span class="transCategory">${category_name}</span>
                                    (<span class="transAccount">${from_account_name}</span>)
                                    <span class="transNote">${transaction[y].fields.entryNote}</span>
                                </div>
                                <div class="transRight">
                                    <span class="dailyAdd">${transaction[y].fields.amount.toFixed(2)}</span>
                                </div>
                            </div>`;
                            transactionDivSub.append(transactionDivSubSub)
                        }
                        if (transaction[y].fields.type == 'transfer') {
                            var to_account_name = lookUpAccount(transaction[y].fields.toAccount, accounts)
                            var from_account_name = lookUpAccount(transaction[y].fields.fromAccount, accounts)
                            var category_name = lookUpCategory(transaction[y].fields.category, category)
                            var transactionDivSubSub =
                            `<div class="transactionDivSubSub divTransfer" style="display:flex; cursor:pointer;" transID="${transaction[y].pk}" data-toggle="modal" data-target=".indexModal" onclick="selectEntry(${transaction[y].pk})">
                                <div class="transLeft">
                                    <span class="transType">Transfer</span>:
                                    <span class="transCategory">${category_name}</span> from
                                    (<span class="transAccount">${from_account_name}</span>) to
                                    (<span class="transAccount">${to_account_name}</span>)
                                    <span class="transNote">${transaction[y].fields.entryNote}</span>
                                </div>
                                <div class="transRight">
                                    <span class="dailyAdd">${transaction[y].fields.amount.toFixed(2)}</span>
                                </div>
                            </div>`;
                            transactionDivSub.append(transactionDivSubSub)
                        }
                        if (transaction[y].fields.type == 'system') {
                            var from_account_name = lookUpAccount(transaction[y].fields.fromAccount, accounts)
                            var transactionDivSubSub =
                            `<div class="transactionDivSubSub divSystem" style="display:flex; cursor:pointer;" transID="${transaction[y].pk}" data-toggle="modal" data-target=".indexModal" onclick="selectEntry(${transaction[y].pk})">
                                <div class="transLeft">
                                    <span class="transType">System</span>:
                                    (<span class="transAccount">${from_account_name}</span>)
                                    <span class="transNote">${transaction[y].fields.entryNote}</span>
                                </div>
                                <div class="transRight">
                                    <span class="dailyAdd">${transaction[y].fields.amount.toFixed(2)}</span>
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

// misc
function convertDate(date) {
    var month = parseInt(date.getMonth())+1
    if (month<10) {
        month = "0"+month
    }
    if (date.getDate()<10) {
        var day = "0"+date.getDate()
    } else {
        var day = date.getDate()
    }
    conv_date = date.getFullYear() +'-'+ month +'-'+ day
    // console.log(conv_date)
    return conv_date
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
                total+=parseFloat($(this)[0].children[1].children[0].innerHTML)
            }
            else {
            }
        })
        $(this).find('.dailyTotal').html("$"+total.toFixed(2))
    })
}

// modal and tab
function hideModal(){
    $('.modal').hide()
    $('.modal-backdrop').hide()
    $('.editEntryForm').hide()
    closeTab()
}

function openTab(env, tab_name){
    $('.tabContent').removeClass('selectedTab')
    $('.tabContent').hide()
    $('.tabContent').find('input').val('')
    $('.tabContent').find('select').val('')
    $('.'+tab_name).addClass('selectedTab')
    $('.'+tab_name).show()
    $(".new_entry_date").val(getTodayDate())
    if (tab_name == 'incomeForm') {
        $('.new_entry_type').val('income')
    }
    if (tab_name == 'expenseForm') {
        $('.new_entry_type').val('expense')
    }
    if (tab_name == 'transferForm') {
        $('.new_entry_type').val('transfer')
    }
}

function closeTab(){
    $('.tabContent').hide()
    $('.tabContent :input').val('')
}

function lookUpAccount(pk, account){
    for (var i in account) {
        if (account[i].pk == pk) {
            var str = account[i].fields.accountName
            return(str.charAt(0).toUpperCase()+str.slice(1))
        }
    }
}

function lookUpCategory(pk, category){
    for (var i in category) {
        if (category[i].pk == pk) {
            var str = category[i].fields.categoryName
            return(str.charAt(0).toUpperCase()+str.slice(1))
        }
    }
}