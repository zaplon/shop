$(document).ready(function($){

    //footer zawsze na dole strony
//    var minh = $(document).height() - $('footer').height() - $('#top').height() - $('header').height();
//    if ($('.container-fluid').height() < minh)
//        $('.container-fluid').height(minh);
    $('[data-toggle="tooltip"]').tooltip();

    $('#logo').click(function(){
       window.location = '/';
    });

    $('.show-on-click').click(function(){
        if ($(this).is(':checked'))
            $('#'+$(this).attr('data-hide')).css('display','none');
        else
            $('#'+$(this).attr('data-hide')).css('display','block');
    })

    $('.container-fluid').delegate('.variations-table select','change', function(){
    	var div = $('.variations-table[data-product='+$(this).attr('data-product')+']');
    	var selectedVariation = shop.getSelectedVariation(div);
        var dtls = $('.variations-details[data-product='+$(this).attr('data-product')+']');
     	$(dtls).find('.variation-details').css('display','none');
        $(dtls).find('.price-from').css('display','none');
     	$(dtls).find('.variation-details[data-variation='+selectedVariation+']').css('display','block');
    });


    $('.container-fluid').delegate('.add-to-cart', 'click', function(){
       var id = $(this).attr('data-variation');
       var isVariable = $(this).hasClass('variable');
       var hasSingleVariation = $(this).hasClass('single-var');
       if (isVariable && !hasSingleVariation) {
           var id = shop.getSelectedVariation($('.variations-table[data-product=' + $(this).attr('data-product') + ']'));
       }
       if (hasSingleVariation)
        id = $(this).attr('data-product');
       //var singleVar =  $(this).hasClass('single-var');
       //if (isVariable && !singleVar)
       // id = $('select["data-product='+id + '"]').val();
      shop.addToCart(id,isVariable);
    });

    $('#account #login').click(function(){
        shop.showWindow(tr('Log in'), Mustache.render(Mustache.TEMPLATES['loginForm']) );
        $('#doLogin').click(function(){
            $.post('/login/', $('#login-form').serialize(), function(res){
                res = JSON.parse(res);
                if (res.success)
                    window.location.reload();
                else {
                    $('.login-error').css('display','block');
                    $('.login-error').html(res.message);
                }
            });
        });
    });

     $('#account #register').click(function(){
        window.location = '/register'
     });

    $('header').delegate('#checkout','click',function(){
        window.location = '/checkout';
    });

    $('header').delegate('#cart','click',function(){
        window.location = '/cart';
    });

    $('#product-categories .thick-box').click(function(){
       if ($(this).hasClass('filter-active')){
           $(this).removeClass('filter-active');
           $(this).removeClass('glyphicon glyphicon-ok');
           delete(shop.filters.categories[$(this).attr('category')]);
       }
       else {
           $(this).addClass('filter-active');
           $(this).addClass('glyphicon glyphicon-ok');
           shop.filters.categories[$(this).attr('category')] = true;
       }
    });



    shop.decorate();

    $('.container-fluid').css('minHeight',($(window).height()-$('#top').height()-$('nav').height()-
        $('header').height() - $('footer').height()-40)+'px');

    //logowanie i rejestracja
    $('.do-login').click(function(){
        $.post('/login/', $('#login-form').serialize(),function(res){
            res = JSON.parse(res);
            if (res.success == false){
                $('.login-error').css('display','block');
                $('.login-error').html(res.message);
            } else
                window.location.reload();
        })
    });

});

