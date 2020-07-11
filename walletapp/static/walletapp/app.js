$(document).ready(function (){
    // console.log("loaded")
    // console.log($('.dailyTotal')[0])
    // console.log($('.dailyAdd')[0])

    getTransTotal() //calculate daily total

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

    $('.accountDiv').click(function(){
        $.ajax({
            type: 'GET',
            url: 'overviewAjax',
            data: {
                "selected_account": $(this).attr('id')
            },
            success: function(data) {
                console.log(data);
                $('#totalIncome').text("$ "+data.total_income)
                $('#totalExpense').text("$ "+data.total_expense)
                $('#totalChange').text("$ "+data.total_change)
                $('#totalTransfer').text("$ "+data.total_transfer)
            }
        })
    })
})





function getTransTotal(){ //sum up total for the day
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
