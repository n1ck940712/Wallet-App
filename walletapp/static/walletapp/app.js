$(document).ready(function (){
    // console.log("loaded")
    // console.log($('.dailyTotal')[0])
    // console.log($('.dailyAdd')[0])
    getTransTotal()
})

$('#addEntryButton').on('click', function(){
    var today = new Date()
    var dd = today.getDate();
    var mm = today.getMonth()+1;
    var yy = today.getFullYear();
    if (mm<10) {
        mm = '0'+mm;
    }
    if (dd<10) {
        dd = '0'+dd;
    }
    var test = (yy + '-' + mm + '-' + dd)
    $(".new_entry_date").val(test)
})

$('#filterNote').on('keyup', function(){
    filter = $(this).val().toLowerCase()
    $('.transactionDivSubSub').find(".transNote").each(function(){
        text = $(this).text().toLowerCase()
        if (text.indexOf(filter)!=-1) {
            $(this).parent('div').parent('div').show()
        }
        else {
            $(this).parent('div').parent('div').hide()
        }
    })
    getTransTotal()

})

$('#filterCategory').change(function(){
    filter = $(this).val()
    $('.transactionDivSubSub').find(".transCategory").each(function(){
        // var elementNum = $(this).parent().parent().parent()[0].childElementCount
        if ($(this).text().indexOf(filter)!=-1) {
            $(this).parent('div').parent('div').show()
        }
        else {
            $(this).parent('div').parent('div').hide()
        }
    })
    getTransTotal()
})

function getTransTotal(){
    $('.transactionDivSub').each(function(){
        var total=0;
        $(this).find(".transactionDivSubSub").each(function(){
            if ($(this).is(':visible')) {
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