shop = {
    currentPage: 1,
    displayAs: 'grid',
    quantity: 1,
    drawElipse: function drawEllipse(context,centerX, centerY, width, height) {

      context.beginPath();
      context.moveTo(centerX - width/2, centerY); // A1

      context.bezierCurveTo(
      centerX - width/2, centerY + height/2, // C1
      centerX + width/2, centerY + height/2, // C2
      centerX + width/2, centerY); // A2

      context.fillStyle = "#999999";
      context.fill();
      context.closePath();
    },
    decorate: function(){
      divs = $('.product-dec canvas, canvas.dec');
      divs.each(function(i,c){
          var w = $(c).parent().parent().width();
          var h = $(c).height();
          c.width = w;
          var context = c.getContext("2d");
          context.shadowOffsetX = 0;
          context.shadowOffsetY = 0;
          context.shadowBlur = 10;
          context.shadowColor = "#222222";
          shop.drawElipse(context,w/2, 0, w-10, h-5);
      });
    },
    showTopMessage: function(message){
        $('#top-message').html(message);
        $('#top-message').animate({padding:'15px',borderWidth:'2px'},200);
        window.setTimeout(function(){
            $('#top-message').animate({padding:'0px',borderWidth:'0px'},200);
            $('#top-message').html('');
        },2000);
    },
    showWindow: function(title,body,footer,buttons){

        $('.modal-dialog').remove();

        var id = new Date().getTime();
        var w = '<div class="modal-dialog" id="'+id+'">';
        w = w + '<div class="modal-content">';
        w = w + '<div class="modal-header">';
        w = w + '<button type="button" class="close" data-dismiss="modal"><span aria-hidden="true">&times;</span><span class="sr-only">Close</span></button>';
        w = w + '<h4>' + title + '</h4></div>';
        w = w + '<div class="modal-body">' + body + '</div>';
        w = w + '</div></div>';
        var b = $('body');
        b.append(w);
        var d = $('#'+id);
        d.css('top', parseInt($(window).height()/2 - d.height()/2)+'px');
        d.css('left', parseInt($(window).width()/2 - d.width()/2 )+'px');
        $('#'+id + ' .close').click(function(){
           $(this).parent().parent().remove();
        });
        //d.draggable();
    },
    login: function(){
    },
    register: function(){

    },
    addToCart: function(id, variable){
        var data = variable ? { 'productVariation': id } : { 'product': id};
        data.quantity = shop.quantity;
        $.ajax({
            url: '/addToCart/',
            method: 'POST',
            data: data,
            success: function (res) {
                $.get('/miniCart',{},function(res){
                    $('#mini-cart').html(Mustache.to_html(Mustache.TEMPLATES.miniCart,
                        JSON.parse(res)));
                    shop.showTopMessage(tr('Product added to cart'));
                });
            }
        });
    },
    filters: {
        categories: {}
    },
    getSelectedVariation: function(div){
        
    	var selects = $(div).find('select');
        var variations = [];
        selects.each(function(ind,el){
    	    var opt = $(el).find(':selected');
                variations.push($(opt).attr('data-variations').split(','));
        });
        var cands = variations[0];
        if (cands.length > 1)
            variations.forEach(function(v){
                cands.forEach(function(c,ind){
                    if (v.indexOf(c) == -1)
                        cands.remove(c);
                });
            });

        return cands[0];

    },
    getProducts: function(container){
        var filters = '';
        var cats = [];
        var page = 1;
        for (f in this.filters.categories)
            cats.push(f);
        cats = cats.join(',');
        filters = filters + 'page=' + shop.currentPage + '&';
        filters = filters + 'categories_in=' + cats;
        $.get('/products?' + filters).done(function(res){
           var cont = $('#'+container)[0];
           $('.product').remove();

          //numeracja stron
          var pagination = $('#shop-pagination');
          pagination.children().remove();
          if (shop.currentPage == 1) {}
           // pagination.append('<li data-page='+(shop.currentPage-1)+' class="disabled"><a href="#"><span aria-hidden="true">&laquo;</span><span class="sr-only">Previous</span></a></li>');
          else
            pagination.append('<li data-page='+(shop.currentPage-1)+' class="enabled"><a href="#"><span aria-hidden="true">&laquo;</span><span class="sr-only">Previous</span></a></li>');
          for(var i=0;i<res.count/10;i++)
            pagination.append('<li data-page='+(i+1)+' class="enabled"><a href="#">'+(i+1)+' <span class="sr-only">(current)</span></a></li>');
          if (shop.currentPage == i) {}
          //  pagination.append('<li data-page='+(shop.currentPage+1)+' class="disabled"><a href="#"><span aria-hidden="true">&raquo;</span><span class="sr-only">Previous</span></a></li>');
          else
            pagination.append('<li data-page='+(shop.currentPage+1)+' class="enabled"><a href="#"><span aria-hidden="true">&raquo;</span><span class="sr-only">Previous</span></a></li>');
          var aPage = $('li[data-page="'+shop.currentPage+ '"]');//pagination.children()[shop.currentPage];
          //$(aPage).removeClass('disabled');
          $('#shop-pagination li').click(function(){
             shop.currentPage = parseInt($(this).attr('data-page'));
             shop.getProducts('products');
          });

          $(aPage).addClass('active');
           for (r in res.results) {
               if ((r) % 3 == 0)
                $(cont).append('<div style="clear:both"></div>');
               var div = document.createElement('div');
               if (shop.displayAs == 'grid')
                div.className = 'product product-grid col-md-4 col-sm-12';
               else
                div.className = 'product product-list col-md-12 col-sm-12';
               cont.appendChild(div);

               if (res.results[r].variations.length == 0)
                res.results[r].noVars = true;
               else
                res.results[r].noVars = false;

               if (shop.displayAs == 'grid') {
                   $(div).html(Handlebars.templates['productSmall']( {'addToCart': 'Do koszyka', 'product': res.results[r] }));
                   //$(div).html(Mustache.to_html(Mustache.TEMPLATES.productSmall, {'addToCart': 'Do koszyka', 'product': res.results[r] }));
               }
               else
                $(div).html(Handlebars.templates['product']( {'addToCart': 'Do koszyka', 'product': res.results[r] }));
                //$(div).html(Mustache.to_html(Mustache.TEMPLATES.product, { 'addToCart':'Do koszyka', 'product': res.results[r] }));
           }
           shop.decorate();
        });;
    }
}


// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});


function tr(str){
    return str;
}
