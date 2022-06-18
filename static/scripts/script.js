$(document).ready(function(){
	$('.pwd-eye').click(function(){
        $(this).hide();
        $(this).siblings().show();
        if ($(this).data('state') == 1) {
            $('input[name="password"]').attr('type', 'text');
        } else {
            $('input[name="password"]').attr('type', 'password');
        }
    });

    $('#artSaleType').change(function(){
        let val = $(this).val()
        if (val == 1) {
            $('#spot-sale').hide()
            $('#auction').show()
            $('#artEndDate').attr('min', new Date().toLocaleDateString('en-ca'))
        } else if(val == 2) {
            $('#auction').hide()
            $('#spot-sale').show()
        } else {
            $('#auction').hide()
            $('#spot-sale').hide()
        }
    });
});
