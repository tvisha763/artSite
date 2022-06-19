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

    $('#like-btn').click(function(){
        const state = $(this).data('state');
        const url = $(this).data('url');
        const art_id = $(this).data('art');
        if (state == "0") {
            $('#like').hide()
            $('#unlike').show()
            $(this).data('state', "1");
            $.ajax({
                type: "POST",
                url: url,
                data: {'action': 1, 'art_id': art_id},
                success: function(response){
                    $('#like-number').html(response.no_of_likes)
                }
            });

        } else {
            $('#like').show()
            $('#unlike').hide()
            $(this).data('state', "0");
            $.ajax({
                type: "POST",
                url: url,
                data: {'action': 0, 'art_id': art_id},
                success: function(response){
                    $('#like-number').html(response.no_of_likes)
                }
            });
        }
    });
});
