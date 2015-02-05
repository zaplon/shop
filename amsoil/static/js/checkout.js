function handlers(){
    $('.container-fluid input[type!="checkbox"]').addClass('form-control');

    //$('.row').css('display','none');
    //$('.row:first').css('display','block');
    var step = $('#checkout-variables input[name="step"]').val();
    if (!isNaN(step))
        checkout.forwardToStep(step);
    else {
        $('.checkout-step').css('display','none');
        $('.checkout-step:first').css('display','block');
    }

    $('.checkout-forward').click(function(){
        checkout.forward(this);
    });
    $('.checkout-back').click(function(){
        $('.checkout-step').css('display','none');
        var step = parseInt($(this).parent().parent().parent().attr('step')) - 1;
        $('div.checkout-step[step="'+step+'"]').css('display','block');
        $('.progress-bar').animate({width:checkout.calcWidth(step)+'%'});
    });
    $('#checkout-process').click(function(){
        checkout.process();
    });

    checkout.getOrderOptions();

    $('#checkout-order').delegate('input[type="radio"]','change',function(){
        console.log('refresh');
        checkout.getOrderOptions();
    });
    $('input[name="invoice"]').click(function(t){
        if ($(this).is(':checked'))
            $('form#invoice-form').css('display','block');
        else
            $('form#invoice-form').css('display','none');
    });
    
    $('#checkout-control div').click(function(){
       if ($(this).attr('step'))
        checkout.forwardToStep($(this).attr('step'));
    });

}


$(document).ready(function(){
    handlers();
});

checkout = {
    forward: function(el){
        $('.checkout-step').css('display','none');
        var step = parseInt($(el).parent().parent().parent().attr('step')) + 1;
        $('div.checkout-step[step="'+step+'"]').css('display','block');
        $('.progress-bar').animate({width:checkout.calcWidth(step)+'%'});
    },
    forwardToStep: function(step){
        $('.checkout-step').css('display','none');
        $('div.checkout-step[step="'+step+'"]').css('display','block');
        $('.progress-bar').animate({width:checkout.calcWidth(step)+'%'});
    },
    getOrderOptions: function(){
      if ($("input[name='shippingMethod']:checked").length > 0)
        var shipping = $("input[name='shippingMethod']:checked").val();
      else
        var shipping = -1;
      if ($("input[name='paymentMethod']:checked").length > 0)
        var payment = $("input[name='paymentMethod']:checked").val();
      else
        var payment = -1;

      if (shipping == -1)
        var shipping = $('#checkout-variables input[name="shippingMethod"]').val();

      $.ajax({
        url: '/getOrderOptions',
        data: {'shipping':shipping, 'payment':payment},
        success: function(res){
            res = JSON.parse(res);
            $('#checkout-order').html(Mustache.to_html(Mustache.TEMPLATES.checkoutOrder, res ));
            $("input[name='shippingMethod'][value='"+shipping+"']").attr('checked', 'true');
            $("input[name='paymentMethod'][value='"+payment+"']").attr('checked', 'true');

            //ukrywanie zbędnych formularzy
            $('.checkout-extra').css('display','none');
            $("div[for-shipping='"+shipping+"']").css('display','initial');
            $("div[for-shipping='"+payment+"']").css('display','initial');

            if (res.needsShipping)
                $('#shipping-forms').css('display','block');
            else
                $('#shipping-forms').css('display','none');
        }
      });
    },
    getFormData: function(form){
      var res = {};
      var data = form.serializeArray();
      data.forEach(function(d){
          res[d.name] = d.value;
      });
      return res;
    },
    process: function(){
      console.log('process');
      data = {};
      if ($('form#buyer-address').length > 0)
        data.buyer = this.getFormData($('form#buyer-address'));
      if ($('form#receiver-address:visible').length > 0)
        data.receiver = this.getFormData($('form#receiver-address'));
      data.shippingMethod = $("input[name='shippingMethod']:checked").val();
      data.paymentMethod = $("input[name='paymentMethod']:checked").val();
      data.terms = $('input[name="terms"]').is(':checked');
      if (!data.shippingMethod) {
          $('#no-terms').css('display', 'block');
      }
      if (!data.shippingMethod) {
          $('#no-shipping').css('display', 'block');
      }
      if (!data.paymentMethod) {
          $('#no-payment').css('display', 'block');
      }

      if (!data.paymentMethod || !data.shippingMethod )
        return;

      data.hasInvoice = $('input[name="invoice"]').is(':checked');
      data.invoice = this.getFormData($('form#invoice-form'));
      data.notes = $('#notes').val();
      data.checkoutBasic = this.getFormData($('form#basic'));

        $.ajax({
            method: 'POST',
            url: '/checkout/',
            data: { 'data':JSON.stringify(data)},
            success: function(res){
                if (res[0] == '{'){
                    res = JSON.parse(res);
                    checkout.forward(document.getElementById('checkout-process'));
                    $('#confirmation').html(res.message);
                }
                else{
                    $('body').html(res);
                    handlers();
                }
            }
        });
    },
    steps: 4,
    calcWidth: function(step){
      if (step == 1)
        return checkout.offset
      else
        return 100/(checkout.steps)*(step-1) + checkout.offset;
    },
    offset: 12.5
};
