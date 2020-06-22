$(document).on('load', function (){

})

function functionA(from_account, ent_date, ent_time){
    $('.inviForm').html(`
        <input type="hidden" name="del_entry_from" value="${from_account}">
        <input type="hidden" name="del_entry_date" value="${ent_date}">
        <input type="hidden" name="del_entry_time" value="${ent_time}">
    `)
    console.log(from_account)
    console.log(ent_date)
    console.log(ent_time)
}
